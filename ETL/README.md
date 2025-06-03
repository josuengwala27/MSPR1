# Pandemic ETL

Ce projet vise à extraire, transformer et charger des données COVID-19 et MPOX dans une base analytique PostgreSQL.

## Structure du projet
- `raw_data/` : fichiers bruts (CSV)
- `processed/` : données prêtes à charger
- `logs/` : logs d'exécution
- `scripts/` : scripts Python ETL
- `docs/` : documentation

## Installation
1. Créez un environnement virtuel Python :
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
2. Installez les dépendances :
   ```powershell
   pip install --upgrade pip
   pip install pandas sqlalchemy psycopg2-binary
   pip freeze > requirements.txt
   ```

## Utilisation
1. Placez les fichiers bruts dans `raw_data/`
2. Exécutez les scripts dans `scripts/` pour chaque étape ETL
3. Consultez les logs dans `logs/` et la documentation dans `docs/`

## Objectif
- Harmoniser et charger les données COVID-19 et MPOX pour analyses comparatives.
- Assurer la qualité, la traçabilité et la reproductibilité du pipeline. 