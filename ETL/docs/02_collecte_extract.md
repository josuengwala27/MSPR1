# 2. Collecte des données (Extract)

## Objectif de l'étape
Rassembler les données brutes nécessaires à l'analyse, garantir leur intégrité et préparer leur chargement dans l'ETL.

## Ce qui a été fait
- Téléchargement manuel de deux jeux de données :
  - COVID-19 (worldometer_coronavirus_daily_data.csv)
  - MPOX (owid-monkeypox-data.csv)
- Placement des fichiers dans le dossier `raw_data/`.
- Vérification de l'intégrité des fichiers :
  - Ouverture pour vérifier la présence d'un header, l'absence de corruption, la cohérence du format.
  - Vérification de la taille (fichiers adaptés à un traitement en mémoire).
- (Optionnel) Copie des fichiers dans `staging/` pour conserver les sources brutes intactes.
- Chargement des fichiers dans des DataFrames Pandas pour un premier aperçu.

## Pourquoi ces choix ?
- **Séparation raw_data/staging** : Permet de toujours garder une copie immuable des données brutes, et de travailler sur des copies pour éviter toute altération accidentelle.
- **Vérification d'intégrité** : Évite de propager des erreurs ou des corruptions dans le pipeline.
- **Chargement dans Pandas** : Permet un premier contrôle rapide de la structure et du contenu.

## Résultat de l'étape
- Deux fichiers bruts valides, prêts à être profilés et transformés.
- Les données sont centralisées, versionnées, et leur intégrité est garantie.

## Comment l'interpréter ?
- Les fichiers dans `raw_data/` sont la source de vérité : toute transformation ultérieure part de ces fichiers.
- Si un problème est détecté plus tard, on peut toujours revenir à ces fichiers pour recharger ou corriger.
- Le pipeline est prêt à passer à l'étape de profiling et de diagnostic. 