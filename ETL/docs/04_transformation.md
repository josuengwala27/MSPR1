# 4. Transformation des données

## Objectif de l'étape
Nettoyer, harmoniser, enrichir et structurer les données brutes issues de deux sources hétérogènes (COVID-19 et MPOX) pour produire des jeux de données analytiques, comparables et exploitables en base ou en BI. Cette étape est cruciale pour garantir la qualité, la cohérence et la pertinence des analyses futures.

---

## 1. Standardisation des schémas

### a) Pourquoi ?
Les deux sources présentent des structures, des noms de colonnes, des types et des granularités différents. Pour permettre toute analyse croisée ou comparative, il est indispensable d'obtenir un schéma commun, avec des noms, types et significations identiques.

### b) Détail des schémas initiaux réels

#### **COVID-19** (raw_data/worldometer_coronavirus_daily_data.csv)
- **Colonnes présentes** :
  - `date` : Date d'observation (format texte, ex : 2020-2-15)
  - `country` : Nom du pays
  - `cumulative_total_cases` : Cumul des cas depuis le début
  - `daily_new_cases` : Nouveaux cas quotidiens
  - `active_cases` : Cas actifs
  - `cumulative_total_deaths` : Cumul des décès
  - `daily_new_deaths` : Nouveaux décès quotidiens

#### **MPOX** (raw_data/owid-monkeypox-data.csv)
- **Colonnes présentes** :
  - `location` : Nom du pays ou région
  - `iso_code` : Code ISO du pays ou région
  - `date` : Date d'observation
  - `total_cases` : Cumul des cas
  - `total_deaths` : Cumul des décès
  - `new_cases` : Nouveaux cas quotidiens
  - `new_deaths` : Nouveaux décès quotidiens
  - `new_cases_smoothed` : Moyenne mobile des nouveaux cas
  - `new_deaths_smoothed` : Moyenne mobile des nouveaux décès
  - `new_cases_per_million`, `total_cases_per_million`, `new_cases_smoothed_per_million`, `new_deaths_per_million`, `total_deaths_per_million`, `new_deaths_smoothed_per_million` : Indicateurs normalisés par million d'habitants

---

## 2. Sélection et justification des colonnes (détail par source)

### **A. Source COVID-19**

#### a) Colonnes non retenues (et pourquoi)
- **cumulative_total_cases** :
  - *Raison* : Redondant, recalculable à partir des flux quotidiens (daily_new_cases).
- **active_cases** :
  - *Raison* : Définition variable selon les pays, non comparable, parfois incohérent (valeurs négatives ou aberrantes).
- **cumulative_total_deaths** :
  - *Raison* : Redondant, recalculable à partir des flux quotidiens (daily_new_deaths).

#### b) Colonnes retenues (et pourquoi)
- **date** :
  - *Raison* : Clé temporelle, indispensable pour toute analyse de tendance ou d'incidence.
- **country** :
  - *Raison* : Clé géographique principale, harmonisée avec la source MPOX.
- **daily_new_cases** :
  - *Raison* : Indicateur de base, comparable entre pays et avec MPOX.
- **daily_new_deaths** :
  - *Raison* : Indicateur de gravité, essentiel pour l'analyse de la mortalité.

### **B. Source MPOX**

#### a) Colonnes non retenues (et pourquoi)
- **total_cases, total_deaths** :
  - *Raison* : Redondants, recalculables à partir des flux quotidiens (new_cases, new_deaths).
- **new_cases_smoothed, new_deaths_smoothed** :
  - *Raison* : Moyennes mobiles, non harmonisées avec la source COVID-19, recalculables à la demande.
- **new_cases_per_million, total_cases_per_million, new_cases_smoothed_per_million, new_deaths_per_million, total_deaths_per_million, new_deaths_smoothed_per_million** :
  - *Raison* : Indicateurs déjà normalisés, mais pour garantir la cohérence, on recalcule nous-mêmes la normalisation à partir des valeurs brutes et de la population de référence.

#### b) Colonnes retenues (et pourquoi)
- **date** :
  - *Raison* : Clé temporelle, indispensable pour toute analyse de tendance ou d'incidence.
- **location** (renommé en `country`) :
  - *Raison* : Clé géographique principale, harmonisée avec la source COVID-19.
- **iso_code** :
  - *Raison* : Code ISO, utile pour les jointures et la traçabilité.
- **new_cases** :
  - *Raison* : Indicateur de base, comparable entre pays et avec COVID-19.
- **new_deaths** :
  - *Raison* : Indicateur de gravité, essentiel pour l'analyse de la mortalité.

---

## 3. Difficultés rencontrées et solutions apportées

### a) Harmonisation des noms de pays
- Les noms de pays diffèrent entre les deux sources et par rapport aux référentiels ISO (ex : "United States", "USA", "US").
- *Solution* : Création d'un mapping manuel et nettoyage systématique (suppression des espaces, uniformisation de la casse, gestion des variantes).
- Les pays non trouvés dans le référentiel sont listés et corrigés manuellement.

### b) Gestion des valeurs manquantes
- **Pays ou date manquants** :
  - *Action* : Suppression de la ligne (impossible à exploiter).
- **Value manquante (daily_new_cases, daily_new_deaths, new_cases, new_deaths)** :
  - *Action* : Imputation par interpolation linéaire au sein du groupe (pays, indicateur), ou suppression si trop de valeurs manquantes (>20%).
- **Population manquante** :
  - *Action* : Recherche manuelle dans des sources externes (Banque mondiale, ONU), ajout dans un fichier de référence.

### c) Gestion des doublons
- Définition d'une clé composite (`country`, `date`, `indicator`).
- Suppression systématique des doublons, en gardant la dernière valeur connue.
- Vérification post-suppression pour garantir l'unicité.

### d) Uniformisation des types et des formats
- Conversion systématique des dates au format `datetime64[ns]`.
- Conversion des valeurs numériques en `float`.
- Nettoyage des chaînes de caractères (espaces, casse, caractères spéciaux).

---

## 4. Normalisation et enrichissement

### a) Ajout de colonnes de référence
- **iso_code** : Ajout du code ISO 3166-1 alpha-3 pour chaque pays (via un mapping ou directement pour MPOX).
- **population** : Ajout de la population nationale (via un fichier de référence).
- **unit** : Ajout d'une colonne unité (toujours 'count' ici, mais extensible).
- **source** : Ajout d'une colonne pour tracer la provenance (covid/mpox).

### b) Calculs dérivés
- **cases_per_100k, deaths_per_100k** :
  - Calcul : `(value / population) * 100_000` pour permettre la comparaison entre pays de tailles différentes.
- **incidence_7j** :
  - Calcul : Somme glissante sur 7 jours des nouveaux cas/décès pour lisser les variations journalières.
- **growth_rate** :
  - Calcul : Taux de croissance journalier (variation relative par rapport à la veille).
- **Gestion des outliers** :
  - Détection des valeurs aberrantes (ex : +10 000 cas en un jour pour un petit pays), marquage ou correction par interpolation.

---

## 5. Structure finale et justification

### a) Schéma cible harmonisé

| Colonne           | Description                                      | Justification principale                                  |
|-------------------|--------------------------------------------------|-----------------------------------------------------------|
| country           | Nom harmonisé du pays                            | Clé géographique, permet l'analyse multi-source            |
| iso_code          | Code ISO 3166-1 alpha-3                          | Unicité, jointure avec référentiels                       |
| date              | Date d'observation                               | Clé temporelle                                            |
| indicator         | 'cases' ou 'deaths'                              | Indicateur harmonisé, comparabilité                       |
| value             | Valeur brute (nombre de cas/décès)               | Indicateur de base, flux quotidien                        |
| population        | Population nationale                             | Pour normalisation                                        |
| unit              | Unité de mesure ('count')                        | Pour extension future (taux, ratios, etc.)                |
| source            | Source d'origine (covid/mpox)                    | Traçabilité                                               |
| cases_per_100k    | Cas quotidiens pour 100 000 habitants            | Comparabilité entre pays                                  |
| deaths_per_100k   | Décès quotidiens pour 100 000 habitants          | Idem                                                      |
| incidence_7j      | Incidence sur 7 jours                            | Lissage, suivi des tendances                              |
| growth_rate       | Taux de croissance journalier                    | Détection des pics, dynamique épidémique                  |

### b) Fichiers finaux générés
- `fact_covid_history.csv` : Données COVID-19 harmonisées, enrichies, prêtes à charger.
- `fact_mpox_history.csv` : Données MPOX harmonisées, enrichies, prêtes à charger.
- `dim_country.csv` : Table de dimension pays (nom, code ISO, population).
- `dim_indicator.csv` : Table de dimension indicateur (nom, description).

---

## 6. Interprétation et valeur ajoutée

- **Robustesse** : Les choix de colonnes et de nettoyage garantissent la fiabilité des analyses, évitent les biais liés à des définitions variables ou à des données incomplètes.
- **Comparabilité** : Grâce à la normalisation et à l'harmonisation, on peut comparer les dynamiques COVID-19 et MPOX entre pays et dans le temps.
- **Traçabilité** : Chaque transformation est documentée, chaque valeur peut être reliée à sa source et à ses règles de calcul.
- **Flexibilité** : Le schéma cible permet d'ajouter d'autres indicateurs ou sources à l'avenir sans refondre tout le pipeline.

---

## 7. Tableau comparatif des schémas (exemple)

| Source   | Colonne initiale      | Colonne finale (harmonisée) | Retenue ? | Justification principale                  |
|----------|-----------------------|-----------------------------|-----------|-------------------------------------------|
| COVID-19 | date                  | date                        | Oui       | Clé temporelle                           |
| COVID-19 | country               | country                     | Oui       | Clé géographique                         |
| COVID-19 | cumulative_total_cases| (non retenue)               | Non       | Redondant, recalculable                  |
| COVID-19 | daily_new_cases       | value (indicator='cases')   | Oui       | Indicateur de base                       |
| COVID-19 | active_cases          | (non retenue)               | Non       | Définition variable, peu fiable           |
| COVID-19 | cumulative_total_deaths| (non retenue)              | Non       | Redondant, recalculable                  |
| COVID-19 | daily_new_deaths      | value (indicator='deaths')  | Oui       | Indicateur de gravité                    |
| MPOX     | date                  | date                        | Oui       | Clé temporelle                           |
| MPOX     | location              | country                     | Oui       | Clé géographique                         |
| MPOX     | iso_code              | iso_code                    | Oui       | Jointure, traçabilité                    |
| MPOX     | total_cases           | (non retenue)               | Non       | Redondant, recalculable                  |
| MPOX     | total_deaths          | (non retenue)               | Non       | Redondant, recalculable                  |
| MPOX     | new_cases             | value (indicator='cases')   | Oui       | Indicateur de base                       |
| MPOX     | new_deaths            | value (indicator='deaths')  | Oui       | Indicateur de gravité                    |
| MPOX     | new_cases_smoothed    | (non retenue)               | Non       | Moyenne mobile, recalculable             |
| MPOX     | new_deaths_smoothed   | (non retenue)               | Non       | Moyenne mobile, recalculable             |
| MPOX     | new_cases_per_million | (non retenue)               | Non       | Calculé à la demande, cohérence          |
| MPOX     | total_cases_per_million| (non retenue)              | Non       | Calculé à la demande, cohérence          |
| MPOX     | new_cases_smoothed_per_million| (non retenue)        | Non       | Calculé à la demande, cohérence          |
| MPOX     | new_deaths_per_million| (non retenue)               | Non       | Calculé à la demande, cohérence          |
| MPOX     | total_deaths_per_million| (non retenue)              | Non       | Calculé à la demande, cohérence          |
| MPOX     | new_deaths_smoothed_per_million| (non retenue)       | Non       | Calculé à la demande, cohérence          |

---

**En résumé** :
La transformation a permis de passer de deux jeux de données hétérogènes, redondants et partiellement incomplets à un modèle harmonisé, enrichi, documenté et prêt pour l'analyse avancée et le chargement en base. Chaque choix de colonne, de nettoyage ou d'enrichissement a été motivé par la recherche de robustesse, de comparabilité et de traçabilité. 