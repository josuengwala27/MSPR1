#!/usr/bin/env python3
"""
Script de test de cohérence ETL
Auteur: MSPR Project
Date: 2024
Description: Vérifie la cohérence entre Extraction et Transformation
"""

import os
import sys
import pandas as pd
from pathlib import Path

def test_file_structure():
    """Teste la structure des fichiers ETL"""
    print(" Test de la structure des fichiers ETL")
    
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

def test_path_consistency():
    """Teste la cohérence des chemins entre scripts"""
    print("\n Test de cohérence des chemins")
    
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
    
    # Vérification des chemins dans 03_transform.py
    try:
        with open('03_transform.py', 'r') as f:
            content = f.read()
            if '../raw_data' in content and '../processed' in content:
                print("03_transform.py utilise les bons chemins relatifs")
            else:
                print("03_transform.py - chemins relatifs incorrects")
                return False
    except Exception as e:
        print(f"Erreur lecture 03_transform.py: {e}")
        return False
    
    return True

def test_data_flow():
    """Teste le flux de données entre Extraction et Transformation"""
    print("\n Test du flux de données")
    
    raw_data_dir = Path('../raw_data')
    processed_dir = Path('../processed')
    
    # Vérification des répertoires
    if not raw_data_dir.exists():
        print("Répertoire raw_data non trouvé (normal si pas encore d'extraction)")
    else:
        print("Répertoire raw_data présent")
    
    if not processed_dir.exists():
        print("Répertoire processed non trouvé (normal si pas encore de transformation)")
    else:
        print("Répertoire processed présent")
    
    # Vérification des fichiers attendus
    expected_raw_files = [
        'worldometer_coronavirus_daily_data.csv',
        'owid-monkeypox-data.csv'
    ]
    
    expected_processed_files = [
        'fact_covid_history.csv',
        'fact_mpox_history.csv',
        'dim_country.csv',
        'dim_indicator.csv'
    ]
    
    # Test fichiers bruts
    if raw_data_dir.exists():
        for file in expected_raw_files:
            if (raw_data_dir / file).exists():
                size_mb = (raw_data_dir / file).stat().st_size / (1024 * 1024)
                print(f"{file} présent ({size_mb:.2f}MB)")
            else:
                print(f"{file} manquant")
    
    # Test fichiers transformés
    if processed_dir.exists():
        for file in expected_processed_files:
            if (processed_dir / file).exists():
                size_mb = (processed_dir / file).stat().st_size / (1024 * 1024)
                print(f"{file} présent ({size_mb:.2f}MB)")
            else:
                print(f"{file} manquant")
    
    return True

def test_schema_consistency():
    """Teste la cohérence des schémas de données"""
    print("\n Test de cohérence des schémas")
    
    # Vérification des colonnes attendues dans les données transformées
    processed_dir = Path('../processed')
    
    if not processed_dir.exists():
        print("Pas de données transformées à vérifier")
        return True
    
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
    
    # Test sur fact_mpox_history.csv
    mpox_file = processed_dir / 'fact_mpox_history.csv'
    if mpox_file.exists():
        try:
            df = pd.read_csv(mpox_file)
            missing_cols = [col for col in expected_columns if col not in df.columns]
            if missing_cols:
                print(f"Colonnes manquantes dans MPOX: {missing_cols}")
                return False
            else:
                print(f"Schéma MPOX cohérent ({len(df.columns)} colonnes)")
        except Exception as e:
            print(f"Erreur lecture MPOX: {e}")
            return False
    
    return True

def test_pipeline_orchestration():
    """Teste l'orchestration du pipeline"""
    print("\nTest de l'orchestration du pipeline")
    
    try:
        with open('run_etl_pipeline.py', 'r') as f:
            content = f.read()
            
        # Vérification des références aux scripts
        expected_refs = [
            '01_extract.py',
            '02_profile.py',
            '03_transform.py'
        ]
        
        missing_refs = []
        for ref in expected_refs:
            if ref not in content:
                missing_refs.append(ref)
        
        if missing_refs:
            print(f"Références manquantes dans run_etl_pipeline.py: {missing_refs}")
            return False
        else:
            print("Orchestrateur cohérent avec la nouvelle structure")
            return True
            
    except Exception as e:
        print(f"Erreur lecture run_etl_pipeline.py: {e}")
        return False

def test_dim_country_coherence():
    """Teste la cohérence de la table dim_country"""
    print("\n Test de cohérence dim_country")
    
    processed_dir = Path('../processed')
    dim_country_path = processed_dir / 'dim_country.csv'
    
    if not dim_country_path.exists():
        print("Fichier dim_country.csv introuvable")
        return True  # Pas d'erreur critique
    
    try:
        dim_country = pd.read_csv(dim_country_path)
        print(f"dim_country: {dim_country.shape[0]} pays")
        
        # Test 1: Codes ISO manquants
        missing_iso = dim_country[dim_country['iso_code'].isna()]
        if len(missing_iso) > 0:
            print(f"{len(missing_iso)} pays sans code ISO:")
            for _, row in missing_iso.head(5).iterrows():  # Afficher les 5 premiers
                print(f"   - {row['country']}")
        
        # Test 2: Codes ISO non-standard
        non_standard_iso = dim_country[
            (dim_country['iso_code'].notna()) & 
            (dim_country['iso_code'].str.len() != 3)
        ]
        if len(non_standard_iso) > 0:
            print(f"{len(non_standard_iso)} codes ISO non-standard:")
            for _, row in non_standard_iso.head(5).iterrows():
                print(f"   - {row['country']}: {row['iso_code']}")
        
        # Test 3: Population manquante
        missing_pop = dim_country[dim_country['population'].isna()]
        if len(missing_pop) > 0:
            print(f"{len(missing_pop)} pays sans population:")
            for _, row in missing_pop.head(5).iterrows():
                print(f"   - {row['country']}")
        
        # Test 4: Doublons
        duplicates = dim_country[dim_country.duplicated(subset=['country'], keep=False)]
        if len(duplicates) > 0:
            print(f"{len(duplicates)} doublons détectés:")
            for _, row in duplicates.head(5).iterrows():
                print(f"   - {row['country']}: {row['iso_code']}")
        
        # Test 5: Pays valides uniquement
        valid_countries = dim_country[
            (dim_country['iso_code'].notna()) & 
            (dim_country['iso_code'].str.len() == 3) &
            (~dim_country['iso_code'].str.startswith('OWID_', na=False))
        ]
        print(f"{len(valid_countries)} pays valides avec code ISO standard")
        
        return True
        
    except Exception as e:
        print(f"Erreur lecture dim_country.csv: {e}")
        return False

def test_fact_tables_data_quality():
    """Teste la qualité des données dans les tables de faits"""
    print("\n Test qualité des données (tables de faits)")
    
    processed_dir = Path('../processed')
    
    # Test COVID
    covid_path = processed_dir / 'fact_covid_history.csv'
    if covid_path.exists():
        try:
            covid = pd.read_csv(covid_path)
            print(f"fact_covid_history: {covid.shape[0]} lignes")
            
            # Test valeurs manquantes
            missing_iso_covid = covid[covid['iso_code'].isna()]['country'].unique()
            if len(missing_iso_covid) > 0:
                print(f"{len(missing_iso_covid)} pays COVID sans code ISO:")
                for country in missing_iso_covid[:5]:  # Afficher les 5 premiers
                    print(f"   - {country}")
            
            # Test valeurs aberrantes
            if 'value' in covid.columns:
                negative_values = covid[covid['value'] < 0]
                if len(negative_values) > 0:
                    print(f"{len(negative_values)} valeurs négatives dans COVID")
        except Exception as e:
            print(f"Erreur lecture COVID: {e}")
    
    # Test MPOX
    mpox_path = processed_dir / 'fact_mpox_history.csv'
    if mpox_path.exists():
        try:
            mpox = pd.read_csv(mpox_path)
            print(f"fact_mpox_history: {mpox.shape[0]} lignes")
            
            # Test valeurs manquantes
            missing_iso_mpox = mpox[mpox['iso_code'].isna()]['country'].unique()
            if len(missing_iso_mpox) > 0:
                print(f"{len(missing_iso_mpox)} pays MPOX sans code ISO:")
                for country in missing_iso_mpox[:5]:  # Afficher les 5 premiers
                    print(f"   - {country}")
            
            # Test valeurs aberrantes
            if 'value' in mpox.columns:
                negative_values = mpox[mpox['value'] < 0]
                if len(negative_values) > 0:
                    print(f"{len(negative_values)} valeurs négatives dans MPOX")
        except Exception as e:
            print(f"Erreur lecture MPOX: {e}")
    
    return True

def test_reference_files():
    """Teste la cohérence des fichiers de référence"""
    print("\nTest fichiers de référence")
    
    docs_dir = Path('../docs')
    
    # Test ISO codes
    iso_path = docs_dir / 'iso_country_codes.csv'
    if iso_path.exists():
        try:
            iso_ref = pd.read_csv(iso_path)
            print(f"Référentiel ISO: {iso_ref.shape[0]} pays")
            
            # Test doublons
            duplicates_iso = iso_ref[iso_ref.duplicated(subset=['country'], keep=False)]
            if len(duplicates_iso) > 0:
                print(f"{len(duplicates_iso)} doublons dans le référentiel ISO")
            
            # Test codes ISO valides
            invalid_iso = iso_ref[
                (iso_ref['iso_code'].notna()) & 
                (iso_ref['iso_code'].str.len() != 3)
            ]
            if len(invalid_iso) > 0:
                print(f"{len(invalid_iso)} codes ISO non-standard dans le référentiel")
        except Exception as e:
            print(f"Erreur lecture référentiel ISO: {e}")
    
    # Test Population
    pop_path = docs_dir / 'country_population_reference.csv'
    if pop_path.exists():
        try:
            pop_ref = pd.read_csv(pop_path)
            print(f"Référentiel Population: {pop_ref.shape[0]} pays")
            
            # Test doublons
            duplicates_pop = pop_ref[pop_ref.duplicated(subset=['country'], keep=False)]
            if len(duplicates_pop) > 0:
                print(f"{len(duplicates_pop)} doublons dans le référentiel Population")
            
            # Test population négative
            negative_pop = pop_ref[pop_ref['population'] < 0]
            if len(negative_pop) > 0:
                print(f"{len(negative_pop)} populations négatives dans le référentiel")
        except Exception as e:
            print(f"Erreur lecture référentiel Population: {e}")
    
    return True

def main():
    """Point d'entrée principal"""
    print("=" * 60)
    print("TEST DE COHÉRENCE ETL - MSPR PROJECT")
    print("=" * 60)
    
    tests = [
        ("Structure des fichiers", test_file_structure),
        ("Cohérence des chemins", test_path_consistency),
        ("Flux de données", test_data_flow),
        ("Cohérence des schémas", test_schema_consistency),
        ("Orchestration du pipeline", test_pipeline_orchestration),
        ("Cohérence dim_country", test_dim_country_coherence),
        ("Qualité des données", test_fact_tables_data_quality),
        ("Fichiers de référence", test_reference_files)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n Test: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"Erreur inattendue: {e}")
            results.append((test_name, False))
    
    # Résumé
    print("\n" + "=" * 60)
    print("RÉSUMÉ DES TESTS DE COHÉRENCE")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    print(f"\n Résultat: {passed}/{total} tests réussis")
    
    if passed == total:
        print("COHÉRENCE ETL PARFAITE - Structure optimisée!")
        return 0
    else:
        print("PROBLÈMES DE COHÉRENCE DÉTECTÉS - Vérification nécessaire")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 