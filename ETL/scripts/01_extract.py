#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script d'extraction automatique des données COVID-19 et MPOX
Auteur: MSPR Project
Date: 2024
Description: Télécharge automatiquement les données depuis les sources officielles
"""

import os
import sys
import time
import hashlib
import logging
import requests
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse
from typing import Dict, List, Tuple

# Configuration des sources de données
SOURCES_CONFIG = {
    'covid_worldometer': {
        'name': 'Donnees COVID-19 Worldometer',
        'description': 'Donnees quotidiennes COVID-19 par pays',
        'url': 'https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv',
        'filename': 'worldometer_coronavirus_daily_data.csv',
        'expected_size_mb': 50.0
    },
    'mpox_owid': {
        'name': 'Donnees MPOX Our World in Data',
        'description': 'Donnees quotidiennes MPOX par pays',
        'url': 'https://raw.githubusercontent.com/owid/monkeypox/main/owid-monkeypox-data.csv',
        'filename': 'owid-monkeypox-data.csv',
        'expected_size_mb': 2.0
    }
}

def setup_logging() -> logging.Logger:
    """Configure le systeme de logging"""
    log_dir = Path('../logs') if not Path('logs').exists() else Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / f"extract_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)

class DataExtractor:
    """Classe principale pour l'extraction des donnees"""
    
    def __init__(self, raw_data_dir: str = '../raw_data'):
        self.logger = setup_logging()
        self.raw_data_dir = Path(raw_data_dir)
        self.raw_data_dir.mkdir(exist_ok=True)
        
        # Configuration de la session HTTP
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'MSPR-ETL-Pipeline/1.0 (https://github.com/mspr-project)'
        })
    
    def calculate_checksum(self, file_path: Path) -> str:
        """Calcule le checksum SHA-256 d'un fichier"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    
    def verify_file_integrity(self, file_path: Path, expected_size_mb: float) -> bool:
        """Verifie l'integrite d'un fichier telecharge"""
        if not file_path.exists():
            self.logger.error(f"Fichier {file_path} introuvable")
            return False
        
        # Verification de la taille
        file_size_mb = file_path.stat().st_size / (1024 * 1024)
        if file_size_mb < expected_size_mb * 0.5:  # Tolerance de 50%
            self.logger.warning(f"Fichier {file_path.name} plus petit que prevu: {file_size_mb:.2f}MB vs {expected_size_mb}MB")
            return False
        
        # Verification que c'est un fichier CSV valide
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                first_line = f.readline().strip()
                if not first_line or ',' not in first_line:
                    self.logger.error(f"Fichier {file_path.name} ne semble pas etre un CSV valide")
                    return False
        except UnicodeDecodeError:
            self.logger.error(f"Fichier {file_path.name} n'est pas encode en UTF-8")
            return False
        
        self.logger.info(f"Integrite verifiee pour {file_path.name} ({file_size_mb:.2f}MB)")
        return True
    
    def download_file(self, url: str, filename: str, max_retries: int = 3) -> bool:
        """Telecharge un fichier avec gestion d'erreurs et retry"""
        file_path = self.raw_data_dir / filename
        
        for attempt in range(max_retries):
            try:
                self.logger.info(f"Tentative {attempt + 1}/{max_retries} - Telechargement de {filename}")
                
                # Verification de l'URL
                parsed_url = urlparse(url)
                if not parsed_url.scheme or not parsed_url.netloc:
                    raise ValueError(f"URL invalide: {url}")
                
                # Telechargement avec timeout et stream
                response = self.session.get(url, timeout=30, stream=True)
                response.raise_for_status()
                
                # Verification du type de contenu
                content_type = response.headers.get('content-type', '')
                if 'text/csv' not in content_type and 'application/octet-stream' not in content_type:
                    self.logger.warning(f"Type de contenu inattendu: {content_type}")
                
                # Telechargement avec barre de progression
                total_size = int(response.headers.get('content-length', 0))
                downloaded_size = 0
                
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded_size += len(chunk)
                            
                            # Log de progression pour les gros fichiers
                            if total_size > 0 and downloaded_size % (1024 * 1024) == 0:  # Tous les MB
                                progress = (downloaded_size / total_size) * 100
                                self.logger.info(f"Progression {filename}: {progress:.1f}%")
                
                self.logger.info(f"Telechargement reussi: {filename}")
                return True
                
            except requests.exceptions.RequestException as e:
                self.logger.error(f"Erreur reseau lors du telechargement de {filename}: {e}")
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Backoff exponentiel
                    self.logger.info(f"Attente de {wait_time}s avant nouvelle tentative...")
                    time.sleep(wait_time)
                else:
                    self.logger.error(f"Echec du telechargement de {filename} apres {max_retries} tentatives")
                    return False
            
            except Exception as e:
                self.logger.error(f"Erreur inattendue lors du telechargement de {filename}: {e}")
                return False
        
        return False
    
    def extract_single_source(self, source_key: str, source_config: Dict) -> bool:
        """Extrait une source de donnees specifique"""
        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"EXTRACTION: {source_config['name']}")
        self.logger.info(f"URL: {source_config['url']}")
        self.logger.info(f"Fichier: {source_config['filename']}")
        self.logger.info(f"{'='*60}")
        
        file_path = self.raw_data_dir / source_config['filename']
        
        # Verification si le fichier existe deja
        if file_path.exists():
            self.logger.info(f"Fichier {source_config['filename']} existe deja")
            if self.verify_file_integrity(file_path, source_config['expected_size_mb']):
                self.logger.info("Fichier existant valide, pas de re-telechargement")
                return True
            else:
                self.logger.warning("Fichier existant corrompu, re-telechargement necessaire")
                file_path.unlink()  # Suppression du fichier corrompu
        
        # Telechargement
        if not self.download_file(source_config['url'], source_config['filename']):
            return False
        
        # Verification post-telechargement
        if not self.verify_file_integrity(file_path, source_config['expected_size_mb']):
            self.logger.error(f"Echec de la verification d'integrite pour {source_config['filename']}")
            return False
        
        # Calcul et stockage du checksum
        checksum = self.calculate_checksum(file_path)
        self.logger.info(f"Checksum SHA-256: {checksum}")
        
        return True
    
    def extract_all_sources(self) -> Dict[str, bool]:
        """Extrait toutes les sources de donnees configurees"""
        self.logger.info("DEBUT DE L'EXTRACTION AUTOMATISEE")
        self.logger.info(f"Repertoire de destination: {self.raw_data_dir.absolute()}")
        
        results = {}
        start_time = time.time()
        
        for source_key, source_config in SOURCES_CONFIG.items():
            try:
                success = self.extract_single_source(source_key, source_config)
                results[source_key] = success
                
                if success:
                    self.logger.info(f"SUCCES: {source_config['name']} - EXTRACTION REUSSIE")
                else:
                    self.logger.error(f"ECHEC: {source_config['name']} - EXTRACTION ECHOUEE")
                
            except Exception as e:
                self.logger.error(f"Erreur critique lors de l'extraction de {source_key}: {e}")
                results[source_key] = False
        
        # Resume final
        elapsed_time = time.time() - start_time
        self.logger.info(f"\n{'='*60}")
        self.logger.info("RESUME DE L'EXTRACTION")
        self.logger.info(f"{'='*60}")
        
        for source_key, success in results.items():
            status = "REUSSI" if success else "ECHOUÉ"
            self.logger.info(f"{SOURCES_CONFIG[source_key]['name']}: {status}")
        
        self.logger.info(f"Temps total: {elapsed_time:.2f} secondes")
        
        # Verification finale
        all_success = all(results.values())
        if all_success:
            self.logger.info("EXTRACTION COMPLETE - TOUTES LES SOURCES TELECHARGEES")
        else:
            self.logger.error("EXTRACTION PARTIELLE - CERTAINES SOURCES ONT ECHOUÉ")
        
        return results

def main():
    """Point d'entree principal du script"""
    print("=" * 80)
    print("EXTRACTEUR DE DONNEES PANDEMIQUES - MSPR PROJECT")
    print("=" * 80)
    print("Sources configurees:")
    for key, config in SOURCES_CONFIG.items():
        print(f"  • {config['name']}")
        print(f"    {config['description']}")
        print(f"    URL: {config['url']}")
        print()
    
    # Creation de l'extracteur
    extractor = DataExtractor()
    
    # Lancement de l'extraction
    try:
        results = extractor.extract_all_sources()
        
        # Code de sortie approprie
        if all(results.values()):
            print("\nExtraction terminee avec succes!")
            sys.exit(0)
        else:
            print("\nExtraction partielle - Verifiez les logs pour plus de details")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\nExtraction interrompue par l'utilisateur")
        sys.exit(130)
    except Exception as e:
        print(f"\nErreur critique: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 