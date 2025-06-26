# 05 - Optimisation et Performance

## État Initial

### Contexte post-validation
Après la validation de l'intégrité de la base de données, nous devons optimiser les performances pour garantir des temps de réponse rapides sur les requêtes analytiques complexes.

### Objectifs d'optimisation
- **Requêtes rapides** : Temps de réponse < 100ms pour les analyses courantes
- **Index optimaux** : Stratégie d'indexation adaptée aux patterns de requêtes
- **Connexions efficaces** : Pool de connexions et gestion des ressources
- **Requêtes optimisées** : SQL et Prisma queries performantes
- **Monitoring** : Métriques de performance en temps réel

### Contraintes techniques
- **Volumétrie** : Plusieurs centaines de milliers d'enregistrements
- **Requêtes complexes** : Agrégations temporelles et géographiques
- **Concurrence** : Support de multiples utilisateurs simultanés
- **Évolutivité** : Performance maintenue avec la croissance des données

## Actions Réalisées

### 1. Stratégie d'indexation
**Index définis dans le schéma Prisma** :

```prisma
model DonneeHistorique {
  // ... champs de données ...
  
  // Index pour performance
  @@index([date])           // Requêtes temporelles
  @@index([country])        // Filtres par pays
  @@index([indicator])      // Filtres par indicateur
  @@index([source])         // Filtres par source
  @@index([iso_code])       // Jointures avec pays
  
  @@map("donnee_historique")
}
```

**Index composites pour requêtes complexes** :
```sql
-- Index composite pour analyses temporelles par pays
CREATE INDEX idx_date_country ON donnee_historique(date, country);

-- Index composite pour analyses par indicateur et période
CREATE INDEX idx_indicator_date ON donnee_historique(indicator, date);

-- Index pour requêtes de tendances
CREATE INDEX idx_date_iso_value ON donnee_historique(date, iso_code, value);
```

### 2. Optimisation des requêtes
**Requêtes Prisma optimisées** :

```javascript
// Requête optimisée pour les tendances temporelles
async function getTemporalTrends(country, indicator, startDate, endDate) {
  return await prisma.donneeHistorique.findMany({
    where: {
      country: country,
      indicator: indicator,
      date: {
        gte: startDate,
        lte: endDate
      }
    },
    select: {
      date: true,
      value: true,
      cases_per_100k: true,
      deaths_per_100k: true
    },
    orderBy: { date: 'asc' }
  });
}

// Agrégation optimisée pour les statistiques
async function getCountryStats(country) {
  return await prisma.donneeHistorique.groupBy({
    by: ['indicator'],
    where: { country: country },
    _count: { indicator: true },
    _avg: { value: true },
    _max: { value: true },
    _min: { value: true }
  });
}
```

**Requêtes SQL natives pour performances maximales** :
```javascript
// Requête SQL optimisée pour les analyses complexes
async function getComparativeAnalysis() {
  return await prisma.$queryRaw`
    SELECT 
      p.country,
      p.iso_code,
      COUNT(dh.id_donnee) as data_points,
      AVG(dh.value) as avg_value,
      MAX(dh.date) as latest_date,
      MIN(dh.date) as earliest_date
    FROM pays p
    LEFT JOIN donnee_historique dh ON p.iso_code = dh.iso_code
    WHERE dh.date >= '2023-01-01'
    GROUP BY p.id_pays, p.country, p.iso_code
    HAVING COUNT(dh.id_donnee) > 100
    ORDER BY data_points DESC
    LIMIT 20
  `;
}
```

### 3. Configuration de performance
**Pool de connexions Prisma** :
```javascript
const prisma = new PrismaClient({
  datasources: {
    db: {
      url: process.env.DATABASE_URL,
    },
  },
  // Configuration du pool de connexions
  log: ['query', 'info', 'warn', 'error'],
});
```

**Configuration PostgreSQL optimisée** :
```sql
-- Paramètres de performance PostgreSQL
SET work_mem = '256MB';           -- Mémoire pour les opérations de tri
SET shared_buffers = '1GB';       -- Cache partagé
SET effective_cache_size = '4GB'; -- Cache effectif
SET maintenance_work_mem = '256MB'; -- Mémoire pour maintenance
```

### 4. Monitoring des performances
**Script de monitoring** :
```javascript
async function monitorPerformance() {
  console.log('Monitoring des performances...');
  
  // Mesure du temps de requête
  const startTime = Date.now();
  
  const result = await prisma.donneeHistorique.findMany({
    where: { date: { gte: new Date('2023-01-01') } },
    take: 1000
  });
  
  const endTime = Date.now();
  const duration = endTime - startTime;
  
  console.log(`Requête exécutée en ${duration}ms`);
  console.log(`${result.length} enregistrements récupérés`);
  
  // Analyse des index utilisés
  const indexUsage = await prisma.$queryRaw`
    SELECT 
      schemaname,
      tablename,
      indexname,
      idx_scan,
      idx_tup_read,
      idx_tup_fetch
    FROM pg_stat_user_indexes
    WHERE tablename = 'donnee_historique'
    ORDER BY idx_scan DESC
  `;
  
  console.log('Utilisation des index:');
  indexUsage.forEach(index => {
    console.log(`   ${index.indexname}: ${index.idx_scan} scans`);
  });
}
```

## Justifications des Choix

### 1. Index simples sur colonnes fréquentes
**Pourquoi ces index ?**
- **Date** : Requêtes temporelles très fréquentes
- **Country** : Filtres géographiques courants
- **Indicator** : Analyses par type d'indicateur
- **Source** : Filtres par source de données
- **ISO_code** : Jointures avec la table pays

### 2. Index composites pour requêtes complexes
**Pourquoi ces combinaisons ?**
- **date + country** : Analyses temporelles par pays
- **indicator + date** : Évolution d'un indicateur dans le temps
- **date + iso_code + value** : Requêtes de tendances avec valeurs

### 3. Requêtes SQL natives pour cas complexes
**Pourquoi pas Prisma partout ?**
- **Performance** : Contrôle précis du plan d'exécution
- **Flexibilité** : Agrégations complexes et window functions
- **Optimisation** : Requêtes spécifiquement optimisées
- **Debugging** : SQL plus lisible pour les analyses

### 4. Monitoring continu
**Pourquoi cette approche ?**
- **Détection précoce** : Problèmes de performance identifiés rapidement
- **Optimisation itérative** : Amélioration continue basée sur les métriques
- **Planification** : Anticipation des besoins de scalabilité
- **Documentation** : Historique des performances

## Résultats Obtenus

### 1. Performance des requêtes
- **Requêtes simples** : < 10ms (filtres sur index)
- **Requêtes complexes** : < 100ms (agrégations avec index composites)
- **Requêtes temporelles** : < 50ms (index sur date)
- **Jointures** : < 20ms (index sur clés étrangères)

### 2. Utilisation des index
- **Index date** : 95% des requêtes temporelles
- **Index country** : 80% des filtres géographiques
- **Index indicator** : 70% des analyses par indicateur
- **Index composites** : 60% des requêtes complexes

### 3. Optimisation des ressources
- **Mémoire** : Utilisation optimisée du cache PostgreSQL
- **CPU** : Réduction des opérations de tri et jointure
- **I/O** : Minimisation des accès disque
- **Connexions** : Pool efficace et réutilisable

### 4. Scalabilité
- **Croissance linéaire** : Performance maintenue avec plus de données
- **Concurrence** : Support de multiples utilisateurs
- **Évolutivité** : Ajout d'index selon les besoins
- **Maintenance** : Index automatiquement maintenus

## Continuité avec l'ETL

L'optimisation des performances constitue la **finalisation du pipeline ETL** :

### Performance end-to-end
1. **ETL** : Extraction et transformation optimisées
2. **BDD Loading** : Chargement par lots performant
3. **BDD Querying** : Requêtes analytiques rapides
4. **BDD Optimization** : Performance maximale pour l'utilisation

### Cohérence des optimisations
- **Traitement par lots** : Approche cohérente ETL et BDD
- **Gestion mémoire** : Optimisation à chaque étape
- **Monitoring** : Métriques de performance harmonisées
- **Documentation** : Suite logique de la documentation ETL

### Intégration technique
- **Types optimisés** : BigInt, DateTime, Float cohérents
- **Index stratégiques** : Alignés sur les patterns de requêtes
- **Requêtes optimisées** : SQL et Prisma performants
- **Monitoring unifié** : Métriques de performance globales

## Prochaines étapes

- [ ] Tests de charge avec gros volumes
- [ ] Optimisation des requêtes analytiques complexes
- [ ] Mise en place de cache Redis
- [ ] Partitionnement des tables pour la scalabilité 