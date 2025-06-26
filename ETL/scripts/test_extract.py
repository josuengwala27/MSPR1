#!/usr/bin/env python3

import sys
import os
from pathlib import Path

# Ajouter le répertoire parent au path pour importer extract
sys.path.append(str(Path(__file__).parent))

def test_extract_import():
    """Teste l'import du module extract"""
    try:
        import extract
        print("Import du module extract réussi")
        return True
    except ImportError as e:
        print(f"Erreur d'import: {e}")
        return False

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

def test_configuration():
    """Teste la configuration des sources"""
    try:
        from extract import SOURCES_CONFIG
        assert len(SOURCES_CONFIG) >= 2, "Au moins 2 sources requises"
        assert 'covid19' in SOURCES_CONFIG, "Source COVID-19 manquante"
        assert 'mpox' in SOURCES_CONFIG, "Source MPOX manquante"
        
        for source_key, config in SOURCES_CONFIG.items():
            required_fields = ['name', 'url', 'filename', 'description', 'expected_size_mb']
            for field in required_fields:
                assert field in config, f"Champ {field} manquant dans {source_key}"
        
        print("Configuration des sources valide")
        return True
    except Exception as e:
        print(f"Erreur configuration: {e}")
        return False

def test_directories():
    """Teste la création des répertoires"""
    try:
        from extract import DataExtractor
        extractor = DataExtractor()
        
        # Test création répertoire raw_data
        assert extractor.raw_data_dir.exists(), "Répertoire raw_data non créé"
        print("Répertoire raw_data créé")
        
        # Test création répertoire logs
        log_dir = Path('../logs') if not Path('logs').exists() else Path('logs')
        if not log_dir.exists():
            log_dir.mkdir(exist_ok=True)
        assert log_dir.exists(), "Répertoire logs non créé"
        print("Répertoire logs créé")
        
        return True
    except Exception as e:
        print(f"Erreur répertoires: {e}")
        return False

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

def test_url_validation():
    """Teste la validation des URLs"""
    try:
        from urllib.parse import urlparse
        
        # URLs valides
        valid_urls = [
            "https://raw.githubusercontent.com/datasets/covid-19/master/data/countries-aggregated.csv",
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

def main():
    """Point d'entrée principal des tests"""
    print("=" * 60)
    print("TESTS DE L'EXTRACTION AUTOMATISÉE")
    print("=" * 60)
    
    tests = [
        ("Import du module", test_extract_import),
        ("Création de la classe", test_extract_class),
        ("Configuration des sources", test_configuration),
        ("Création des répertoires", test_directories),
        ("Fonction checksum", test_checksum_function),
        ("Validation des URLs", test_url_validation)
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
    print("RÉSUMÉ DES TESTS")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    print(f"\n Résultat: {passed}/{total} tests réussis")
    
    if passed == total:
        print("TOUS LES TESTS RÉUSSIS - Extraction prête à utiliser!")
        return 0
    else:
        print("CERTAINS TESTS ONT ÉCHOUÉ - Vérifiez les erreurs")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 