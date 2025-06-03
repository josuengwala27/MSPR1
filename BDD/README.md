# Dossier BDD

Ce dossier contient tout ce qui concerne la base de données du projet Pandémies :
- Le schéma Prisma (schema.prisma)
- Les scripts d'initialisation et de chargement
- Un fichier .env pour la connexion PostgreSQL

Les scripts de ce dossier utilisent les fichiers générés par l'ETL (dans ETL/processed) pour alimenter la base PostgreSQL.

## Initialisation rapide

1. Configurer la connexion PostgreSQL dans `.env`
2. Initialiser la base avec Prisma
3. Lancer les scripts de chargement

## Installation et initialisation

1. Installer les dépendances Node.js :
   ```bash
   npm install
   ```
2. Configurer la connexion PostgreSQL dans `.env` (voir exemple dans ce dossier).
3. Générer le client Prisma :
   ```bash
   npx prisma generate
   ```
4. Créer les tables dans la base :
   ```bash
   npx prisma db push
   ```
5. (Optionnel) Ouvrir Prisma Studio pour explorer la base :
   ```bash
   npx prisma studio
   ```

## Chargement des dimensions

Après avoir généré les tables, lance le script suivant pour charger les dimensions (pays, indicateurs) :

```bash
node load_data.js
```

Le script va lire les fichiers CSV générés par l'ETL et remplir les tables correspondantes.

Voir la documentation détaillée dans ce dossier. 