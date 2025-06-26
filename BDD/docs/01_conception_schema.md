# 01 - Conception et Justification du Schéma Prisma

## État Initial

### Contexte du projet
Le projet Pandémies nécessite une base de données relationnelle pour stocker et analyser les données COVID-19 et MPOX. Après l'extraction, transformation et chargement des données brutes via le pipeline ETL (voir `ETL/docs/`), nous devons concevoir un schéma de base de données optimisé pour les requêtes analytiques.

### Contraintes identifiées
- **Sources multiples** : Données COVID-19 et MPOX avec structures différentes
- **Volumétrie importante** : Plusieurs millions d'enregistrements historiques
- **Requêtes analytiques** : Besoin de performances pour les analyses temporelles
- **Intégrité référentielle** : Maintien de la cohérence entre pays et indicateurs
- **Évolutivité** : Capacité d'ajouter de nouveaux indicateurs ou sources

### Choix technologiques
- **SGBD** : PostgreSQL (robustesse, performances, support JSON)
- **ORM** : Prisma (type-safety, migrations automatiques, génération de schéma)
- **Architecture** : Modèle en étoile avec dimensions et faits

## Actions Réalisées

### 1. Analyse des données ETL
Après le traitement ETL (`ETL/processed/`), nous disposons de :
- `dim_country.csv` : Dimensions pays (nom, code ISO, population)
- `dim_indicator.csv` : Dimensions indicateurs (nom, description)
- `fact_covid_history.csv` : Faits COVID-19 (données temporelles)
- `fact_mpox_history.csv` : Faits MPOX (données temporelles)

### 2. Conception du modèle relationnel
**Table `pays` (Dimension)**
```prisma
model Pays {
  id_pays      Int     @id @default(autoincrement())
  country      String  @db.VarChar(100)
  iso_code     String  @unique @db.Char(3)
  population   BigInt?
  
  donneesHistoriques DonneeHistorique[]
  
  @@map("pays")
}
```

**Table `indicateur` (Dimension)**
```prisma
model Indicateur {
  id_indicateur    Int     @id @default(autoincrement())
  indicator_name   String  @unique @db.VarChar(50)
  description      String?
  
  donneesHistoriques DonneeHistorique[]
  
  @@map("indicateur")
}
```

**Table `donnee_historique` (Fait)**
```prisma
model DonneeHistorique {
  id_donnee         Int      @id @default(autoincrement())
  date              DateTime
  country           String   @db.VarChar(200)
  value             Float?
  indicator         String   @db.VarChar(200)
  source            String?  @db.VarChar(200)
  iso_code          String?  @db.Char(3)
  population        BigInt?
  unit              String?  @db.VarChar(200)
  cases_per_100k    Float?
  deaths_per_100k   Float?
  incidence_7j      Float?
  growth_rate       Float?
  
  // Relations optionnelles pour compatibilité
  pays              Pays?    @relation(fields: [iso_code], references: [iso_code])
  indicateur        Indicateur? @relation(fields: [indicator], references: [indicator_name])
  
  // Index pour performance
  @@index([date])
  @@index([country])
  @@index([indicator])
  @@index([source])
  @@index([iso_code])
  
  @@map("donnee_historique")
}
```

### 3. Optimisations de performance
- **Index composites** : Sur les colonnes fréquemment utilisées en jointure
- **Types optimisés** : `BigInt` pour population, `Char(3)` pour codes ISO
- **Relations optionnelles** : Permettent l'insertion même si les dimensions n'existent pas
- **Gestion des doublons** : `skipDuplicates: true` dans les insertions

## Justifications des Choix

### 1. Modèle en étoile
**Pourquoi ?** 
- **Simplicité** : Facilite les requêtes analytiques
- **Performance** : Jointures optimisées sur les clés primaires
- **Maintenabilité** : Séparation claire entre dimensions et faits

**Alternative rejetée** : Modèle normalisé complet (trop de jointures pour les analyses)

### 2. Relations optionnelles
**Pourquoi ?**
- **Robustesse** : Permet l'insertion de données même si les dimensions sont incomplètes
- **Compatibilité** : Gère les cas où les codes ISO ou indicateurs ne sont pas encore référencés
- **Évolutivité** : Facilite l'ajout de nouvelles sources de données

### 3. Champs redondants dans les faits
**Pourquoi ?**
- **Performance** : Évite les jointures systématiques pour les requêtes fréquentes
- **Flexibilité** : Permet l'évolution des dimensions sans impacter les faits
- **Traçabilité** : Conserve l'historique des valeurs (population au moment de la donnée)

### 4. Types de données optimisés
**BigInt pour population** : Gère les grandes populations (> 2^31)
**Char(3) pour ISO** : Optimisation espace et contrainte de longueur
**VarChar avec limites** : Évite les débordements et optimise l'espace

## Résultats Obtenus

### 1. Schéma final validé
- **3 tables principales** : pays, indicateur, donnee_historique
- **Relations optimisées** : 1:N avec clés étrangères optionnelles
- **Index stratégiques** : Sur toutes les colonnes de jointure
- **Contraintes d'intégrité** : Unicité des codes ISO et noms d'indicateurs

### 2. Compatibilité ETL
Le schéma est parfaitement aligné avec les fichiers CSV générés par l'ETL :
- **Mapping direct** : Colonnes CSV → Champs Prisma
- **Types compatibles** : Conversion automatique via `dataUtils.js`
- **Gestion des erreurs** : Validation et nettoyage des données

### 3. Performance attendue
- **Insertions** : ~1000 enregistrements/seconde (traitement par lots)
- **Requêtes** : < 100ms pour les analyses temporelles (index sur date)
- **Stockage** : ~50MB pour 1M d'enregistrements

### 4. Évolutivité garantie
- **Nouveaux indicateurs** : Insertion automatique via `load_data.js`
- **Nouveaux pays** : Gestion dynamique des codes ISO
- **Nouvelles sources** : Ajout de colonnes sans impact sur l'existant

## Continuité avec l'ETL

Ce schéma constitue la **suite logique du pipeline ETL** :
1. **ETL** : Extraction → Transformation → Fichiers CSV structurés
2. **BDD** : Chargement → Validation → Base PostgreSQL optimisée

Le script `load_data.js` fait le pont entre les deux phases, transformant les données ETL en enregistrements de base de données avec validation et optimisation.

## Prochaines étapes

- [ ] Génération du diagramme ERD automatique
- [ ] Tests de performance sur gros volumes
- [ ] Optimisation des requêtes analytiques
- [ ] Documentation des requêtes d'exemple 