const { PrismaClient } = require('@prisma/client');
const fs = require('fs');
const { parse } = require('csv-parse/sync');
const path = require('path');

const prisma = new PrismaClient();

async function loadCountries() {
  const filePath = path.join(__dirname, '../ETL/processed/dim_country.csv');
  const data = fs.readFileSync(filePath, 'utf-8');
  const records = parse(data, { columns: true, delimiter: ',' });
  let count = 0;
  for (const record of records) {
    if (!record.iso_code || record.iso_code.length !== 3) {
      console.log(`Ignoré: '${record.country}' (iso_code: '${record.iso_code}')`);
      continue;
    }
    console.log(`Insertion: '${record.country}' (longueur: ${record.country.length})`);
    await prisma.pays.upsert({
      where: { iso_code: record.iso_code },
      update: {},
      create: {
        country: record.country,
        population: record.population ? parseInt(record.population) : null,
        iso_code: record.iso_code,
      },
    });
    count++;
  }
  console.log(`Pays chargés : ${count}`);
}

async function loadIndicators() {
  const filePath = path.join(__dirname, '../ETL/processed/dim_indicator.csv');
  const data = fs.readFileSync(filePath, 'utf-8');
  const records = parse(data, { columns: true, delimiter: ',' });
  let count = 0;
  for (const record of records) {
    await prisma.indicateur.upsert({
      where: { indicator_name: record.indicator_name },
      update: {},
      create: {
        indicator_name: record.indicator_name,
        description: record.description || null,
      },
    });
    count++;
  }
  console.log(`Indicateurs chargés : ${count}`);
}

async function loadFacts(fileName) {
  const filePath = path.join(__dirname, '../ETL/processed/', fileName);
  const data = fs.readFileSync(filePath, 'utf-8');
  const records = parse(data, { columns: true, delimiter: ',' });
  let count = 0;
  for (const record of records) {
    if (!record.date || !record.country) continue;
    if (!record.iso_code || record.iso_code.length !== 3) continue;
    // Log des longueurs pour debug
    const debugInfo = {
      country: record.country,
      countryLen: record.country ? record.country.length : 0,
      indicator: record.indicator,
      indicatorLen: record.indicator ? record.indicator.length : 0,
      source: record.source,
      sourceLen: record.source ? record.source.length : 0,
      unit: record.unit,
      unitLen: record.unit ? record.unit.length : 0,
    };
    if (
      debugInfo.countryLen > 200 ||
      debugInfo.indicatorLen > 200 ||
      debugInfo.sourceLen > 200 ||
      debugInfo.unitLen > 200
    ) {
      console.log('Record trop long:', debugInfo, record);
    }
    // Log complet juste avant insertion
    console.log('Insertion DonneeHistorique:', record);
    await prisma.donneeHistorique.create({
      data: {
        date: new Date(record.date),
        country: record.country,
        value: record.value ? parseFloat(record.value) : null,
        indicator: record.indicator,
        source: record.source || null,
        iso_code: record.iso_code || null,
        population: record.population ? parseInt(record.population) : null,
        unit: record.unit || null,
        cases_per_100k: record.cases_per_100k ? parseFloat(record.cases_per_100k) : null,
        deaths_per_100k: record.deaths_per_100k ? parseFloat(record.deaths_per_100k) : null,
        incidence_7j: record.incidence_7j ? parseFloat(record.incidence_7j) : null,
        growth_rate: record.growth_rate ? parseFloat(record.growth_rate) : null,
      },
    });
    count++;
  }
  console.log(`${fileName} : ${count} faits chargés.`);
}

// TODO: Ajouter les fonctions pour pandemie, source_donnee, et donnee_historique

async function main() {
  await loadCountries();
  await loadIndicators();
  await loadFacts('fact_covid_history.csv');
  await loadFacts('fact_mpox_history.csv');
  // await loadPandemics();
  // await loadSources();
  // await loadHistoricalData();
  console.log('Chargement complet terminé.');
}

main()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  }); 