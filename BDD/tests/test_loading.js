const { PrismaClient } = require('@prisma/client');
const fs = require('fs');
const { parse } = require('csv-parse/sync');
const path = require('path');
const { 
  safeParseFloat, 
  safeParseBigInt, 
  safeParseDate, 
  validateString, 
  DEFAULT_CONFIG 
} = require('../src/utils/dataUtils');

const prisma = new PrismaClient();

async function testDataParsing() {
  console.log(' Test de parsing des données...\n');
  
  const ETL_PROCESSED_DIR = path.join(__dirname, DEFAULT_CONFIG.ETL_PROCESSED_DIR);
  
  // Test 1: Parsing des pays
  console.log('1. Test parsing des pays:');
  const countryFile = path.join(ETL_PROCESSED_DIR, 'dim_country.csv');
  
  if (fs.existsSync(countryFile)) {
    const data = fs.readFileSync(countryFile, 'utf-8');
    const records = parse(data, { columns: true, delimiter: ',' });
    
    // Tester les 5 premiers enregistrements
    for (let i = 0; i < Math.min(5, records.length); i++) {
      const record = records[i];
      console.log(`   Enregistrement ${i + 1}:`);
      console.log(`     - Country: "${record.country}"`);
      console.log(`     - ISO: "${record.iso_code}"`);
      console.log(`     - Population brute: "${record.population}"`);
      
      // Test des conversions
      const countryName = validateString(record.country, 100, 'country');
      const isoCode = validateString(record.iso_code, 3, 'iso_code');
      const population = safeParseBigInt(record.population);
      
      console.log(`     - Country validé: "${countryName}"`);
      console.log(`     - ISO validé: "${isoCode}"`);
      console.log(`     - Population convertie: ${population}`);
      console.log('');
    }
  }
  
  // Test 2: Parsing des faits (COVID)
  console.log('2. Test parsing des faits COVID:');
  const covidFile = path.join(ETL_PROCESSED_DIR, 'fact_covid_history.csv');
  
  if (fs.existsSync(covidFile)) {
    const data = fs.readFileSync(covidFile, 'utf-8');
    const records = parse(data, { columns: true, delimiter: ',' });
    
    // Tester les 3 premiers enregistrements
    for (let i = 0; i < Math.min(3, records.length); i++) {
      const record = records[i];
      console.log(`   Enregistrement ${i + 1}:`);
      console.log(`     - Date brute: "${record.date}"`);
      console.log(`     - Country: "${record.country}"`);
      console.log(`     - Value brute: "${record.value}"`);
      console.log(`     - Population brute: "${record.population}"`);
      
      // Test des conversions
      const date = safeParseDate(record.date);
      const country = validateString(record.country, 200, 'country');
      const value = safeParseFloat(record.value);
      const population = safeParseBigInt(record.population);
      
      console.log(`     - Date convertie: ${date}`);
      console.log(`     - Country validé: "${country}"`);
      console.log(`     - Value convertie: ${value}`);
      console.log(`     - Population convertie: ${population}`);
      console.log('');
    }
  }
  
  // Test 3: Détection des problèmes potentiels
  console.log('3. Détection des problèmes potentiels:');
  
  if (fs.existsSync(covidFile)) {
    const data = fs.readFileSync(covidFile, 'utf-8');
    const records = parse(data, { columns: true, delimiter: ',' });
    
    let bigIntErrors = 0;
    let floatErrors = 0;
    let dateErrors = 0;
    let stringErrors = 0;
    
    // Analyser les 100 premiers enregistrements
    for (let i = 0; i < Math.min(100, records.length); i++) {
      const record = records[i];
      
      try {
        safeParseBigInt(record.population);
      } catch (error) {
        bigIntErrors++;
      }
      
      try {
        safeParseFloat(record.value);
      } catch (error) {
        floatErrors++;
      }
      
      try {
        safeParseDate(record.date);
      } catch (error) {
        dateErrors++;
      }
      
      try {
        validateString(record.country, 200, 'country');
      } catch (error) {
        stringErrors++;
      }
    }
    
    console.log(`   - Erreurs BigInt: ${bigIntErrors}`);
    console.log(`   - Erreurs Float: ${floatErrors}`);
    console.log(`   - Erreurs Date: ${dateErrors}`);
    console.log(`   - Erreurs String: ${stringErrors}`);
  }
}

async function testDatabaseConnection() {
  console.log('\n🔌 Test de connexion à la base de données...');
  
  try {
    // Test de connexion simple
    await prisma.$connect();
    console.log(' Connexion à la base de données réussie');
    
    // Test de requête simple
    const countryCount = await prisma.pays.count();
    console.log(` Nombre de pays dans la base: ${countryCount}`);
    
  } catch (error) {
    console.error(' Erreur de connexion:', error.message);
  }
}

async function main() {
  console.log(' TESTS DE VALIDATION DU CHARGEMENT');
  console.log('=' * 50);
  
  await testDataParsing();
  await testDatabaseConnection();
  
  console.log('\n Tests terminés');
}

main()
  .catch((e) => {
    console.error(' Erreur fatale:', e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  }); 