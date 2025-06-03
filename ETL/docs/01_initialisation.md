# 1. Initialisation du projet ETL Pandémies

## Objectif de l'étape
Mettre en place une base de travail professionnelle, reproductible et collaborative pour tout le cycle de vie du projet ETL (Extraction, Transformation, Chargement, Analyse).

## Ce qui a été fait
- Création d'une arborescence de dossiers claire :
  - `raw_data/` : données brutes
  - `processed/` : données prêtes à charger
  - `logs/` : logs d'exécution
  - `scripts/` : scripts Python ETL
  - `docs/` : documentation, référentiels
- Initialisation d'un environnement virtuel Python (`venv`) pour isoler les dépendances.
- Installation des packages essentiels : `pandas`, `sqlalchemy`, `psycopg2-binary`.
- Création d'un dépôt Git pour le versionnement, avec un `.gitignore` adapté.
- Rédaction d'un `README.md` pour présenter le projet, la structure et les instructions de démarrage.

## Pourquoi ces choix ?
- **Arborescence** : Séparer les données brutes, intermédiaires, finales, les scripts et la documentation permet de garantir la clarté, la maintenabilité et la reproductibilité du projet.
- **Environnement virtuel** : Évite les conflits de dépendances et facilite le déploiement sur d'autres machines.
- **Versionnement** : Permet de suivre l'évolution du projet, de collaborer efficacement et de revenir à un état antérieur en cas de problème.
- **Documentation** : Facilite la prise en main par d'autres utilisateurs et la transmission du projet.

## Résultat de l'étape
- Un socle technique solide, prêt à accueillir les étapes suivantes (collecte, transformation, chargement, analyse).
- Un projet structuré, professionnel, facilement partageable et évolutif.

## Comment l'interpréter ?
- Si tu ouvres le projet, tu comprends immédiatement où placer les données, où écrire les scripts, où trouver la documentation.
- Tu peux installer l'environnement et relancer le projet sur n'importe quelle machine en quelques commandes.
- Tu peux collaborer avec d'autres sans risque de confusion ou d'écrasement de fichiers. 