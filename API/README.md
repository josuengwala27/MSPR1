# API Pandémies

API REST développée avec Express.js et Prisma pour accéder aux données des pandémies COVID-19 et MPOX.

## Installation

1. Cloner le répertoire
2. Installer les dépendances :
   ```
   cd API
   npm install
   ```
3. Configurer la connexion à la base de données PostgreSQL dans le fichier `.env` :
   ```
   DATABASE_URL="postgresql://username:password@localhost:5432/pandemies"
   PORT=3000
   ```
4. Générer le client Prisma :
   ```
   npx prisma generate
   ```

## Démarrage

### Mode développement
```
npm run dev
```

### Mode production
```
npm start
```

## Structure du projet

- `/src` : Code source de l'API
  - `/controllers` : Logique métier
  - `/routes` : Routes de l'API
  - `/middleware` : Middleware Express
- `/prisma` : Configuration Prisma (lien symbolique vers le schéma principal)

## Points d'API

### Pays

- `GET /api/pays` : Liste tous les pays
- `GET /api/pays/:id` : Récupère un pays par ID
- `GET /api/pays/iso/:code` : Récupère un pays par code ISO
- `POST /api/pays` : Crée un nouveau pays
- `PUT /api/pays/:id` : Met à jour un pays
- `DELETE /api/pays/:id` : Supprime un pays

### Indicateurs

- `GET /api/indicateurs` : Liste tous les indicateurs
- `GET /api/indicateurs/:id` : Récupère un indicateur par ID
- `GET /api/indicateurs/nom/:nom` : Récupère un indicateur par nom
- `POST /api/indicateurs` : Crée un nouvel indicateur
- `PUT /api/indicateurs/:id` : Met à jour un indicateur
- `DELETE /api/indicateurs/:id` : Supprime un indicateur

### Données Historiques

- `GET /api/donnees-historiques` : Récupère les données historiques (pagination)
- `GET /api/donnees-historiques/filtre` : Filtre les données historiques
- `GET /api/donnees-historiques/pays/:isoCode` : Récupère les données par pays
- `GET /api/donnees-historiques/:id` : Récupère une donnée par ID
- `POST /api/donnees-historiques` : Crée une nouvelle donnée
- `PUT /api/donnees-historiques/:id` : Met à jour une donnée
- `DELETE /api/donnees-historiques/:id` : Supprime une donnée

## Exemples d'utilisation

### Récupérer les cas COVID en France pour 2020

```
GET /api/donnees-historiques/filtre?pays=France&indicator=cases&dateDebut=2020-01-01&dateFin=2020-12-31
```

### Créer un nouvel enregistrement

```
POST /api/donnees-historiques
{
  "date": "2023-01-01",
  "country": "France",
  "indicator": "cases",
  "value": 1000,
  "iso_code": "FRA",
  "source": "OMS"
}
```

## Lien avec le projet principal

Cette API utilise le même schéma Prisma que le module BDD via un lien symbolique, garantissant la cohérence des modèles de données. 