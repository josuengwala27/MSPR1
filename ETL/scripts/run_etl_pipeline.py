#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script principal orchestrant le pipeline ETL complet
Auteur: MSPR Project
Date: 2024
Description: Execute automatiquement toutes les etapes ETL
"""

import os
import sys
import subprocess
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

def setup_logging() -> logging.Logger:
    """Configure le systeme de logging pour le pipeline complet"""
    log_dir = Path('../logs') if not Path('logs').exists() else Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / f"etl_pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)

class ETLPipeline:
    """Classe principale pour l'orchestration du pipeline ETL"""
    
    def __init__(self):
        self.logger = setup_logging()
        self.scripts_dir = Path(__file__).parent
        self.results = {}
        
    def run_script(self, script_name: str, description: str) -> bool:
        """Execute un script Python avec gestion d'erreurs"""
        script_path = self.scripts_dir / script_name
        
        if not script_path.exists():
            self.logger.error(f"Script {script_name} introuvable")
            return False
        
        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"EXECUTION: {description}")
        self.logger.info(f"Script: {script_name}")
        self.logger.info(f"{'='*60}")
        
        start_time = time.time()
        
        try:
            result = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True,
                cwd=self.scripts_dir,
                timeout=300
            )
            
            elapsed_time = time.time() - start_time
            
            if result.stdout:
                self.logger.info("Sortie standard:")
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        self.logger.info(f"  {line}")
            
            if result.stderr:
                self.logger.warning("Erreurs:")
                for line in result.stderr.strip().split('\n'):
                    if line.strip():
                        self.logger.warning(f"  {line}")
            
            if result.returncode == 0:
                self.logger.info(f"SUCCES: {description} - REUSSI ({elapsed_time:.2f}s)")
                return True
            else:
                self.logger.error(f"ECHEC: {description} - ECHOUÉ (code: {result.returncode}, {elapsed_time:.2f}s)")
                return False
                
        except subprocess.TimeoutExpired:
            self.logger.error(f"TIMEOUT: {description} - TIMEOUT (plus de 5 minutes)")
            return False
        except Exception as e:
            self.logger.error(f"ERREUR: {description} - ERREUR: {e}")
            return False
    
    def check_prerequisites(self) -> bool:
        """Verifie les prerequis avant l'execution"""
        self.logger.info("VERIFICATION DES PREREQUIS")
        
        try:
            import pandas
            import requests
            import numpy
            self.logger.info("Dependances Python installees")
        except ImportError as e:
            self.logger.error(f"Dependance manquante: {e}")
            return False
        
        required_dirs = ['../raw_data', '../processed', '../logs']
        for dir_path in required_dirs:
            dir_obj = Path(dir_path)
            if not dir_obj.exists():
                dir_obj.mkdir(exist_ok=True)
                self.logger.info(f"Repertoire cree: {dir_path}")
            else:
                self.logger.info(f"Repertoire existant: {dir_path}")
        
        return True
    
    def run_extraction(self) -> bool:
        """Execute l'etape d'extraction"""
        return self.run_script(
            '01_extract.py',
            'Extraction automatisee des donnees COVID-19 et MPOX'
        )
    
    def run_profiling(self) -> bool:
        """Execute l'etape de profiling"""
        return self.run_script(
            '02_profile.py',
            'Profiling et analyse des donnees brutes'
        )
    
    def run_transformation(self) -> bool:
        """Execute l'etape de transformation"""
        return self.run_script(
            '03_transform.py',
            'Transformation et nettoyage des donnees'
        )
    
    def run_tests(self) -> bool:
        """Execute les tests (optionnel)"""
        return self.run_script(
            'test_extract.py',
            'Tests de validation de l\'extraction'
        )
    
    def verify_outputs(self) -> bool:
        """Verifie que les fichiers de sortie ont ete crees"""
        self.logger.info("\nVERIFICATION DES FICHIERS DE SORTIE")
        
        expected_files = [
            '../raw_data/worldometer_coronavirus_daily_data.csv',
            '../raw_data/owid-monkeypox-data.csv',
            '../processed/fact_covid_history.csv',
            '../processed/fact_mpox_history.csv',
            '../processed/dim_country.csv',
            '../processed/dim_indicator.csv'
        ]
        
        all_exist = True
        for file_path in expected_files:
            file_obj = Path(file_path)
            if file_obj.exists():
                size_mb = file_obj.stat().st_size / (1024 * 1024)
                self.logger.info(f"FICHIER PRESENT: {file_path} ({size_mb:.2f}MB)")
            else:
                self.logger.error(f"FICHIER MANQUANT: {file_path}")
                all_exist = False
        
        return all_exist
    
    def run_pipeline(self, include_tests: bool = False) -> Dict[str, bool]:
        """Execute le pipeline ETL complet"""
        self.logger.info("DEBUT DU PIPELINE ETL COMPLET")
        self.logger.info(f"Horodatage: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        start_time = time.time()
        
        if not self.check_prerequisites():
            self.logger.error("ECHEC DES PREREQUIS - ARRET DU PIPELINE")
            return {'prerequisites': False}
        
        steps = [
            ('extraction', self.run_extraction, 'Extraction'),
            ('profiling', self.run_profiling, 'Profiling'),
            ('transformation', self.run_transformation, 'Transformation')
        ]
        
        if include_tests:
            steps.append(('tests', self.run_tests, 'Tests'))
        
        for step_name, step_func, step_desc in steps:
            self.logger.info(f"\nETAPE: {step_desc}")
            success = step_func()
            self.results[step_name] = success
            
            if not success:
                self.logger.error(f"ECHEC A L'ETAPE {step_desc} - ARRET DU PIPELINE")
                break
        
        if all(self.results.values()):
            self.logger.info("\nVERIFICATION FINALE DES SORTIES")
            self.results['verification'] = self.verify_outputs()
        
        elapsed_time = time.time() - start_time
        self.logger.info(f"\n{'='*60}")
        self.logger.info("RESUME DU PIPELINE ETL")
        self.logger.info(f"{'='*60}")
        
        for step_name, success in self.results.items():
            status = "REUSSI" if success else "ECHOUÉ"
            self.logger.info(f"{step_name.upper()}: {status}")
        
        self.logger.info(f"Temps total: {elapsed_time:.2f} secondes")
        
        all_success = all(self.results.values())
        if all_success:
            self.logger.info("PIPELINE ETL COMPLET - TOUTES LES ETAPES REUSSIES")
        else:
            self.logger.error("PIPELINE ETL PARTIEL - CERTAINES ETAPES ONT ECHOUÉ")
        
        return self.results

def main():
    """Point d'entree principal"""
    print("=" * 80)
    print("PIPELINE ETL COMPLET - MSPR PROJECT")
    print("=" * 80)
    print("Ce script execute automatiquement toutes les etapes ETL :")
    print("1. Extraction automatisee des donnees")
    print("2. Profiling et analyse des donnees brutes")
    print("3. Transformation et nettoyage des donnees")
    print("4. Tests de validation (optionnel)")
    print()
    
    include_tests = False
    if len(sys.argv) > 1 and sys.argv[1] == '--with-tests':
        include_tests = True
        print("Tests inclus dans le pipeline")
    else:
        print("Pour inclure les tests: python run_etl_pipeline.py --with-tests")
    
    print()
    
    pipeline = ETLPipeline()
    
    try:
        results = pipeline.run_pipeline(include_tests=include_tests)
        
        if all(results.values()):
            print("\nPipeline termine avec succes!")
            sys.exit(0)
        else:
            print("\nPipeline partiel - Verifiez les logs pour plus de details")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\nPipeline interrompu par l'utilisateur")
        sys.exit(130)
    except Exception as e:
        print(f"\nErreur critique: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 