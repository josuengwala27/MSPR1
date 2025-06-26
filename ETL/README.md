# Pipeline ETL Pandémies 

Pipeline ETL professionnel pour l'analyse comparative des données COVID-19 et MPOX avec **extraction automatisée**, **profiling avancé**, **visualisations automatiques** et **transformation harmonisée**.

## Objectif

Ce projet vise à créer un pipeline ETL robuste et reproductible pour :
- **Extraire** automatiquement les données COVID-19 et MPOX depuis les sources officielles
- **Analyser** et **visualiser** les données avec des graphiques professionnels
- **Transformer** et **harmoniser** les données pour l'analyse comparative
- **Charger** les données dans une base PostgreSQL optimisée pour l'analyse

---

## Structure du projet

```
ETL/
├── raw_data/          # Données brutes téléchargées
├── processed/         # Données transformées et prêtes
├── graphs/            # Visualisations générées automatiquement
├── logs/              # Logs d'exécution détaillés
├── scripts/           # Scripts Python du pipeline ETL
├── docs/              # Documentation professionnelle
└── venv/              # Environnement virtuel Python
```

---

## Installation et configuration

### 1. Prérequis
- **Python 3.8+**
- **Git**
- **PostgreSQL** (pour le chargement final)

### 2. Installation
   ```powershell
# Cloner le projet
git clone <repository-url>
cd MSPR/ETL

# Créer l'environnement virtuel
   python -m venv venv
   .\venv\Scripts\Activate.ps1

# Installer les dépendances
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

---

## Utilisation - Pipeline ETL complet

### Option 1 : Pipeline automatisé complet (RECOMMANDÉ)
```powershell
cd scripts
python run_etl_pipeline.py
```

**Exécute automatiquement :**
1. **Extraction** : Téléchargement sécurisé des données
2. **Profiling** : Analyse exploratoire avec visualisations
3. **Transformation** : Nettoyage et harmonisation
4. **Validation** : Vérification des résultats

### Option 2 : Exécution étape par étape

#### 1. Extraction automatisée
```powershell
python 01_extract.py
```
**Fonctionnalités :**
- Téléchargement automatique depuis Our World in Data
- Vérification d'intégrité avec checksums SHA-256
- Gestion d'erreurs avec retry automatique
- Logging détaillé et traçabilité complète

#### 2. Profiling et analyse exploratoire
```powershell
python 02_profile.py
```
**Visualisations automatiques générées :**
- **Histogrammes** : Distribution des cas et décès
- **Boxplots** : Analyse des outliers et variabilité
- **Heatmaps** : Corrélations entre variables
- **Graphiques temporels** : Évolution des pandémies
- **Analyse comparative** : COVID-19 vs MPOX
- **Top pays** : Impact géographique
- **Métriques avancées** : Létalité, saisonnalité

#### 3. Transformation et nettoyage
```powershell
python 03_transform.py
```
**Fonctionnalités :**
- Harmonisation des schémas COVID-19 et MPOX
- Normalisation des noms de pays et codes ISO
- Calcul des métriques dérivées (incidence 7j, croissance)
- Génération des tables de dimension

#### 4. Tests de validation (optionnel)
```powershell
python test_extract.py      # Tests de l'extraction
python test_coherence.py    # Tests de cohérence globale
```

---

## 📊 Scripts du pipeline ETL

| Script | Fonction | Description |
|--------|----------|-------------|
| `01_extract.py` | **Extraction** | Téléchargement sécurisé des données brutes |
| `02_profile.py` | **Profiling** | Analyse exploratoire + visualisations automatiques |
| `03_transform.py` | **Transformation** | Nettoyage, harmonisation et enrichissement |
| `run_etl_pipeline.py` | **Orchestration** | Pipeline complet automatisé |
| `test_extract.py` | **Tests** | Validation du module d'extraction |
| `test_coherence.py` | **Tests** | Validation de la cohérence globale |

---

## Visualisations générées

### Graphiques par source
- `graphs/covid_analysis.png` : 6 graphiques COVID-19
- `graphs/mpox_analysis.png` : 6 graphiques MPOX

### Analyse comparative
- `graphs/comparative_analysis.png` : 8 graphiques comparatifs

### Types de visualisations
1. **Distributions** : Histogrammes avec échelle log
2. **Outliers** : Boxplots pour détection d'anomalies
3. **Corrélations** : Heatmaps des relations
4. **Évolution temporelle** : Tendances et pics épidémiques
5. **Comparaisons** : Analyse COVID vs MPOX
6. **Géographie** : Top pays par impact
7. **Métriques** : Létalité et saisonnalité

---

## Sources de données

### COVID-19 - Our World in Data
- **URL** : `https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv`
- **Format** : CSV (~50MB)
- **Période** : 2020-2024
- **Granularité** : Quotidienne par pays

### MPOX - Our World in Data
- **URL** : `https://raw.githubusercontent.com/owid/monkeypox/main/owid-monkeypox-data.csv`
- **Format** : CSV (~2MB)
- **Période** : 2022-2024
- **Granularité** : Quotidienne par pays

**Justification du choix :** Our World in Data est une organisation reconnue mondialement pour la qualité et la standardisation de ses données épidémiologiques.

---

## Analyse exploratoire intégrée

### Métriques calculées automatiquement
- **Statistiques descriptives** : Moyenne, médiane, écart-type, quartiles
- **Distributions** : Histogrammes avec détection de patterns
- **Corrélations** : Matrices de corrélation complètes
- **Tendances** : Évolution temporelle et saisonnalité
- **Comparaisons** : Analyse comparative détaillée

### Rapports générés
- **Rapport textuel** : `logs/profiling_report_YYYYMMDD_HHMMSS.txt`
- **Interprétations** : `logs/interpretation_report_YYYYMMDD_HHMMSS.md`
- **Visualisations** : `graphs/` (PNG 300 DPI)
- **Logs détaillés** : Traçabilité complète

---

## Documentation détaillée

### Documentation par étape
- `docs/01_extraction_justification.md` : Extraction automatisée
- `docs/02_profiling_analyse.md` : Profiling et visualisations
- `docs/03_transformation_nettoyage.md` : Transformation et nettoyage
- `docs/04_orchestration_pipeline.md` : Orchestration du pipeline
- `docs/05_tests_validation.md` : Tests et validation
- `docs/06_loading_data.md` : Choix architectural du loading

### Documentation technique
- `docs/benchmark_etl.md` : Comparaison Python vs Talend vs Apache Hop

---

## Résultats attendus

### Fichiers de données transformées
- `processed/fact_covid_history.csv` : Données COVID harmonisées
- `processed/fact_mpox_history.csv` : Données MPOX harmonisées
- `processed/dim_country.csv` : Référentiel des pays
- `processed/dim_indicator.csv` : Référentiel des indicateurs

### Suite du pipeline
**Le chargement (Loading) des données est implémenté dans la partie BDD :**
- **Script** : `BDD/src/scripts/load_data.js`
- **Technologie** : Node.js + Prisma + PostgreSQL
- **Justification** : Cohérence de stack, intégration Prisma, gain de temps de développement

**Voir** `docs/06_loading_data.md` pour la justification détaillée de ce choix architectural.

---

## Performance et qualité

### Métriques de performance
- **Extraction** : ~2 minutes pour 50MB de données
- **Profiling** : ~3 minutes avec génération de 20+ graphiques
- **Transformation** : ~1 minute pour l'harmonisation complète
- **Validation** : Tests automatisés en < 30 secondes

### Qualité des données
- **Intégrité** : Vérification des checksums SHA-256
- **Cohérence** : Validation des schémas et contraintes
- **Complétude** : Détection des données manquantes
- **Traçabilité** : Logs détaillés à chaque étape

