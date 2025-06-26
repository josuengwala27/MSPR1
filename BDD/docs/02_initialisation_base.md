# 02 - Installation, Configuration et Initialisation

## État Initial

### Prérequis identifiés
Après la phase ETL qui a généré les fichiers CSV structurés (`ETL/processed/`), nous devons initialiser l'environnement de base de données pour charger ces données dans PostgreSQL.

### Environnement cible
- **SGBD** : PostgreSQL 12+ (support des types BigInt et index avancés)
- **Runtime** : Node.js 16+ (support des modules ES et async/await)
- **ORM** : Prisma 5.x (génération automatique du client et migrations)
- **OS** : Compatible Windows/Linux/macOS

### Dépendances nécessaires
- **@prisma/client** : Client ORM type-safe
- **csv-parse** : Parsing des fichiers CSV de l'ETL
- **prisma-erd-generator** : Génération automatique du diagramme relationnel

## Actions Réalisées

### 1. Structure du projet
```
BDD/
├── src/
│   ├── scripts/          # Scripts de chargement (suite ETL)
│   │   ├── load_data.js  # Chargement depuis ETL/processed/
│   │   └── validate_db.js # Validation de l'intégrité
│   ├── utils/            # Utilitaires partagés
│   │   └── dataUtils.js  # Fonctions de parsing/validation
│   └── config/           # Configuration
│       └── env.example   # Template des variables d'environnement
├── tests/                # Tests de validation
├── docs/                 # Documentation
├── ERD/                  # Diagrammes relationnels générés
├── schema.prisma         # Schéma de base de données
└── package.json          # Dépendances et scripts
```

### 2. Configuration des dépendances
**package.json** - Scripts automatisés :
```json
{
  "scripts": {
    "prisma:generate": "prisma generate",
    "prisma:dbpush": "prisma db push",
    "prisma:studio": "prisma studio",
    "load": "node src/scripts/load_data.js",
    "validate": "node src/scripts/validate_db.js",
    "test": "node tests/test_loading.js",
    "setup": "npm run prisma:generate && npm run prisma:dbpush"
  }
}
```

### 3. Configuration de l'environnement
**src/config/env.example** - Template de configuration :
```env
# Connexion PostgreSQL (suite du pipeline ETL)
DATABASE_URL="postgresql://username:password@localhost:5432/pandemies_db"

# Configuration du chargement
BATCH_SIZE=1000
ETL_PROCESSED_DIR=../ETL/processed
```

### 4. Scripts d'initialisation
**npm run setup** - Initialisation complète :
```bash
# 1. Génération du client Prisma
npx prisma generate

# 2. Création des tables en base
npx prisma db push

# 3. Vérification de la connexion
npx prisma studio
```

## Justifications des Choix

### 1. Organisation modulaire
**Pourquoi cette structure ?**
- **Séparation des responsabilités** : Scripts, utilitaires, config séparés
- **Réutilisabilité** : `dataUtils.js` centralise les fonctions communes
- **Maintenabilité** : Tests isolés, documentation organisée
- **Évolutivité** : Ajout facile de nouveaux scripts ou utilitaires

### 2. Scripts npm automatisés
**Pourquoi ces commandes ?**
- **Simplicité** : `npm run setup` pour tout initialiser
- **Cohérence** : Même interface sur tous les environnements
- **Documentation** : Les commandes sont auto-documentées
- **Intégration CI/CD** : Facilite l'automatisation

### 3. Configuration centralisée
**Pourquoi env.example ?**
- **Sécurité** : Pas de credentials en dur dans le code
- **Flexibilité** : Configuration par environnement
- **Onboarding** : Guide pour les nouveaux développeurs
- **Portabilité** : Fonctionne sur tous les environnements

### 4. Prisma comme ORM
**Pourquoi Prisma ?**
- **Type-safety** : Génération automatique des types TypeScript
- **Migrations automatiques** : `db push` pour le développement
- **Client optimisé** : Requêtes préparées et connection pooling
- **Écosystème riche** : Studio, ERD generator, introspection

## Résultats Obtenus

### 1. Environnement opérationnel
- **Base de données** : Tables créées avec contraintes et index
- **Client Prisma** : Généré et prêt pour les requêtes
- **Configuration** : Variables d'environnement sécurisées
- **Scripts** : Commandes npm fonctionnelles

### 2. Intégration ETL réussie
La configuration permet une **transition fluide** depuis l'ETL :
- **Chemin relatif** : `../ETL/processed` pour accéder aux fichiers CSV
- **Types compatibles** : Mapping direct CSV → Prisma
- **Validation** : Même logique de parsing que l'ETL

### 3. Tests de validation
- **Connexion** : Test de connectivité à PostgreSQL
- **Parsing** : Validation des types de données
- **Chargement** : Test avec échantillon de données
- **Intégrité** : Vérification des contraintes

### 4. Documentation complète
- **README principal** : Guide d'installation et utilisation
- **Scripts documentés** : Chaque commande expliquée
- **Configuration** : Template avec exemples
- **Structure** : Organisation claire du projet

## Continuité avec l'ETL

Cette phase d'initialisation constitue le **pont technologique** entre ETL et BDD :

### Flux de données
1. **ETL** : `raw_data/` → `processed/` (fichiers CSV structurés)
2. **BDD** : `processed/` → PostgreSQL (base relationnelle optimisée)

### Scripts de transition
- **`load_data.js`** : Lit les CSV ETL et les insère en base
- **`dataUtils.js`** : Réutilise la logique de parsing de l'ETL
- **`validate_db.js`** : Vérifie la cohérence des données chargées

### Configuration unifiée
- **Variables d'environnement** : Cohérentes avec l'ETL
- **Types de données** : Alignés sur les transformations ETL
- **Gestion d'erreurs** : Même approche robuste

## Prochaines étapes

- [ ] Chargement des données depuis l'ETL
- [ ] Validation de l'intégrité de la base
- [ ] Tests de performance
- [ ] Optimisation des requêtes 