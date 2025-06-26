const { PrismaClient } = require('@prisma/client');
const fs = require('fs');
const { parse } = require('csv-parse/sync');
const path = require('path');
const { 
  safeParseInt, 
  safeParseFloat, 
  safeParseBigInt, 
  safeParseDate, 
  validateString, 
  DEFAULT_CONFIG 
} = require('../utils/dataUtils');

const prisma = new PrismaClient();

// Configuration
const BATCH_SIZE = DEFAULT_CONFIG.BATCH_SIZE;
const ETL_PROCESSED_DIR = path.resolve(__dirname, '../../../ETL/processed');

// Statistiques globales
const stats = {
  countries: { loaded: 0, skipped: 0, errors: 0 },
  indicators: { loaded: 0, skipped: 0, errors: 0 },
  facts: { loaded: 0, skipped: 0, errors: 0 }
};

async function loadCountries() {
  console.log('Chargement des pays...');
  const filePath = path.join(ETL_PROCESSED_DIR, 'dim_country.csv');
  
  if (!fs.existsSync(filePath)) {
    console.error(`Fichier introuvable: ${filePath}`);
    return;
  }
  
  try {
  const data = fs.readFileSync(filePath, 'utf-8');
  const records = parse(data, { columns: true, delimiter: ',' });
    
  for (const record of records) {
      try {
        // Validation du code ISO
    if (!record.iso_code || record.iso_code.length !== 3) {
          console.log(`Ignoré: '${record.country}' (iso_code: '${record.iso_code}')`);
          stats.countries.skipped++;
          continue;
        }
        
        // Validation et nettoyage des données
        const countryName = validateString(record.country, 100, 'country');
        const isoCode = validateString(record.iso_code, 3, 'iso_code');
        const population = safeParseBigInt(record.population);
        
        if (!countryName || !isoCode) {
          console.log(`Données invalides pour: ${record.country}`);
          stats.countries.skipped++;
      continue;
    }
        
    await prisma.pays.upsert({
          where: { iso_code: isoCode },
          update: {
            country: countryName,
            population: population,
          },
      create: {
            country: countryName,
            population: population,
            iso_code: isoCode,
      },
    });
        
        stats.countries.loaded++;
        if (stats.countries.loaded % 50 === 0) {
          console.log(`${stats.countries.loaded} pays chargés...`);
        }
        
      } catch (error) {
        console.error(`Erreur pour ${record.country}:`, error.message);
        stats.countries.errors++;
      }
    }
    
    console.log(`Pays chargés: ${stats.countries.loaded} | Ignorés: ${stats.countries.skipped} | Erreurs: ${stats.countries.errors}`);
    
  } catch (error) {
    console.error('Erreur lors du chargement des pays:', error);
  }
}

async function loadIndicators() {
  console.log('Chargement des indicateurs...');
  const filePath = path.join(ETL_PROCESSED_DIR, 'dim_indicator.csv');
  
  if (!fs.existsSync(filePath)) {
    console.error(`Fichier introuvable: ${filePath}`);
    return;
  }
  
  try {
  const data = fs.readFileSync(filePath, 'utf-8');
  const records = parse(data, { columns: true, delimiter: ',' });
    
  for (const record of records) {
      try {
        const indicatorName = validateString(record.indicator_name, 50, 'indicator_name');
        const description = validateString(record.description, 255, 'description');
        
        if (!indicatorName) {
          console.log(`Nom d'indicateur invalide: ${record.indicator_name}`);
          stats.indicators.skipped++;
          continue;
        }
        
    await prisma.indicateur.upsert({
          where: { indicator_name: indicatorName },
          update: {
            description: description,
          },
      create: {
            indicator_name: indicatorName,
            description: description,
      },
    });
        
        stats.indicators.loaded++;
        
      } catch (error) {
        console.error(`Erreur pour ${record.indicator_name}:`, error.message);
        stats.indicators.errors++;
      }
    }
    
    console.log(`Indicateurs chargés: ${stats.indicators.loaded} | Erreurs: ${stats.indicators.errors}`);
    
  } catch (error) {
    console.error('Erreur lors du chargement des indicateurs:', error);
  }
}

async function loadFacts(fileName) {
  console.log(`Chargement des faits: ${fileName}...`);
  const filePath = path.join(ETL_PROCESSED_DIR, fileName);
  
  if (!fs.existsSync(filePath)) {
    console.error(`Fichier introuvable: ${filePath}`);
    return;
  }
  
  try {
  const data = fs.readFileSync(filePath, 'utf-8');
  const records = parse(data, { columns: true, delimiter: ',' });
    
    // Traitement par lots pour les performances
    const batches = [];
    for (let i = 0; i < records.length; i += BATCH_SIZE) {
      batches.push(records.slice(i, i + BATCH_SIZE));
    }
    
    for (let batchIndex = 0; batchIndex < batches.length; batchIndex++) {
      const batch = batches[batchIndex];
      const batchData = [];
      
      for (const record of batch) {
        try {
          // Validation des données obligatoires
          if (!record.date || !record.country || !record.iso_code || record.iso_code.length !== 3) {
            stats.facts.skipped++;
            continue;
          }
          
          // Validation et nettoyage des données
          const date = safeParseDate(record.date);
          const country = validateString(record.country, 200, 'country');
          const indicator = validateString(record.indicator, 200, 'indicator');
          const source = validateString(record.source, 200, 'source');
          const isoCode = validateString(record.iso_code, 3, 'iso_code');
          const unit = validateString(record.unit, 200, 'unit');
          
          // Conversion des valeurs numériques
          const value = safeParseFloat(record.value);
          const population = safeParseBigInt(record.population);
          const casesPer100k = safeParseFloat(record.cases_per_100k);
          const deathsPer100k = safeParseFloat(record.deaths_per_100k);
          const incidence7j = safeParseFloat(record.incidence_7j);
          const growthRate = safeParseFloat(record.growth_rate);
          
          // Validation finale
          if (!date || !country || !indicator || !isoCode) {
            stats.facts.skipped++;
            continue;
          }
          
          batchData.push({
            date: date,
            country: country,
            value: value,
            indicator: indicator,
            source: source,
            iso_code: isoCode,
            population: population,
            unit: unit,
            cases_per_100k: casesPer100k,
            deaths_per_100k: deathsPer100k,
            incidence_7j: incidence7j,
            growth_rate: growthRate,
          });
          
        } catch (error) {
          console.error(`Erreur parsing record:`, error.message);
          stats.facts.errors++;
        }
      }
      
      // Insertion du lot
      if (batchData.length > 0) {
        try {
          await prisma.donneeHistorique.createMany({
            data: batchData,
            skipDuplicates: true, // Évite les doublons
          });
          
          stats.facts.loaded += batchData.length;
          
          if (batchIndex % 10 === 0) {
            console.log(`${stats.facts.loaded} faits chargés... (lot ${batchIndex + 1}/${batches.length})`);
          }
          
        } catch (error) {
          console.error(`Erreur insertion lot ${batchIndex + 1}:`, error.message);
          stats.facts.errors += batchData.length;
        }
      }
    }
    
    console.log(`${fileName}: ${stats.facts.loaded} faits chargés | Ignorés: ${stats.facts.skipped} | Erreurs: ${stats.facts.errors}`);
    
  } catch (error) {
    console.error(`Erreur lors du chargement de ${fileName}:`, error);
  }
}

async function generateStats() {
  console.log('\n Statistiques de la base de données:');
  
  try {
    const countryCount = await prisma.pays.count();
    const indicatorCount = await prisma.indicateur.count();
    const factCount = await prisma.donneeHistorique.count();
    
    console.log(`Pays: ${countryCount}`);
    console.log(`Indicateurs: ${indicatorCount}`);
    console.log(`Données historiques: ${factCount.toLocaleString()}`);
    
    // Statistiques par source
    const sources = await prisma.donneeHistorique.groupBy({
      by: ['source'],
      _count: { source: true }
    });
    
    console.log('\n Répartition par source:');
    sources.forEach(source => {
      console.log(`   ${source.source}: ${source._count.source.toLocaleString()} enregistrements`);
    });
    
  } catch (error) {
    console.error('Erreur lors de la génération des statistiques:', error);
  }
}

async function main() {
  console.log('Début du chargement de la base de données...');
  console.log(`Répertoire ETL: ${ETL_PROCESSED_DIR}`);
  
  const startTime = Date.now();
  
  try {
  await loadCountries();
  await loadIndicators();
  await loadFacts('fact_covid_history.csv');
  await loadFacts('fact_mpox_history.csv');
    
    const endTime = Date.now();
    const duration = (endTime - startTime) / 1000;
    
    console.log('\n Chargement complet terminé!');
    console.log(`Durée totale: ${duration.toFixed(2)} secondes`);
    
    await generateStats();
    
  } catch (error) {
    console.error('Erreur critique lors du chargement:', error);
    process.exit(1);
  }
}

main()
  .catch((e) => {
    console.error('Erreur fatale:', e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
    console.log('Connexion à la base de données fermée.');
  }); 