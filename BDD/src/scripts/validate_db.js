const { PrismaClient } = require('@prisma/client');

const prisma = new PrismaClient();

async function validateDatabaseIntegrity() {
  console.log('Validation de l\'intégrité de la base de données...\n');
  
  try {
    // 1. Vérification des tables
    console.log('Vérification des tables:');
    const countryCount = await prisma.pays.count();
    const indicatorCount = await prisma.indicateur.count();
    const factCount = await prisma.donneeHistorique.count();
    
    console.log(`Table pays: ${countryCount} enregistrements`);
    console.log(`Table indicateur: ${indicatorCount} enregistrements`);
    console.log(`Table donnee_historique: ${factCount.toLocaleString()} enregistrements\n`);
    
    // 2. Vérification des relations
    console.log('Vérification des relations:');
    
    // Pays avec données historiques
    const countriesWithData = await prisma.pays.findMany({
      where: {
        donneesHistoriques: {
          some: {}
        }
      },
      select: {
        country: true,
        _count: {
          select: { donneesHistoriques: true }
        }
      }
    });
    
    console.log(`${countriesWithData.length} pays ont des données historiques`);
    
    // Indicateurs avec données historiques
    const indicatorsWithData = await prisma.indicateur.findMany({
      where: {
        donneesHistoriques: {
          some: {}
        }
      },
      select: {
        indicator_name: true,
        _count: {
          select: { donneesHistoriques: true }
        }
      }
    });
    
    console.log(`${indicatorsWithData.length} indicateurs ont des données historiques\n`);
    
    // 3. Vérification des données aberrantes
    console.log('Vérification des données aberrantes:');
    
    // Valeurs négatives
    const negativeValues = await prisma.donneeHistorique.count({
      where: {
        OR: [
          { value: { lt: 0 } },
          { cases_per_100k: { lt: 0 } },
          { deaths_per_100k: { lt: 0 } },
          { incidence_7j: { lt: 0 } }
        ]
      }
    });
    
    if (negativeValues > 0) {
      console.log(`${negativeValues} enregistrements avec des valeurs négatives`);
    } else {
      console.log('Aucune valeur négative détectée');
    }
    
    // Valeurs manquantes critiques
    const missingCriticalData = await prisma.donneeHistorique.count({
      where: {
        OR: [
          { date: null },
          { country: null },
          { indicator: null }
        ]
      }
    });
    
    if (missingCriticalData > 0) {
      console.log(`${missingCriticalData} enregistrements avec des données critiques manquantes`);
    } else {
      console.log('Aucune donnée critique manquante');
    }
    
    // 4. Statistiques par source
    console.log('\n Statistiques par source:');
    const sources = await prisma.donneeHistorique.groupBy({
      by: ['source'],
      _count: { source: true },
      _sum: {
        value: true,
        cases_per_100k: true,
        deaths_per_100k: true
      }
    });
    
    sources.forEach(source => {
      console.log(`   ${source.source}:`);
      console.log(`     - Enregistrements: ${source._count.source.toLocaleString()}`);
      console.log(`     - Valeurs totales: ${source._sum.value?.toLocaleString() || 'N/A'}`);
    });
    
    // 5. Statistiques temporelles
    console.log('\n Statistiques temporelles:');
    const dateRange = await prisma.donneeHistorique.aggregate({
      _min: { date: true },
      _max: { date: true }
    });
    
    console.log(`   Période: ${dateRange._min.date?.toISOString().split('T')[0]} à ${dateRange._max.date?.toISOString().split('T')[0]}`);
    
    // 6. Top 10 des pays par nombre de données
    console.log('\n Top 10 des pays par nombre de données:');
    const topCountries = await prisma.donneeHistorique.groupBy({
      by: ['country'],
      _count: { country: true },
      orderBy: {
        _count: {
          country: 'desc'
        }
      },
      take: 10
    });
    
    topCountries.forEach((country, index) => {
      console.log(`   ${index + 1}. ${country.country}: ${country._count.country.toLocaleString()} enregistrements`);
    });
    
    // 7. Vérification des doublons potentiels
    console.log('\n Vérification des doublons potentiels:');
    const duplicates = await prisma.$queryRaw`
      SELECT country, date, indicator, source, COUNT(*) as count
      FROM donnee_historique
      GROUP BY country, date, indicator, source
      HAVING COUNT(*) > 1
      ORDER BY count DESC
      LIMIT 5
    `;
    
    if (duplicates.length > 0) {
      console.log('  Doublons potentiels détectés:');
      duplicates.forEach(dup => {
        console.log(`   ${dup.country} - ${dup.date} - ${dup.indicator}: ${dup.count} occurrences`);
      });
    } else {
      console.log(' Aucun doublon détecté');
    }
    
    console.log('\n Validation terminée avec succès!');
    
  } catch (error) {
    console.error(' Erreur lors de la validation:', error);
  }
}

async function generateSampleQueries() {
  console.log('\n Exemples de requêtes utiles:\n');
  
  try {
    // 1. Données COVID-19 pour la France
    console.log('1. Données COVID-19 pour la France (derniers 7 jours):');
    const franceData = await prisma.donneeHistorique.findMany({
      where: {
        country: 'France',
        source: 'covid',
        date: {
          gte: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)
        }
      },
      orderBy: { date: 'desc' },
      take: 7,
      select: {
        date: true,
        indicator: true,
        value: true,
        cases_per_100k: true
      }
    });
    
    franceData.forEach(record => {
      console.log(`   ${record.date.toISOString().split('T')[0]} - ${record.indicator}: ${record.value} (${record.cases_per_100k?.toFixed(2)}/100k)`);
    });
    
    // 2. Comparaison COVID vs MPOX
    console.log('\n2. Comparaison COVID vs MPOX (top 5 pays par cas):');
    const comparison = await prisma.donneeHistorique.groupBy({
      by: ['country', 'source'],
      _sum: { value: true },
      where: {
        indicator: 'cases',
        value: { gt: 0 }
      },
      orderBy: {
        _sum: {
          value: 'desc'
        }
      },
      take: 10
    });
    
    comparison.forEach(record => {
      console.log(`   ${record.country} (${record.source}): ${record._sum.value?.toLocaleString() || 0} cas`);
    });
    
  } catch (error) {
    console.error(' Erreur lors de la génération des exemples:', error);
  }
}

async function main() {
  console.log('=' * 60);
  console.log(' VALIDATION DE LA BASE DE DONNÉES PANDÉMIES');
  console.log('=' * 60);
  
  await validateDatabaseIntegrity();
  await generateSampleQueries();
}

main()
  .catch((e) => {
    console.error(' Erreur fatale:', e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
    console.log('\n🔌 Connexion fermée.');
  }); 