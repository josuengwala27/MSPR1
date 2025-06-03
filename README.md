# MSPR – COVID & MPOX

Cette partie permet d'extraire, transformer et charger (ETL) des données COVID-19 et MPOX dans une base de données analytique PostgreSQL, en utilisant un pipeline Python pour l'ETL et Prisma (Node.js) pour l'orchestration et le chargement.

---

## 1. Organisation du projet

- `ETL/` : Scripts Python, données brutes, données transformées, logs, documentation technique.
- `BDD/` : Schéma Prisma, scripts Node.js de chargement, configuration PostgreSQL.
- `README.md` (ce fichier) : Guide complet d'installation et d'utilisation.

---

## 2. Prérequis

- **Python 3.8+** (pour l'ETL)
- **Node.js 18+** (pour Prisma et le chargement)
- **PostgreSQL 15+** (base de données cible)

---

## 3. Installation étape par étape

### A. Préparer l'environnement Python (ETL)

1. Aller dans le dossier ETL :
   ```bash
   cd ETL
   ```
2. Créer un environnement virtuel et l'activer :
   ```bash
   python -m venv venv
   # Sous Windows :
   .\venv\Scripts\activate
   # Sous Linux/Mac :
   source venv/bin/activate
   ```
3. Installer les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

### B. Préparer l'environnement Node.js (BDD)

1. Aller dans le dossier BDD :
   ```bash
   cd ../BDD
   ```
2. Installer les dépendances Node.js :
   ```bash
   npm install
   ```

### C. Installer PostgreSQL

- Télécharger et installer PostgreSQL depuis [postgresql.org](https://www.postgresql.org/download/)
- Noter le mot de passe de l'utilisateur `postgres` (par défaut utilisé dans la config)
- Acceder à la console de PostgreSQL :
   ```bash
   psql -U postgres
   ```
- Créer une base vide nommée `pandemies` :
   ```sql
   CREATE DATABASE pandemies;
   ```

### D. Configurer la connexion à la base

1. Dans le dossier `BDD`, créer un fichier `.env` avec :
   ```env
   DATABASE_URL="postgresql://postgres:lemotdepasse@localhost:5432/pandemies"
   ```
   *(Adapte le mot de passe si besoin)*

---

## 4. Pipeline complet – Étapes à suivre

### 1. Générer les données transformées (ETL)

- Place les fichiers bruts dans `ETL/raw_data/`
- Exécute les scripts Python dans `ETL/scripts/` pour générer les fichiers transformés dans `ETL/processed/` :
  ```bash
  python scripts/01_extract_and_profile.py
  python scripts/02_transform.py
  ```
- **À observer** :
  - Les fichiers `dim_country.csv`, `dim_indicator.csv`, `fact_covid_history.csv`, `fact_mpox_history.csv` sont créés dans `ETL/processed/`
  - Les logs d'exécution sont dans `ETL/logs/`

### 2. Synchroniser le schéma de la base

- Dans `BDD` :
  ```bash
  npx prisma db push
  ```
- **À observer** :
  - La base PostgreSQL est créée/ajustée selon le schéma Prisma
  - Aucun message d'erreur

### 3. Charger toutes les données dans la base

- Dans `BDD` :
  ```bash
  node load_data.js
  ```
- **À observer** :
  - Nombre de pays et d'indicateurs chargés affiché
  - Nombre de faits chargés pour chaque fichier
  - Aucun message d'erreur

### 4. Visualiser la base et vérifier les données

- Lancer Prisma Studio :
  ```bash
  npx prisma studio
  ```
- **À observer** :
  - Naviguer dans les tables `Pays`, `Indicateur`, `DonneeHistorique`
  - Vérifier la présence des données, la cohérence des champs, la correspondance avec les CSV

---

## 5. Conseils & bonnes pratiques

- Toujours vérifier les logs et les messages d'erreur à chaque étape
- Adapter le fichier `.env` si la configuration PostgreSQL change
- Pour recharger la base à partir de zéro, refaire `npx prisma db push` (attention, cela efface les données)
- Les scripts sont conçus pour ignorer automatiquement les agrégats régionaux (codes ISO non standards)

---

## 6. Ressources utiles

- [Documentation Prisma](https://www.prisma.io/docs/)
- [Documentation PostgreSQL](https://www.postgresql.org/docs/)
- [Documentation Pandas](https://pandas.pydata.org/docs/)

---

**Auteur :** Projet MSPR – ETL Pandémies 