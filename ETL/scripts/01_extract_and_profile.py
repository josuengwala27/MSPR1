import os
import pandas as pd
import logging
from datetime import datetime

# Configuration du logging
log_dir = '../logs' if not os.path.exists('logs') else 'logs'
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f"etl_extract_profile_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

RAW_DATA_DIR = '../raw_data' if not os.path.exists('raw_data') else 'raw_data'
FILES = {
    'covid': 'worldometer_coronavirus_daily_data.csv',
    'mpox': 'owid-monkeypox-data.csv'
}

PROFILE_REPORT = os.path.join(log_dir, f"profiling_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")

def profile_csv(file_path, name):
    print(f"\n--- Profiling {name} ---")
    logging.info(f"Profiling {name} ({file_path})")
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        logging.error(f"Erreur lors de la lecture de {file_path}: {e}")
        print(f"Erreur lors de la lecture de {file_path}: {e}")
        return None
    with open(PROFILE_REPORT, 'a', encoding='utf-8') as report:
        report.write(f"\n===== Profiling {name} ({file_path}) =====\n")
        report.write(f"Shape: {df.shape}\n")
        report.write(f"Colonnes: {list(df.columns)}\n")
        report.write(f"Types:\n{df.dtypes}\n")
        report.write(f"\nValeurs manquantes par colonne:\n{df.isna().sum()}\n")
        report.write(f"\nPremières lignes:\n{df.head(5).to_string()}\n")
        report.write(f"\nStatistiques descriptives:\n{df.describe(include='all').to_string()}\n")
        # Doublons
        nb_total = len(df)
        nb_unique = df.drop_duplicates().shape[0]
        report.write(f"\nDoublons (lignes identiques): {nb_total - nb_unique}\n")
    print(f"Shape: {df.shape}")
    print(f"Colonnes: {list(df.columns)}")
    print(f"Types:\n{df.dtypes}")
    print(f"Valeurs manquantes par colonne:\n{df.isna().sum()}")
    print(f"Premières lignes:\n{df.head(3)}")
    print(f"Statistiques descriptives:\n{df.describe(include='all').head(3)}")
    print(f"Doublons (lignes identiques): {nb_total - nb_unique}")
    logging.info(f"Profiling {name} terminé.")
    return df

def main():
    print("Début de l'extraction et du profiling des fichiers CSV...")
    logging.info("Début de l'extraction et du profiling des fichiers CSV.")
    for name, fname in FILES.items():
        file_path = os.path.join(RAW_DATA_DIR, fname)
        if not os.path.exists(file_path):
            logging.error(f"Fichier manquant: {file_path}")
            print(f"Fichier manquant: {file_path}")
            continue
        profile_csv(file_path, name)
    print(f"\nProfiling terminé. Rapport détaillé dans {PROFILE_REPORT}")
    logging.info("Profiling terminé.")

if __name__ == "__main__":
    main() 