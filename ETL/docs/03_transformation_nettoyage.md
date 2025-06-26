# 3. Transformation et Nettoyage des Données - Harmonisation et Enrichissement

## Objectif de l'étape

La transformation et le nettoyage visent à harmoniser deux jeux de données hétérogènes (COVID-19 et MPOX) en un modèle unifié, propre et exploitable. Cette étape transforme les données brutes en un format standardisé avec des métriques comparables, des référentiels cohérents et des indicateurs enrichis pour l'analyse.

---

## Cheminement de la transformation

### 3.1 Architecture technique implémentée

#### **Script principal** : `03_transform.py`
- **Langage** : Python 3.x
- **Bibliothèques** : pandas, numpy
- **Fonctionnalités** : Harmonisation + Nettoyage + Enrichissement
- **Sorties** : Fichiers CSV standardisés + Tables de dimension

#### **Structure des répertoires**
```
ETL/
├── processed/              # Données transformées
│   ├── fact_covid_history.csv
│   ├── fact_mpox_history.csv
│   ├── dim_country.csv
│   └── dim_indicator.csv
├── docs/                   # Fichiers de référence
│   ├── country_population_reference.csv
│   └── iso_country_codes.csv
└── scripts/
    └── 03_transform.py     # Script de transformation principal
```

### 3.2 Étapes de transformation

#### **1. Standardisation des schémas**
- Harmonisation des noms de colonnes
- Conversion des types de données
- Gestion des valeurs manquantes
- Suppression des doublons

#### **2. Nettoyage et validation**
- Normalisation des noms de pays
- Validation des codes ISO
- Gestion des outliers
- Imputation des valeurs manquantes

#### **3. Enrichissement**
- Ajout des populations
- Calcul des métriques normalisées
- Création d'indicateurs dérivés
- Génération des tables de dimension

---

## Justifications des choix de transformation

### 4.1 Analyse des schémas initiaux

#### **COVID-19 - Schéma initial**
```python
# Colonnes disponibles dans les données brutes
covid_columns = [
    'date', 'location', 'iso_code', 'new_cases', 'new_deaths',
    'total_cases', 'total_deaths', 'population',
    'new_cases_per_million', 'new_deaths_per_million',
    'total_cases_per_million', 'total_deaths_per_million'
]
```

#### **MPOX - Schéma initial**
```python
# Colonnes disponibles dans les données brutes
mpox_columns = [
    'date', 'location', 'iso_code', 'new_cases', 'new_deaths',
    'total_cases', 'total_deaths',
    'new_cases_smoothed', 'new_deaths_smoothed',
    'new_cases_per_million', 'new_deaths_per_million'
]
```

### 4.2 Décisions de sélection des colonnes

#### **Colonnes CONSERVÉES et justifications**

##### **`date` - Clé temporelle**
**Justification :**
- **Obligatoire** : Indispensable pour toute analyse temporelle
- **Format** : Conversion en `datetime64[ns]` pour cohérence
- **Usage** : Tri, filtrage, agrégation temporelle

##### **`location` → `country` - Clé géographique**
**Justification :**
- **Harmonisation** : Renommé en `country` pour cohérence
- **Nettoyage** : Suppression des espaces, uniformisation de la casse
- **Usage** : Jointures géographiques, analyses par pays

##### **`iso_code` - Identifiant unique**
**Justification :**
- **Standardisation** : Code ISO 3166-1 alpha-3
- **Unicité** : Identifiant unique par pays
- **Usage** : Jointures avec référentiels externes

##### **`new_cases` → `value` - Indicateur principal**
**Justification :**
- **Flux quotidien** : Mesure de l'activité épidémique
- **Comparabilité** : Même métrique entre COVID et MPOX
- **Usage** : Analyses de tendance, détection de pics

##### **`new_deaths` → `value` - Indicateur de gravité**
**Justification :**
- **Sévérité** : Mesure de la létalité
- **Décalage temporel** : Suit les cas avec délai
- **Usage** : Analyses de mortalité, taux de létalité

#### **Colonnes SUPPRIMÉES et justifications**

##### **`total_cases` et `total_deaths` - Cumuls**
**Justification de suppression :**
- **Redondance** : Calculable à partir des flux quotidiens
- **Espace** : Économie de stockage significative
- **Cohérence** : Évite les incohérences de cumul
- **Recalcul** : `total = sum(new_cases)` si nécessaire

##### **`new_cases_smoothed` et `new_deaths_smoothed` - Moyennes mobiles**
**Justification de suppression :**
- **Recalculabilité** : Moyenne mobile = `rolling(window=7).mean()`
- **Paramètres** : Fenêtre variable selon les besoins
- **Flexibilité** : Permet différents types de lissage
- **Cohérence** : Même logique pour COVID et MPOX

##### **`*_per_million` - Indicateurs normalisés**
**Justification de suppression :**
- **Recalcul** : `per_million = (value / population) * 1_000_000`
- **Population** : Source de référence à maintenir
- **Flexibilité** : Permet différentes normalisations (100k, 10k)
- **Cohérence** : Calcul uniforme pour toutes les sources

### 4.3 Schéma final harmonisé

#### **Structure cible unifiée**
```python
# Colonnes finales pour les tables de faits
target_columns = [
    'country', 'date', 'indicator', 'value', 'iso_code',
    'population', 'unit', 'source',
    'cases_per_100k', 'deaths_per_100k',
    'incidence_7j', 'growth_rate'
]
```

#### **Justification du schéma cible**
- **`country`** : Nom harmonisé du pays
- **`date`** : Date d'observation (datetime)
- **`indicator`** : 'cases' ou 'deaths' (catégorisation)
- **`value`** : Valeur brute (nombre de cas/décès)
- **`iso_code`** : Code ISO 3166-1 alpha-3
- **`population`** : Population nationale (BigInt)
- **`unit`** : Unité de mesure ('count')
- **`source`** : Source d'origine ('covid' ou 'mpox')
- **`cases_per_100k`** : Cas normalisés par 100k habitants
- **`deaths_per_100k`** : Décès normalisés par 100k habitants
- **`incidence_7j`** : Incidence sur 7 jours (somme glissante)
- **`growth_rate`** : Taux de croissance journalier

---

## Nettoyage et harmonisation

### 5.1 Normalisation des noms de pays

#### **Problèmes identifiés**
```python
# Exemples de variantes trouvées
country_variants = {
    'United States': ['USA', 'US', 'United States of America'],
    'United Kingdom': ['UK', 'Great Britain'],
    'Czech Republic': ['Czechia', 'Czech Republic'],
    'Côte d\'Ivoire': ['Cote d Ivoire', 'Ivory Coast']
}
```

#### **Solution implémentée**
```python
def normalize_country_name(country_name):
    """Normalise les noms de pays pour améliorer le mapping"""
    name = str(country_name).strip().lower()
    
    # Mapping des variantes courantes
    country_mapping = {
        'cabo verde': 'cape verde',
        'cote d\'ivoire': 'cote d ivoire',
        'uk': 'united kingdom',
        'usa': 'united states',
        'czech republic': 'czechia'
    }
    
    return country_mapping.get(name, name)
```

**Justification :**
- **Cohérence** : Noms uniformes entre sources
- **Jointures** : Facilite les jointures avec référentiels
- **Analyse** : Évite les doublons par variantes de noms

### 5.2 Gestion des valeurs manquantes

#### **Stratégie par type de donnée**

##### **Données critiques (date, country, indicator)**
**Action :** Suppression de la ligne
**Justification :**
- **Impossible à exploiter** : Sans ces données, l'enregistrement est inutilisable
- **Qualité** : Mieux vaut moins de données mais de qualité

##### **Données numériques (value, population)**
**Action :** Imputation par interpolation linéaire
**Justification :**
- **Continuité** : Évite les trous dans les séries temporelles
- **Précision** : Interpolation plus précise que moyenne globale
- **Contexte** : Par groupe (pays, indicateur) pour respecter les patterns

##### **Codes ISO manquants**
**Action :** Recherche dans référentiel + création mapping
**Justification :**
- **Standardisation** : Codes ISO essentiels pour jointures
- **Traçabilité** : Permet l'identification unique des pays
- **International** : Standard reconnu mondialement

### 5.3 Suppression des doublons

#### **Clé composite définie**
```python
# Clé d'unicité : (country, date, indicator)
duplicate_key = ['country', 'date', 'indicator']
```

**Justification :**
- **Logique métier** : Un pays ne peut avoir qu'une valeur par jour par indicateur
- **Cohérence** : Évite les incohérences de données
- **Performance** : Optimise les requêtes et analyses

---

## Enrichissement et calculs dérivés

### 6.1 Normalisation par population

#### **Calcul des métriques normalisées**
```python
# Normalisation par 100k habitants
df['cases_per_100k'] = np.where(
    (df['indicator'] == 'cases') & (df['population'].notna()),
    (df['value'] / df['population']) * 100000,
    np.nan
)

df['deaths_per_100k'] = np.where(
    (df['indicator'] == 'deaths') & (df['population'].notna()),
    (df['value'] / df['population']) * 100000,
    np.nan
)
```

**Justification :**
- **Comparabilité** : Permet de comparer des pays de tailles différentes
- **Équité** : Évite le biais de la taille de population
- **Standard** : Métrique reconnue en épidémiologie

### 6.2 Indicateurs dérivés

#### **Incidence sur 7 jours**
```python
df['incidence_7j'] = df.groupby(['country', 'indicator'])['value'].transform(
    lambda x: x.rolling(window=7, min_periods=1).sum()
)
```

**Justification :**
- **Lissage** : Réduit la variabilité journalière
- **Tendance** : Meilleur indicateur de l'évolution
- **Standard** : Métrique utilisée par les autorités sanitaires

#### **Taux de croissance**
```python
df['growth_rate'] = df.groupby(['country', 'indicator'])['value'].pct_change()
```

**Justification :**
- **Dynamique** : Mesure l'accélération/décélération
- **Détection** : Identifie les pics et creux
- **Prévision** : Indicateur pour la modélisation

### 6.3 Tables de dimension

#### **Table `dim_country`**
```python
# Structure de la table pays
dim_country_columns = ['country', 'iso_code', 'population']
```

**Justification :**
- **Normalisation** : Évite la redondance des données pays
- **Mise à jour** : Facilite les mises à jour de population
- **Jointures** : Optimise les requêtes géographiques

#### **Table `dim_indicator`**
```python
# Structure de la table indicateur
dim_indicator_data = [
    {'indicator_name': 'cases', 'description': 'Nombre de cas'},
    {'indicator_name': 'deaths', 'description': 'Nombre de décès'}
]
```

**Justification :**
- **Extensibilité** : Permet d'ajouter de nouveaux indicateurs
- **Documentation** : Décrit chaque indicateur
- **Flexibilité** : Supporte différents types d'indicateurs

---

## Résultats de la transformation

### 7.1 Fichiers générés

#### **Tables de faits**
- `fact_covid_history.csv` : 1,500,000+ lignes, 12 colonnes
- `fact_mpox_history.csv` : 50,000+ lignes, 12 colonnes

#### **Tables de dimension**
- `dim_country.csv` : 200+ pays, 3 colonnes
- `dim_indicator.csv` : 2 indicateurs, 2 colonnes

### 7.2 Métriques de qualité

#### **Avant transformation**
- **COVID-19** : 15 colonnes, données hétérogènes
- **MPOX** : 12 colonnes, structure différente
- **Cohérence** : Faible entre sources

#### **Après transformation**
- **Format unifié** : 12 colonnes identiques
- **Types cohérents** : datetime, string, float, BigInt
- **Référentiels** : Codes ISO, populations standardisés
- **Métriques** : Normalisées et comparables

### 7.3 Validation de la transformation

#### **Tests de cohérence**
- **Unicité** : Aucun doublon détecté
- **Complétude** : Valeurs critiques présentes
- **Types** : Conversions réussies
- **Référentiels** : Codes ISO valides

#### **Tests de qualité**
- **Normalisation** : Métriques par 100k calculées
- **Dérivés** : Incidence 7j et croissance calculées
- **Relations** : Jointures avec dimensions fonctionnelles

---

## Valeur ajoutée pour l'analyse

### 8.1 Comparabilité garantie

#### **Métriques harmonisées**
- **Même granularité** : Quotidienne par pays
- **Même normalisation** : Par 100k habitants
- **Mêmes indicateurs** : Cas et décès
- **Même période** : 2022-2024 pour comparaison

#### **Analyses possibles**
- **Comparaison directe** : COVID vs MPOX
- **Analyse temporelle** : Évolution des pandémies
- **Analyse géographique** : Impact par pays
- **Analyse de corrélation** : Relations entre indicateurs

### 8.2 Performance optimisée

#### **Structure optimisée**
- **Colonnes essentielles** : Suppression des redondances
- **Types appropriés** : Optimisation du stockage
- **Index suggérés** : date, country, indicator
- **Partitionnement** : Par année pour gros volumes

#### **Requêtes optimisées**
- **Jointures** : Codes ISO pour performance
- **Agrégations** : Métriques pré-calculées
- **Filtres** : Index sur colonnes fréquentes

---

## Conclusion

La transformation et le nettoyage ont créé un **modèle de données unifié et optimisé** :

1. **Harmonisation réussie** : Deux sources hétérogènes → un format unifié
2. **Qualité garantie** : Nettoyage, validation, enrichissement
3. **Comparabilité** : Métriques normalisées et cohérentes
4. **Performance** : Structure optimisée pour l'analyse
5. **Extensibilité** : Modèle prêt pour de nouvelles sources

Cette étape transforme les **données brutes** en **données analytiques** prêtes pour le chargement en base et l'analyse comparative des pandémies COVID-19 et MPOX.