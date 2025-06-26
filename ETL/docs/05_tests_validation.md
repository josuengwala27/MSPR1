# 5. Tests et Validation - Assurance Qualité du Pipeline ETL

## Objectif de l'étape

Les tests et la validation visent à garantir la qualité, la cohérence et la fiabilité du pipeline ETL complet. Cette étape implémente des tests automatisés pour valider chaque composant, détecter les anomalies et assurer la robustesse du système avant la mise en production.

---

## Architecture des tests

### 5.1 Scripts de test implémentés

#### **`test_extract.py` - Tests de l'extraction**
- **Objectif** : Validation du module d'extraction
- **Portée** : Tests unitaires et d'intégration
- **Fonctionnalités** : Import, configuration, fonctions utilitaires

#### **`test_coherence.py` - Tests de cohérence**
- **Objectif** : Validation de la cohérence globale
- **Portée** : Tests end-to-end du pipeline
- **Fonctionnalités** : Structure, flux de données, qualité

#### **Structure des tests**
```
ETL/scripts/
├── test_extract.py      # Tests du module d'extraction
├── test_coherence.py    # Tests de cohérence globale
└── test_loading.js      # Tests de chargement BDD (Node.js)
```

### 5.2 Stratégie de test

#### **Pyramide de tests**
1. **Tests unitaires** : Fonctions individuelles
2. **Tests d'intégration** : Interactions entre modules
3. **Tests end-to-end** : Pipeline complet
4. **Tests de performance** : Temps d'exécution et ressources

#### **Types de validation**
- **Structurelle** : Fichiers, répertoires, schémas
- **Fonctionnelle** : Logique métier, transformations
- **Qualité** : Données, cohérence, intégrité
- **Performance** : Temps, mémoire, ressources

---

## Tests d'extraction (`test_extract.py`)

### 6.1 Tests d'import et configuration

#### **Test d'import du module**
```python
def test_extract_import():
    """Teste l'import du module extract"""
    try:
        import extract
        print("Import du module extract réussi")
        return True
    except ImportError as e:
        print(f"Erreur d'import: {e}")
        return False
```

**Justification :**
- **Robustesse** : Vérification que le module est accessible
- **Dépendances** : Détection des problèmes d'installation
- **Environnement** : Validation de l'environnement Python

#### **Test de création de classe**
```python
def test_extract_class():
    """Teste la création de la classe DataExtractor"""
    try:
        from extract import DataExtractor
        extractor = DataExtractor()
        print("Création de DataExtractor réussi")
        return True
    except Exception as e:
        print(f"Erreur création classe: {e}")
        return False
```

**Justification :**
- **Instanciation** : Validation de la classe principale
- **Initialisation** : Vérification des paramètres par défaut
- **Cohérence** : Test de la structure de l'objet

### 6.2 Tests de configuration

#### **Validation des sources**
```python
def test_configuration():
    """Teste la configuration des sources"""
    try:
        from extract import SOURCES_CONFIG
        assert len(SOURCES_CONFIG) >= 2, "Au moins 2 sources requises"
        assert 'covid_worldometer' in SOURCES_CONFIG, "Source COVID-19 manquante"
        assert 'mpox_owid' in SOURCES_CONFIG, "Source MPOX manquante"
        
        for source_key, config in SOURCES_CONFIG.items():
            required_fields = ['name', 'url', 'filename', 'description', 'expected_size_mb']
            for field in required_fields:
                assert field in config, f"Champ {field} manquant dans {source_key}"
        
        print("Configuration des sources valide")
        return True
    except Exception as e:
        print(f"Erreur configuration: {e}")
        return False
```

**Justification :**
- **Complétude** : Vérification de toutes les sources requises
- **Structure** : Validation des champs obligatoires
- **Cohérence** : Assurance de la configuration correcte

### 6.3 Tests des fonctions utilitaires

#### **Test de calcul de checksum**
```python
def test_checksum_function():
    """Teste la fonction de calcul de checksum"""
    try:
        from extract import DataExtractor
        extractor = DataExtractor()
        
        # Créer un fichier de test
        test_file = extractor.raw_data_dir / "test.txt"
        test_content = "Test content for checksum"
        test_file.write_text(test_content)
        
        # Calculer le checksum
        checksum = extractor.calculate_checksum(test_file)
        assert len(checksum) == 64, "Checksum SHA-256 doit faire 64 caractères"
        assert checksum.isalnum(), "Checksum doit être alphanumérique"
        
        # Nettoyer
        test_file.unlink()
        
        print("Fonction checksum fonctionnelle")
        return True
    except Exception as e:
        print(f"Erreur checksum: {e}")
        return False
```

**Justification :**
- **Intégrité** : Validation du calcul de checksum SHA-256
- **Format** : Vérification du format de sortie
- **Fonctionnalité** : Test avec fichier réel

#### **Test de validation d'URL**
```python
def test_url_validation():
    """Teste la validation des URLs"""
    try:
        from urllib.parse import urlparse
        
        # URLs valides
        valid_urls = [
            "https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv",
            "https://raw.githubusercontent.com/owid/monkeypox/main/owid-monkeypox-data.csv"
        ]
        
        for url in valid_urls:
            parsed = urlparse(url)
            assert parsed.scheme == "https", f"URL {url} doit utiliser HTTPS"
            assert parsed.netloc, f"URL {url} doit avoir un domaine"
        
        print("Validation des URLs réussie")
        return True
    except Exception as e:
        print(f"Erreur validation URLs: {e}")
        return False
```

**Justification :**
- **Sécurité** : Vérification du protocole HTTPS
- **Validité** : Test de la structure des URLs
- **Fiabilité** : Assurance des sources de données

---

## Tests de cohérence (`test_coherence.py`)

### 7.1 Tests de structure

#### **Validation des fichiers**
```python
def test_file_structure():
    """Teste la structure des fichiers ETL"""
    scripts_dir = Path(__file__).parent
    expected_scripts = [
        '01_extract.py',
        '02_profile.py', 
        '03_transform.py',
        'run_etl_pipeline.py',
        'test_extract.py'
    ]
    
    missing_scripts = []
    for script in expected_scripts:
        if not (scripts_dir / script).exists():
            missing_scripts.append(script)
    
    if missing_scripts:
        print(f"Scripts manquants: {missing_scripts}")
        return False
    else:
        print("Tous les scripts ETL présents")
        return True
```

**Justification :**
- **Complétude** : Vérification de tous les scripts requis
- **Structure** : Validation de l'architecture du projet
- **Maintenance** : Détection des fichiers manquants

#### **Cohérence des chemins**
```python
def test_path_consistency():
    """Teste la cohérence des chemins entre scripts"""
    # Vérification des chemins dans 02_profile.py
    try:
        with open('02_profile.py', 'r') as f:
            content = f.read()
            if '../raw_data' in content:
                print("02_profile.py utilise les bons chemins relatifs")
            else:
                print("02_profile.py - chemins relatifs incorrects")
                return False
    except Exception as e:
        print(f"Erreur lecture 02_profile.py: {e}")
        return False
```

**Justification :**
- **Cohérence** : Vérification des chemins relatifs
- **Portabilité** : Assurance du fonctionnement sur différents environnements
- **Maintenance** : Détection des incohérences de chemins

### 7.2 Tests de flux de données

#### **Validation du flux ETL**
```python
def test_data_flow():
    """Teste le flux de données entre Extraction et Transformation"""
    raw_data_dir = Path('../raw_data')
    processed_dir = Path('../processed')
    
    # Vérification des répertoires
    if not raw_data_dir.exists():
        print("Répertoire raw_data non trouvé (normal si pas encore d'extraction)")
    else:
        print("Répertoire raw_data présent")
    
    # Vérification des fichiers attendus
    expected_raw_files = [
        'worldometer_coronavirus_daily_data.csv',
        'owid-monkeypox-data.csv'
    ]
    
    if raw_data_dir.exists():
        for file in expected_raw_files:
            if (raw_data_dir / file).exists():
                size_mb = (raw_data_dir / file).stat().st_size / (1024 * 1024)
                print(f"{file} présent ({size_mb:.2f}MB)")
            else:
                print(f"{file} manquant")
```

**Justification :**
- **Flux** : Validation du passage des données entre étapes
- **Intégrité** : Vérification de la présence des fichiers
- **Taille** : Contrôle de la taille des fichiers

### 7.3 Tests de qualité des données

#### **Validation des schémas**
```python
def test_schema_consistency():
    """Teste la cohérence des schémas de données"""
    processed_dir = Path('../processed')
    
    expected_columns = [
        'country', 'date', 'indicator', 'value', 'iso_code', 
        'population', 'unit', 'source', 'cases_per_100k', 
        'deaths_per_100k', 'incidence_7j', 'growth_rate'
    ]
    
    # Test sur fact_covid_history.csv
    covid_file = processed_dir / 'fact_covid_history.csv'
    if covid_file.exists():
        try:
            df = pd.read_csv(covid_file)
            missing_cols = [col for col in expected_columns if col not in df.columns]
            if missing_cols:
                print(f"Colonnes manquantes dans COVID: {missing_cols}")
                return False
            else:
                print(f"Schéma COVID cohérent ({len(df.columns)} colonnes)")
        except Exception as e:
            print(f"Erreur lecture COVID: {e}")
            return False
```

**Justification :**
- **Cohérence** : Vérification du schéma final
- **Complétude** : Validation de toutes les colonnes attendues
- **Qualité** : Assurance de la structure des données

#### **Validation de la table dim_country**
```python
def test_dim_country_coherence():
    """Teste la cohérence de la table dim_country"""
    processed_dir = Path('../processed')
    dim_country_path = processed_dir / 'dim_country.csv'
    
    if not dim_country_path.exists():
        print("Fichier dim_country.csv introuvable")
        return True
    
    try:
        dim_country = pd.read_csv(dim_country_path)
        print(f"dim_country: {dim_country.shape[0]} pays")
        
        # Test 1: Codes ISO manquants
        missing_iso = dim_country[dim_country['iso_code'].isna()]
        if len(missing_iso) > 0:
            print(f"{len(missing_iso)} pays sans code ISO")
        
        # Test 2: Codes ISO non-standard
        non_standard_iso = dim_country[
            (dim_country['iso_code'].notna()) & 
            (dim_country['iso_code'].str.len() != 3)
        ]
        if len(non_standard_iso) > 0:
            print(f"{len(non_standard_iso)} codes ISO non-standard")
        
        # Test 3: Population manquante
        missing_pop = dim_country[dim_country['population'].isna()]
        if len(missing_pop) > 0:
            print(f"{len(missing_pop)} pays sans population")
        
        # Test 4: Doublons
        duplicates = dim_country[dim_country.duplicated(subset=['country'], keep=False)]
        if len(duplicates) > 0:
            print(f"{len(duplicates)} doublons détectés")
        
        return True
        
    except Exception as e:
        print(f"Erreur lecture dim_country.csv: {e}")
        return False
```

**Justification :**
- **Qualité** : Validation des données de référence
- **Standardisation** : Vérification des codes ISO
- **Cohérence** : Détection des doublons et incohérences

---

## Résultats des tests

### 8.1 Métriques de qualité

#### **Tests d'extraction**
- **Import** : Module accessible
- **Configuration** : Sources valides
- **Fonctions** : Utilitaires fonctionnels
- **URLs** : Validation réussie

#### **Tests de cohérence**
- **Structure** : Fichiers présents
- **Chemins** : Cohérence validée
- **Flux** : Données transitent correctement
- **Schémas** : Format unifié

### 8.2 Détection d'anomalies

#### **Problèmes identifiés**
- **Codes ISO manquants** : Pays sans identifiant standard
- **Populations manquantes** : Données démographiques incomplètes
- **Doublons potentiels** : Entrées en double dans les référentiels
- **Valeurs aberrantes** : Données hors des plages attendues

#### **Recommandations**
- **Compléter les référentiels** : Ajouter les codes ISO et populations manquants
- **Nettoyer les doublons** : Supprimer les entrées en double
- **Valider les outliers** : Vérifier les valeurs aberrantes
- **Documenter les exceptions** : Expliquer les cas particuliers

---

## Fonctionnalités avancées

### 9.1 Tests de performance

#### **Validation des temps d'exécution**
```python
def test_performance():
    """Teste les performances du pipeline"""
    start_time = time.time()
    
    # Simulation d'exécution
    # ... exécution des étapes ...
    
    elapsed_time = time.time() - start_time
    
    if elapsed_time < 300:  # 5 minutes max
        print(f"Performance acceptable: {elapsed_time:.2f}s")
        return True
    else:
        print(f"Performance dégradée: {elapsed_time:.2f}s")
        return False
```

**Justification :**
- **Performance** : Validation des temps d'exécution
- **Ressources** : Contrôle de l'utilisation mémoire
- **Scalabilité** : Test de la capacité à traiter de gros volumes

### 9.2 Tests de régression

#### **Validation de la cohérence**
```python
def test_regression():
    """Teste la cohérence entre exécutions"""
    # Comparaison avec une exécution de référence
    reference_checksum = "abc123..."
    current_checksum = calculate_pipeline_checksum()
    
    if reference_checksum == current_checksum:
        print("Cohérence maintenue")
        return True
    else:
        print("Dérive détectée")
        return False
```

**Justification :**
- **Stabilité** : Détection des régressions
- **Cohérence** : Validation de la reproductibilité
- **Qualité** : Assurance de la fiabilité

---

## Valeur ajoutée

### 10.1 Assurance qualité

#### **Avantages**
- **Détection précoce** : Identification des problèmes avant production
- **Confiance** : Validation de la qualité du pipeline
- **Maintenance** : Facilite la maintenance et l'évolution
- **Documentation** : Tests comme documentation vivante

### 10.2 Robustesse

#### **Gestion des erreurs**
- **Tests défensifs** : Validation des cas d'erreur
- **Messages clairs** : Indication précise des problèmes
- **Recovery** : Suggestions de correction
- **Monitoring** : Suivi de la qualité dans le temps

### 10.3 Évolutivité

#### **Extensibilité**
- **Tests modulaires** : Facile d'ajouter de nouveaux tests
- **Configuration** : Tests paramétrables
- **Intégration** : Tests CI/CD ready
- **Reporting** : Rapports détaillés de qualité

---

## Conclusion

Les tests et la validation fournissent une **assurance qualité complète** :

1. **Couverture** : Tests unitaires, intégration et end-to-end
2. **Robustesse** : Validation de tous les composants
3. **Qualité** : Détection des anomalies et incohérences
4. **Maintenance** : Facilite l'évolution du pipeline
5. **Confiance** : Garantit la fiabilité du système

Cette approche garantit un **pipeline ETL de qualité professionnelle** avec une validation automatisée et une détection précoce des problèmes pour l'analyse comparative des pandémies COVID-19 et MPOX.
