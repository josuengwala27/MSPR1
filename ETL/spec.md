Voici une feuille de route détaillée, étape par étape, pour concevoir et réaliser l’ETL complet de vos deux sources (COVID-19 et MPOX Monkeypox) en Python/Pandas. L’accent est mis sur la phase **T »Transform »** pour expliciter chaque transformation effectuée.

---

## 1. Préparation générale du projet

### 1.1. Mise en place de l’environnement de travail

1. **Créer un répertoire racine pour le projet**, par exemple :

   ```
   pandemic_etl/
     ├── raw_data/          # Contiendra les fichiers CSV/JSON bruts
     ├── staging/           # Tableaux intermédiaires après nettoyage
     ├── processed/         # Données prêtes à charger en base
     ├── logs/              # Fichiers de logs ETL (extractions, erreurs)
     ├── scripts/           # Scripts Python pour chaque étape ETL
     ├── notebooks/         # Jupyter notebooks de prototypage/profiling
     ├── docs/              # Documentation, descriptions des étapes
     ├── requirements.txt   # Liste des dépendances Python
     └── README.md          # Vue d’ensemble du projet
   ```
2. **Initialiser un environnement virtuel Python** (venv ou Conda) :

   * Installer au minimum les packages :

     * `pandas` (pour la manipulation de données)
     * `sqlalchemy` (pour l’insertion vers PostgreSQL)
     * `psycopg2-binary` (driver PostgreSQL)
     * `great_expectations` (ou un équivalent maison pour les contrôles qualité)
   * Lister ces dépendances dans `requirements.txt` pour pouvoir les réinstaller aisément.

### 1.2. Définition des conventions et outils annexes

1. **Convention de nommage** :

   * Fichiers bruts : `raw_data/covid19_global.csv`, `raw_data/mpox_monkeypox.json` (ou `.csv`).
   * Scripts :

     * `scripts/01_extract_covid.py`
     * `scripts/01_extract_mpox.py`
     * `scripts/02_transform_covid.py`
     * `scripts/02_transform_mpox.py`
     * `scripts/03_load.py`
   * Logs : `logs/etl_<date>_covid.log`, `logs/etl_<date>_mpox.log`.
2. **Gestion de version** :

   * Initialiser un dépôt Git à la racine (`git init`) et ajouter un `.gitignore` pour exclure les fichiers volumineux (fichiers bruts, logs, bases locales).
3. **Documentation initiale** :

   * Dans `docs/README.md`, décrire en quelques lignes l’objectif global et la structure d’arborescence exposée ci-dessus.

---

## 2. Choix et collecte des sources

### 2.1. Justification du choix des deux jeux de données

1. **Dataset COVID-19 global (Kaggle)** :

   * Volume historique important (plusieurs années).
   * Présence d’indicateurs variés : cas confirmés, décès, hospitalisations selon les pays.
   * Format CSV standard et mise à jour régulière.
2. **Dataset MPOX Monkeypox (Open Source ou Kaggle)** :

   * Permet de comparer deux pandémies différentes (virus respiratoire vs. virus à transmission par contact).
   * Présentation en CSV ou JSON selon la source officielle.
   * Volumes plus modestes mais schéma de données comparable pour les indicateurs.

> **Objectif :** disposer d’un jeu « COVID » pour illustrer des séries temporelles nationales et d’un jeu « MPOX » pour enrichir la comparaison.

### 2.2. Téléchargement manuel et organisation

1. **Télécharger manuellement les deux fichiers** :

   * Aller sur la page Kaggle ou GitHub correspondante pour le dataset COVID-19 :

     * Télécharger le fichier `covid19_global.csv` (ou `covid19_global.json` si disponible).
   * Aller sur la source MPOX (Kaggle, GitHub ou API officielle) pour récupérer `mpox_monkeypox.csv` ou `.json`.
2. **Placer les fichiers bruts dans `raw_data/`** :

   ```
   raw_data/
     ├── covid19_global.csv
     └── mpox_monkeypox.json   (ou .csv)
   ```
3. **Vérifier la taille des fichiers** :

   * S’assurer qu’ils ne dépassent pas plusieurs centaines de mégaoctets.
   * Si trop volumineux, envisager un découpage initial (mais pour l’instant on part du principe qu’ils tiennent en mémoire).

---

## 3. Phase E »Extract »

> Dans cette étape, l’objectif est d’« extraire » les fichiers bruts depuis `raw_data/`, de vérifier leur intégrité et de les charger dans des DataFrames Pandas pour inspection.

### 3.1. Validation des sources brutes

1. **Vérifier l’intégrité des fichiers** :

   * S’assurer que les fichiers CSV/JSON ne sont pas corrompus :

     * Ouvrir rapidement avec un éditeur de texte pour repérer erreurs visibles (ligne incomplète, fin prématurée).
     * Vérifier qu’il y a bien un header clair (noms de colonnes).
2. **Relevé des schémas initiaux** (profilage rapide) dans un notebook :

   * Charger 100 000 premières lignes de chaque fichier (via `pd.read_csv(…, nrows=100000)` ou `pd.read_json(…, lines=True, nrows=100000)`).
   * Examiner les colonnes détectées, leur type « brut », et relever les principales différences de schéma entre les deux fichiers (noms, types, formats de date).

### 3.2. Copie des données dans `staging/` (optionnel)

1. **Créer une copie initiale** des fichiers :

   * Pour garder intact le dossier `raw_data/`, effectuer un copier :

     ```
     cp raw_data/covid19_global.csv staging/covid19_raw.csv
     cp raw_data/mpox_monkeypox.json staging/mpox_raw.json
     ```
   * L’idée est de travailler dans `staging/`, en laissant la source « immuable » dans `raw_data/`.

---

## 4. Phase T »Transform »

> C’est ici que l’essentiel du travail réside : chaque étape de transformation, nettoyage et enrichissement doit être minutieusement planifiée.

### 4.1. Chargement initial dans des DataFrames

1. **Script ou notebook de prototypage** (`notebooks/profiling_etl.ipynb`) :

   * Charger la totalité des données brutes pour explorer le contenu de manière interactive.
   * Examiner un aperçu (`df.head()`), la forme (`df.shape`), et quelques statistiques descriptives (`df.describe()`).
   * Relever les colonnes pertinentes pour l’analyse (pays, date, indicateur, valeur, etc.).

2. **Créer deux DataFrames de base** :

   * `df_covid_raw` : lecture de `staging/covid19_raw.csv`.
   * `df_mpox_raw` : lecture de `staging/mpox_raw.json` (ou `.csv`).
   * S’assurer que ces deux DataFrames contiennent au minimum les colonnes :

     * **pays** (ou `country_region`),
     * **date**,
     * **type d’indicateur** (ex : `cases`, `deaths`, `recoveries`),
     * **valeur numérique** (nombre de cas, etc.).

### 4.2. Profilage et diagnostic préliminaire

1. **Lister les colonnes de chaque DataFrame** et leur type détecté par Pandas (via `df.dtypes`) ; noter les différences :

   * Par exemple, `df_covid_raw` a peut-être une colonne `Province/State` que `df_mpox_raw` n’a pas.
   * Vérifier si la colonne « date » est déjà un type datetime ou un simple string.

2. **Compter les valeurs manquantes** par colonne (`df.isna().sum()`) :

   * Relever le pourcentage d’enregistrements manquants dans chaque colonne critique (pays, date, indicateur, valeur).
   * Prioriser les colonnes où un faible pourcentage de données manquantes peut être imputé, et celles où un taux élevé peut conduire à la suppression de lignes.

3. **Statistiques élémentaires sur les indicateurs** :

   * Pour chaque valeur de la colonne « indicator », afficher la distribution (nombre de lignes, min, max, moyenne, quartiles).
   * Identifier d’éventuels outliers (valeurs négatives, valeurs aberrantes > 10 millions de cas, etc.).

4. **Identification des doublons potentiels** :

   * Déterminer quelles colonnes constituent la clé composite : souvent `(pays, date, indicator)`.
   * Calculer le nombre de duplicata sur cette clé :

     ```
     nombre_total = len(df)
     nombre_unique = df.drop_duplicates(subset=['pays','date','indicator']).shape[0]
     doublons = nombre_total - nombre_unique
     ```
   * Si doublons > 0, noter la proportion et réfléchir à la manière de les traiter.

> À l’issue de ce diagnostic, vous aurez une vision claire des étapes de nettoyage à appliquer.

---

### 4.3. Standardisation des schémas

L’objectif est d’obtenir, pour **les deux** DataFrames, un *schéma harmonisé* :

1. **Uniformiser les noms de colonnes** :

   * Définir une liste cible de colonnes communes, par exemple :

     ```
     ['country', 'date', 'indicator', 'value', 'population', 'unit']
     ```
   * Pour `df_covid_raw` et `df_mpox_raw`, prévoir un mapping :

     * Exemple pour COVID :

       * `Country/Region` → `country`
       * `Date` (format `YYYY-MM-DD`) → `date`
       * `Confirmed` → `cases` (à renommer ensuite en `value` avec un champ `indicator=’cases’`)
       * `Deaths` → `deaths` (idem)
     * Exemple pour MPOX :

       * `location` → `country`
       * `report_date` → `date`
       * `new_cases` → `value` (avec `indicator=’cases’`)
       * `new_deaths` → créer un second enregistrement ou gérer deux DataFrames si nécessaire
   * **Action** : dans `scripts/02_transform_covid.py`, écrire une fonction `standardize_columns(df, mapping_dict)` qui renomme systématiquement.
   * **Résultat attendu** : à l’issue, `df_covid_std` et `df_mpox_std` partagent exactement les mêmes noms de colonnes pour les champs de base.

2. **Conversion des types de champs** :

   * **Colonnes `date`** :

     * Utiliser `pd.to_datetime(df['date'], format=...)` pour transformer en `datetime64[ns]`.
     * Vérifier l’uniformité du format (ex. : certains fichiers contiennent `MM/DD/YYYY`, d’autres `YYYY-MM-DD`).
   * **Colonnes numériques (`value`, `population`, …)** :

     * Transformer en type `float` ou `int` selon le cas (`df['value'] = df['value'].astype(float)`).
   * **Colonnes catégorielles (`country`, `indicator`, `unit`)** :

     * S’assurer que ce sont des strings sans espaces parasites (ex. supprimer les espaces en début/fin, uniformiser la casse avec `.str.strip().str.lower()`).

3. **Ajout de colonnes manquantes obligatoires** :

   * Si l’une des sources ne fournit pas la colonne « population » pour chaque pays, créer une table de référence ou ajouter une colonne vide (à remplir ultérieurement lors de l’enrichissement).
   * Si l’une des sources n’a pas de champ `unit`, ajouter ensuite une colonne par défaut (ex. `cases` → `unit = 'count'`).

> À l’issue de cette étape, vous devez avoir deux DataFrames `df_covid_std` et `df_mpox_std` possédant exactement les mêmes colonnes :
>
> ```
> ['country', 'date', 'indicator', 'value', 'population', 'unit']
> ```

---

### 4.4. Suppression des doublons

1. **Définir la clé composite** pour l’unicité :

   * Généralement : `(country, date, indicator)`.
   * Confirmer qu’il n’y a pas d’autres colonnes importantes à intégrer (ex. : si pour MPOX il existe une colonne `region_state`, l’intégrer à la clé si nécessaire).

2. **Filtrer les duplicata** :

   * Pour chaque DataFrame standardisé (`df_covid_std`, `df_mpox_std`), exécuter :

     * `df = df.drop_duplicates(subset=['country','date','indicator'], keep='last')`
   * Si plusieurs lignes partagent la même triple `(country, date, indicator)` mais avec des valeurs différentes, définir la stratégie :

     * **Garder la valeur la plus récente** (si un champ `last_updated` existe),
     * **Garder la valeur moyenne** (rarement recommandé),
     * **Arbitrer manuellement** si peu de cas (noter dans la doc).

3. **Vérifier qu’il ne reste plus de doublons** :

   * Réexécuter le comptage de doublons pour s’assurer que `nombre_total = nombre_unique`.
   * Enregistrer un rapport sommaire dans `logs/etl_<date>_covid.log` (ex. « Suppression de 120 doublons, 0 doublons restants »).

---

### 4.5. Gestion des valeurs manquantes

1. **Quantifier le nombre et le pourcentage de valeurs vides** (NaN) pour chaque colonne clé (`country`, `date`, `indicator`, `value`, `population`) :

   * Ex. :

     ```
     taux_na = df.isna().mean() * 100
     ```
   * Documenter dans `docs/missing_values_report.md` les pourcentages relevés (sous forme de tableau).

2. **Traiter les colonnes essentielles** :

   * **`country` ou `date` vide** :

     * Si la date est manquante, on ne peut pas utiliser la ligne → **supprimer la ligne** (ajouter un log « Suppression X lignes, date manquante »).
     * Si le pays est manquant, envisager de déduire le pays depuis une colonne proche (ex. si `province_state` = « New York », attribuer `country = 'USA'`), sinon supprimer.
   * **`indicator` vide** :

     * Si un enregistrement n’a pas de type d’indicateur, on ne peut pas décider si c’est un cas, un décès, etc. → supprimer, ou marquer dans une colonne `to_review = True` pour tri manuel.
   * **`value` manquant** :

     * Deux stratégies possibles :

       1. **Imputation par interpolation linéaire temporelle** :

          * Regrouper par `(country, indicator)`, trier par date, puis appliquer `.interpolate(method='linear')`.
          * Ex. : si le 3 avril il manque la valeur, et que le 2 avril on a 50 cas et le 4 avril 70 cas → imputer 60 cas pour le 3 avril.
       2. **Imputation par moyenne glissante (rolling average)** :

          * Au sein de chaque groupe `(country, indicator)`, calculer une moyenne sur les 7 jours précédents (si disponibles) et substituer.
          * Faire très attention aux tout premiers jours (pas assez de points pour la moyenne glissante).
     * Si le pourcentage de valeurs manquantes pour `(country, indicator)` dépasse un seuil critique (ex. 20 %), on peut décider de **supprimer la série temporelle entière** pour ce couple – mais documenter cette décision.
   * **`population` manquant** :

     * Si pour un pays la population n’est pas renseignée, aller chercher une source externe (par ex. Banque mondiale) et créer un fichier référence `docs/country_population_reference.csv` à charger manuellement.
     * Remplir les valeurs manquantes via un mapping manuel (ex. `{'France': 67390000, 'Germany': 83190000, …}`).
   * **Autres colonnes éventuelles (ex. `unit`)** :

     * Si `unit` est manquant, on peut créer une valeur par défaut selon `indicator` (ex. `cases` → `'count'`, `rate` → `'per_100k'`, etc.).

3. **Enregistrer un rapport d’imputation** :

   * Dans `docs/imputation_report.md`, décrire pour chaque colonne la méthode utilisée (interpolation vs moyenne roulante), les seuils, et le pourcentage de lignes modifiées.
   * Mettre une section « Lignes supprimées » pour lister les raisons (date manquante, pays manquant, indicateur manquant, trop de NaN).

---

### 4.6. Normalisation des valeurs

1. **Harmonisation des unités** :

   * Dans `df_covid_std`, si les colonnes `cases`, `deaths` sont en « nombre brut », décider si l’on souhaite également générer une colonne normalisée « cases\_per\_100k » :

     * Calcul : `(value / population) * 100_000`.
     * Créer une nouvelle colonne `value_normalized = (df['value'] / df['population']) * 100000` pour chaque groupe `(country, date)`, en explicitant le choix dans `docs/normalization_rules.md`.
   * Dans `df_mpox_std`, faire de même si on a accès à la population par pays :

     * Même calcul pour `cases_per_100k` ou `deaths_per_100k`.

2. **Uniformisation des libellés d’indicateurs** :

   * Si, par exemple, COVID-19 utilise `confirmed` et `deaths`, et MPOX utilise `new_cases` et `new_deaths` :

     * Créer une table de correspondance (mapping) `indicator_mapping = {'Confirmed':'cases', 'Deaths':'deaths', 'new_cases':'cases', 'new_deaths':'deaths'}`.
     * Remplacer systématiquement la colonne `indicator` par le schéma commun (`'cases'` ou `'deaths'`).

3. **Vérification des plages de valeurs autorisées** :

   * Pour chaque `(country, indicator)`, s’assurer que `value >= 0`.
   * Pour les taux calculés (`cases_per_100k`, etc.), vérifier qu’ils restent dans une fourchette logiquement cohérente (ex. `0 ≤ rate ≤ 100 000`).
   * Documenter toute anomalie détectée (ex. un pays avec 10 000 000 cas sur un jour pour une population de 100 000 000 → taux de 10 %) : valider si c’est plausible ou erreur de saisie.

4. **Gestion des outliers et correction** :

   * Détecter des sauts très brusques (ex. +10 000 cas en un jour pour un petit pays) :

     * Pour chaque `(country, indicator)`, calculer la différence absolue par rapport à la journée précédente (`diff = value_t - value_{t-1}`).
     * Si `diff` excède un seuil défini (ex. 3 × écart-type ou un multiple fixe, à déterminer), marquer la ligne comme potentiellement erronée.
   * Deux approches :

     1. **Imputation** : remplacer la valeur anormale par la moyenne des deux jours voisins.
     2. **Flag** : créer une colonne `anomaly = True` et laisser la valeur, puis exclure ces lignes du chargement final.

---

### 4.7. Enrichissement des données

1. **Ajout systématique du code ISO pays** :

   * Créer un fichier local `docs/iso_country_codes.csv` avec deux colonnes : `country_name`, `iso_code` (ISO 3166-1 alpha 3).
   * Dans le script, charger cette table (via `pd.read_csv`) et faire un merge :

     ```
     df = df.merge(iso_df, how='left', left_on='country', right_on='country_name')
     ```
   * Si `iso_code` est manquant pour certains pays (ex. noms alternatifs, pays récents), corriger manuellement dans `iso_country_codes.csv`.

2. **Création d’attributs dérivés** :

   * **Incidence à 7 jours** :

     * Pour chaque `(country, indicator)`, trier par date et calculer :

       ```
       df['incidence_7j'] = df.groupby(['country','indicator'])['value'].transform(lambda x: x.rolling(window=7).sum())
       ```
     * Expliciter dans un document `docs/derived_metrics.md` la logique (pourquoi la fenêtre de 7 jours, etc.).
   * **Taux de croissance quotidien** :

     * Définir `df['growth_rate'] = df.groupby(['country','indicator'])['value'].pct_change()`.
     * Attention aux divisions par zéro (ajouter une condition pour éviter l’infini).

3. **Identification des périodes clés** (optionnel) :

   * Détecter les « pics » (jours où `growth_rate` est maximal) et ajouter une colonne booléenne `is_peak_day`.
   * Documenter cette détection dans le même fichier `derived_metrics.md`.

---

### 4.8. Tri, ordonnancement et création de tableaux intermédiaires

1. **Trier les enregistrements** :

   * Avant le chargement, on veut que toutes les données soient triées par `(country, indicator, date)` pour faciliter un chargement séquentiel en base.
   * Exemple :

     ```
     df = df.sort_values(by=['country','indicator','date'])
     ```

2. **Création de tables de dimension** (pour la phase L) :

   * **Table `dim_country`** : extraire la liste unique de pays, leurs codes ISO, population, région (si disponible).
   * **Table `dim_indicator`** : lister les indicateurs possibles (`cases`, `deaths`, éventuellement `recoveries`, etc.) et fournir une description courte.
   * **Table `dim_date`** (optionnel, si vous souhaitez dénormaliser) : lister toutes les dates de la plage couverte (utile pour certaines analyses OLAP).

3. **Séparation en sous-jeux de données** :

   * Créer une copie de travail `df_covid_processed.csv` et `df_mpox_processed.csv` dans `processed/` qui contiendront uniquement les colonnes finales à charger :

     ```
     processed/
       ├── dim_country.csv
       ├── dim_indicator.csv
       ├── fact_covid_history.csv
       └── fact_mpox_history.csv
     ```
   * Pour chaque « fact\_\*.csv », ne conserver que les colonnes destinées à la table `DonnéeHistorique` (voir modèle de base) :

     ```
     ['country', 'iso_code', 'date', 'indicator', 'value', 'incidence_7j', 'growth_rate']
     ```

---

## 5. Phase L »Load »

> Dans cette étape, on charge les jeux de données transformés dans la base PostgreSQL destinée au datalake analytique.

### 5.1. Préparation de la base de données

1. **Déployer un conteneur PostgreSQL (optionnel)** ou installer localement :

   * Définir une base `oms_db` et un utilisateur dédié (ex. `etl_user` avec mot de passe sécurisé).
   * Créer un schéma `public` ou dédié `pandemic_etl`.

2. **Créer les tables de dimension** (`dim_country`, `dim_indicator`) et la table de faits (`DonnéeHistorique`) selon le modèle suivant :

   ```sql
   -- Table dim_country
   CREATE TABLE dim_country (
     id_country SERIAL PRIMARY KEY,
     country_name TEXT NOT NULL UNIQUE,
     iso_code CHAR(3) NOT NULL UNIQUE,
     population BIGINT
   );

   -- Table dim_indicator
   CREATE TABLE dim_indicator (
     id_indicator SERIAL PRIMARY KEY,
     indicator_name TEXT NOT NULL UNIQUE,
     description TEXT
   );

   -- Table DonnéeHistorique (fact table)
   CREATE TABLE DonnéeHistorique (
     id_donnee SERIAL PRIMARY KEY,
     id_country INT REFERENCES dim_country(id_country),
     id_indicator INT REFERENCES dim_indicator(id_indicator),
     date DATE NOT NULL,
     value DOUBLE PRECISION,
     incidence_7j DOUBLE PRECISION,
     growth_rate DOUBLE PRECISION,
     CONSTRAINT uq_history UNIQUE (id_country, id_indicator, date)
   );
   ```

3. **Configurer les index** pour accélérer les requêtes analytiques :

   ```sql
   CREATE INDEX idx_history_country_date ON DonnéeHistorique (id_country, date);
   CREATE INDEX idx_history_indicator_date ON DonnéeHistorique (id_indicator, date);
   ```

4. **Créer une table de logs ETL** pour tracer chaque exécution :

   ```sql
   CREATE TABLE LogETL (
     id_log SERIAL PRIMARY KEY,
     source_name TEXT NOT NULL,           -- 'covid' ou 'mpox'
     execution_date TIMESTAMP NOT NULL DEFAULT NOW(),
     status TEXT NOT NULL,                -- 'STARTED', 'SUCCESS', 'FAILED'
     message TEXT,
     row_count INT,                       -- nombre de lignes insérées
     duration_sec INT                     -- durée d’exécution
   );
   ```

### 5.2. Chargement des dimensions

1. **Dim\_country** :

   * Charger depuis `processed/dim_country.csv` :

     * Chaque ligne contient `country_name`, `iso_code`, `population`.
     * Si une ligne existe déjà (même `iso_code`), faire un `ON CONFLICT (iso_code) DO UPDATE SET population = EXCLUDED.population`.

2. **Dim\_indicator** :

   * Charger depuis `processed/dim_indicator.csv` :

     * Chaque ligne contient `indicator_name`, `description`.
     * Méthode similaire pour gérer d’éventuels doublons (même `indicator_name`).

3. **Logs de chargement** :

   * Insérer un enregistrement `LogETL(source_name='dim_country', status='STARTED', message=NULL)` au début, puis mettre à jour en `SUCCESS` ou `FAILED` à la fin.

### 5.3. Chargement des faits (DonnéeHistorique)

1. **Vérifier l’ordre de chargement** :

   * Charger d’abord les `dim_country` et `dim_indicator` pour que les clés étrangères soient résolues.
   * Ensuite, charger les faits `fact_covid_history.csv` puis `fact_mpox_history.csv`.

2. **Insertion par batch** (pour éviter les timeouts) :

   * Lire `fact_*.csv` par morceaux (chunks de 100 000 lignes si volumineux) :

     * Pour chaque chunk, faire un `df_chunk.to_sql('DonnéeHistorique', engine, if_exists='append', index=False)` via SQLAlchemy.
   * Utiliser un paramètre `if_exists='append'`, mais déclencher un contrôle d’unicité (clé unique) pour ne pas réinjecter des doublons si le script est relancé.

3. **Vérification post-chargement** :

   * Avant et après chaque insertion, interroger PostgreSQL pour obtenir le nombre de lignes dans `DonnéeHistorique` et vérifier la croissance attendue.
   * Exemple :

     ```
     SELECT COUNT(*) FROM DonnéeHistorique WHERE id_country = (SELECT id_country FROM dim_country WHERE iso_code='FRA') AND id_indicator = (SELECT id_indicator FROM dim_indicator WHERE indicator_name='cases');
     ```
   * Consigner ces chiffres dans `LogETL`.

4. **Gestion des erreurs pendant le chargement** :

   * Si une ligne déclenche une erreur (violations de contraintes, type invalide), consigner la ligne fautive dans un fichier `logs/failed_rows_covid.csv` (ou `mpox`) pour enquête ultérieure.
   * Mettre à jour `LogETL` avec le message d’erreur détaillé (`message = 'Unique constraint violation on (id_country, id_indicator, date) for iso_code=…'`).

---

## 6. Logging et suivi des erreurs

### 6.1. Fichier de log local

1. **Configurations de logging Python** (dans chaque script) :

   * Créer un logger avec `logging.getLogger(__name__)`.
   * Configurer un `FileHandler` pointant vers `logs/etl_<date>_<source>.log`.
   * Exemple (en pseudocode) :

     ```
     logger = logging.getLogger('etl_logger')
     handler = FileHandler(f'logs/etl_{YYYYMMDD}_covid.log')
     handler.setFormatter(Formatter('%(asctime)s - %(levelname)s - %(message)s'))
     logger.addHandler(handler)
     logger.setLevel(INFO)
     ```
   * Enregistrer systématiquement :

     * Début du script : `logger.info("Début ETL COVID")`.
     * Fin réussie : `logger.info("Fin ETL COVID – X lignes chargées en Y secondes")`.
     * En cas d’exception : `logger.exception("Erreur inattendue lors du traitement COVID")`.

2. **Table `LogETL` dans PostgreSQL** :

   * À chaque étape majeure (extraction, transformation, chargement), insérer ou mettre à jour un enregistrement dans `LogETL` avec le statut courant.

### 6.2. Gestion des erreurs critiques

1. **Extraction** :

   * Si le fichier brut n’existe pas dans `raw_data/`, logger une erreur fatale et *stopper* l’exécution (raise Exception).
2. **Transformation** :

   * Capturer toute exception dans la transformation (ex. `ValueError` lors de la conversion en datetime) et noter la ligne fautive.
   * Si trop d’erreurs (ex. plus de 5 % des lignes posent problème), arrêter pour correction manuelle.
3. **Chargement** :

   * Pour chaque chunk inséré, entourer d’un `try/except` pour logger les erreurs liées à la base (contraintes, timeouts).
   * Continuer l’insertion des autres chunks même en cas d’erreur, mais *mettre à jour* le statut global : `status='FAILED'` dans `LogETL`.

---

## 7. Automatisation de l’ETL

### 7.1. Script maître ETL

1. **Créer un script d’orchestration** (`scripts/run_etl.py`) qui appelle dans l’ordre :

   1. `scripts/01_extract_covid.py`
   2. `scripts/02_transform_covid.py`
   3. `scripts/01_extract_mpox.py`
   4. `scripts/02_transform_mpox.py`
   5. `scripts/03_load.py`

2. **Arguments et options** :

   * Le script principal peut accepter un argument `--source` pour ne lancer que « covid » ou « mpox » ou « both ».
   * Possibilité d’ajouter un flag `--dry-run` pour juste exécuter le « profiling » sans charger en base.

3. **Chronométrage global** :

   * Au tout début, capter l’heure (`start_time = datetime.now()`), et à la fin calculer la durée totale.
   * Logger la durée dans le `LogETL` (enregistrement global, par exemple `source_name='all', status='SUCCESS', duration_sec = (now–start).seconds`).

### 7.2. Planification avec cron (ou Airflow)

1. **Cron (simple)** :

   * Ouvrir le crontab de l’utilisateur et ajouter :

     ```
     0 2 * * * cd /chemin/vers/pandemic_etl && /chemin/vers/venv/bin/python run_etl.py --source both >> logs/cron_etl.log 2>&1
     ```

     * Exécution quotidienne à 2 h du matin – adapter selon les besoins.
   * Rediriger la sortie standard et d’erreur vers `logs/cron_etl.log` pour conserver une trace.

2. **Airflow (plus robuste)** :

   * Installer Apache Airflow et configurer un DAG `pandemic_etl_dag.py` qui définit trois tâches :

     1. `extract_transform_covid` (en tant que `PythonOperator` appelant le module `scripts/02_transform_covid.py`)
     2. `extract_transform_mpox`
     3. `load_fact_tables`
   * Définir l’ordre (`extract_transform_covid >> extract_transform_mpox >> load_fact_tables`).
   * Configurer des alertes par email ou Slack en cas d’échec d’une tâche (via `on_failure_callback`).

---

## 8. Documentation et versionnement

### 8.1. Documentation utilisateur

1. **README.md** (à la racine) :

   * Présentation générale du projet.
   * Prérequis (version Python, packages à installer, accès à PostgreSQL).
   * Structure des répertoires.
   * Mode d’emploi pour lancer l’ETL manuellement ou via cron.

2. **docs/etl\_steps.md** :

   * Détail de chaque étape (extraction, transformation, chargement) avec les commandes à exécuter.
   * Explication des choix de design (pourquoi telle méthode d’imputation, pourquoi tel seuil d’anomalie, etc.).

3. **docs/schema\_database.md** :

   * Diagramme UML ou Merise des tables créées (`dim_country`, `dim_indicator`, `DonnéeHistorique`, `LogETL`).
   * Liste des champs, types SQL et contraintes (PK, FK, unique).

4. **docs/derived\_metrics.md** :

   * Définition claire des métriques calculées (incidence\_7j, growth\_rate).
   * Formules utilisées et justification.

5. **docs/missing\_values\_report.md** :

   * Pourcentage de valeurs manquantes par colonne, pour chaque source.
   * Stratégies appliquées (interpolation, rolling, suppression).

6. **docs/normalization\_rules.md** :

   * Méthode et formules pour normaliser les valeurs (`per_100k`, etc.).

### 8.2. Suivi des versions de scripts

1. **Branching Git** :

   * Créer une branche `dev` pour le développement actif.
   * Une fois la feuille de route validée, fusionner dans `main`.
   * Pour toute modification ultérieure (ex. ajout d’un nouveau dataset), créer une branche spécifique (`feature/new_source_xyz`).

2. **Tagging** :

   * Lorsqu’une version complète de l’ETL est fonctionnelle (tous les scripts validés), taguer `v1.0.0`.
   * À chaque évolution majeure (ajout d’une nouvelle source, refonte du transform), taguer `v2.0.0` puis passer à `v2.1.0` pour petits correctifs.

---

## 9. Récapitulatif de la feuille de route

1. **Initialisation du projet**

   * Création de l’arborescence, environnement virtuel, installation des dépendances, dépôt Git.
   * Rédaction initiale du `README.md` et description sommaire.

2. **Collecte (Extract)**

   * Choix des deux sources (COVID-19, MPOX).
   * Téléchargement manuel et dépôt dans `raw_data/`.
   * Vérification d’intégrité et profiling initial pour comprendre le schéma.

3. **Transformation (Transform)**

   * **Standardisation des schémas** : uniformiser noms de colonnes, types de données (dates, numériques, textes).
   * **Suppression des doublons** : définition de la clé composite, éliminer les lignes redondantes ou incohérentes.
   * **Gestion des valeurs manquantes** : analyse des pourcentages, choix des méthodes d’imputation ou suppression, mise à jour de la doc.
   * **Normalisation** : calcul de `cases_per_100k`, conversion des unités, détection et traitement des outliers.
   * **Enrichissement** : ajout des codes ISO pays (via un fichier de référence), calcul d’attributs dérivés (incidence 7 jours, growth rate).
   * **Tri et création de tables intermédiaires** : tri par `(country, indicator, date)`, constitution des fichiers finals dans `processed/` (dimensions et faits).

4. **Chargement (Load)**

   * Création préalable du schéma PostgreSQL (tables de dimension, table `DonnéeHistorique`, table de logs).
   * Chargement successif des dimensions (`dim_country`, `dim_indicator`) avec gestion des conflits.
   * Chargement des faits par batch, vérifications post-chargement, gestion d’erreurs sur les clés uniques.
   * Mise à jour de la table `LogETL` pour tracer l’état global et par source.

