# 3. Profilage et diagnostic

## Objectif de l'étape
Analyser en profondeur la structure, la qualité et la distribution des données brutes pour anticiper les besoins de nettoyage, de transformation et d'harmonisation.

## Ce qui a été fait
- Chargement des fichiers bruts dans des DataFrames Pandas.
- Listing des colonnes et des types détectés automatiquement.
- Comptage des valeurs manquantes par colonne.
- Analyse de la distribution des indicateurs (ex : cases, deaths, etc.).
- Identification des doublons potentiels (lignes identiques ou clés composites).
- Génération d'un rapport de profiling détaillé (logs/profiling_report_*.txt).

## Pourquoi ces choix ?
- **Profiling systématique** : Permet de détecter très tôt les problèmes de schéma, de types, de valeurs manquantes ou aberrantes.
- **Analyse des indicateurs** : Aide à comprendre la granularité, la couverture et la pertinence des données pour l'analyse future.
- **Détection des doublons** : Évite de fausser les analyses ou de surévaluer certains indicateurs.

## Résultat de l'étape
- Rapport détaillé sur la structure et la qualité des données.
- Liste claire des colonnes à harmoniser, des valeurs à imputer ou à supprimer, des clés à utiliser pour l'unicité.
- Vision précise des différences entre les deux sources (COVID-19 et MPOX).

## Comment l'interpréter ?
- Le rapport de profiling permet de planifier précisément les étapes de transformation (mapping des colonnes, gestion des NaN, choix des indicateurs).
- Les problèmes détectés ici (ex : valeurs manquantes, doublons) sont traités dans l'étape suivante.
- Cette étape garantit que la transformation sera adaptée à la réalité des données et non à des hypothèses. 