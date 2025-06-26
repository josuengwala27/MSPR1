# Base de Données Pandémies

Ce module gère la base de données PostgreSQL du projet Pandémies avec Prisma, incluant le schéma, les scripts de chargement, et la documentation complète.

## Structure du projet

```
BDD/
├── src/
│   ├── scripts/          # Scripts principaux
│   │   ├── load_data.js  # Chargement des données
│   │   └── validate_db.js # Validation de la base
│   ├── utils/            # Utilitaires partagés
│   │   └── dataUtils.js  # Fonctions de parsing/validation
│   └── config/           # Configuration
│       └── env.example   # Variables d'environnement
├── tests/                # Tests
│   └── test_loading.js   # Tests de parsing
├── docs/                 # Documentation
│   └── README_BDD.md     # Documentation détaillée
├── ERD/                  # Diagrammes relationnels
│   └── ERD.svg          # Schéma de base généré
├── schema.prisma         # Schéma de base de données
├── package.json          # Dépendances Node.js
└── README.md             # Ce fichier
```

## Installation et initialisation

### 1. Installer les dépendances Node.js
   ```bash
   npm install
   ```

### 2. Configurer la connexion PostgreSQL
- Copier `src/config/env.example` vers `.env`
- Modifier les paramètres de connexion selon votre environnement
   ```bash
cp src/config/env.example .env
   ```

### 3. Initialiser la base de données
   ```bash
npm run setup
```
Cette commande :
- Génère le client Prisma (`npx prisma generate`)
- Crée les tables dans la base (`npx prisma db push`)

### 4. (Optionnel) Explorer la base avec Prisma Studio
   ```bash
npm run prisma:studio
   ```

## Chargement des données

Après avoir généré les tables, lancez le script de chargement pour alimenter la base avec les données de l'ETL :

```bash
npm run load
```

Le script va :
- Lire les fichiers CSV générés par l'ETL (`ETL/processed/`)
- Remplir les tables `pays`, `indicateur`, et `donnee_historique`
- Afficher des statistiques détaillées du chargement

## Scripts disponibles

| Commande | Description |
|----------|-------------|
| `npm run setup` | Génère Prisma et crée les tables |
| `npm run load` | Charge les données depuis l'ETL |
| `npm run validate` | Valide l'intégrité de la base |
| `npm run test` | Teste le parsing des données |
| `npm run prisma:studio` | Interface graphique Prisma |

## Architecture de la base

Le schéma Prisma définit trois tables principales :

### Table `pays`
- **id_pays** (Int, PK) : Identifiant unique
- **country** (String) : Nom du pays
- **iso_code** (String, unique) : Code ISO 3 lettres
- **population** (BigInt, optionnel) : Population du pays

### Table `indicateur`
- **id_indicateur** (Int, PK) : Identifiant unique
- **indicator_name** (String, unique) : Nom de l'indicateur
- **description** (String, optionnel) : Description de l'indicateur

### Table `donnee_historique`
- **id_donnee** (Int, PK) : Identifiant unique
- **date** (DateTime) : Date de la donnée
- **country** (String) : Pays concerné
- **value** (Float, optionnel) : Valeur de l'indicateur
- **indicator** (String) : Nom de l'indicateur
- **source** (String, optionnel) : Source des données
- **iso_code** (String, optionnel) : Code ISO du pays
- **population** (BigInt, optionnel) : Population au moment de la donnée
- **unit** (String, optionnel) : Unité de mesure
- **cases_per_100k** (Float, optionnel) : Cas pour 100k habitants
- **deaths_per_100k** (Float, optionnel) : Décès pour 100k habitants
- **incidence_7j** (Float, optionnel) : Incidence sur 7 jours
- **growth_rate** (Float, optionnel) : Taux de croissance

### Relations
- Un pays peut avoir plusieurs données historiques (1:N)
- Un indicateur peut avoir plusieurs données historiques (1:N)
- Les relations sont optionnelles pour la compatibilité

## Configuration

### Variables d'environnement
Voir `src/config/env.example` pour la liste complète des variables configurables.

**Exemple de configuration :**
```env
DATABASE_URL="postgresql://username:password@localhost:5432/pandemies_db"
```

## Tests et validation

### Tests de parsing
```bash
npm run test
```
Teste :
- La conversion des types de données
- La validation des chaînes de caractères
- La détection des erreurs potentielles
- La connexion à la base de données

### Validation de l'intégrité
```bash
npm run validate
```
Vérifie :
- L'intégrité référentielle
- La cohérence des données
- Les statistiques de la base
- Génère des requêtes d'exemple

## Gestion des erreurs

Les scripts incluent une gestion robuste des erreurs :
- **Validation des types** : Conversion sécurisée des données
- **Gestion des valeurs manquantes** : Traitement des champs optionnels
- **Logs détaillés** : Suivi des opérations et erreurs
- **Statistiques de chargement** : Compteurs de succès/échecs
- **Traitement par lots** : Performance optimisée pour de gros volumes

## Diagramme relationnel (ERD)

Le schéma de base de données est automatiquement généré en SVG :
- **Fichier** : `ERD/ERD.svg`
- **Génération** : Automatique via `prisma-erd-generator`
- **Utilisation** : Documentation, présentations, validation du design

## Structure des scripts

### Scripts principaux (`src/scripts/`)
- **`load_data.js`** : Chargement des données depuis les CSV vers PostgreSQL
- **`validate_db.js`** : Validation complète de l'intégrité de la base

### Utilitaires (`src/utils/`)
- **`dataUtils.js`** : Fonctions communes de parsing et validation des données
  - `safeParseInt()`, `safeParseFloat()`, `safeParseBigInt()`, `safeParseDate()`
  - `validateString()` avec gestion des longueurs maximales
  - Configuration centralisée pour la cohérence

### Tests (`tests/`)
- **`test_loading.js`** : Tests de parsing et de connexion à la base

## Intégration avec l'ETL

Ce module utilise les fichiers générés par le pipeline ETL :
- **Source** : `ETL/processed/`
- **Fichiers attendus** :
  - `dim_country.csv` : Dimensions pays
  - `dim_indicator.csv` : Dimensions indicateurs
  - `fact_covid_history.csv` : Faits COVID-19
  - `fact_mpox_history.csv` : Faits MPOX

## Performance et optimisation

- **Traitement par lots** : Chargement par groupes de 1000 enregistrements
- **Index de base de données** : Optimisation des requêtes fréquentes
- **Gestion des doublons** : Évite les insertions redondantes
- **Validation préalable** : Réduit les erreurs en base

## Support et maintenance

Pour toute question ou problème :
1. Vérifiez les logs d'erreur détaillés
2. Consultez la documentation dans `docs/README_BDD.md`
3. Lancez les tests de validation
4. Vérifiez la configuration de l'environnement 