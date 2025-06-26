import os
import pandas as pd
import numpy as np
from datetime import datetime

RAW_DATA_DIR = '../raw_data' if not os.path.exists('raw_data') else 'raw_data'
PROCESSED_DIR = '../processed' if not os.path.exists('processed') else 'processed'
DOCS_DIR = '../docs' if not os.path.exists('docs') else 'docs'
LOGS_DIR = '../logs' if not os.path.exists('logs') else 'logs'

os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(DOCS_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

def normalize_country_name(country_name):
    """Normalise les noms de pays pour améliorer le mapping"""
    if pd.isna(country_name):
        return country_name
    
    name = str(country_name).strip().lower()
    
    # Mapping des variantes courantes
    country_mapping = {
        'cabo verde': 'cape verde',
        'cote d\'ivoire': 'cote d ivoire',
        'cote d ivoire': 'cote d ivoire',
        'democratic republic of congo': 'democratic republic of the congo',
        'east timor': 'timor leste',
        'swaziland': 'eswatini',
        'uk': 'united kingdom',
        'usa': 'united states',
        'viet nam': 'vietnam',
        'czech republic': 'czechia',
        'north macedonia': 'macedonia',
        'micronesia (country)': 'micronesia',
        'sint maarten (dutch part)': 'sint maarten',
        'saint martin (french part)': 'saint martin',
        'united states virgin islands': 'virgin islands',
        'wallis and futuna': 'wallis and futuna islands',
        'falkland islands': 'falkland islands malvinas',
        'faroe islands': 'faeroe islands',
        'holy see': 'vatican',
        'state of palestine': 'palestine',
        'brunei darussalam': 'brunei',
        'guinea bissau': 'guinea-bissau',
        'tokelau': 'tokelau',
        'tuvalu': 'tuvalu',
        'pitcairn': 'pitcairn',
        'northern mariana islands': 'northern mariana islands',
        'north korea': 'north korea',
        'kosovo': 'kosovo',
        'turkmenistan': 'turkmenistan',
        'virgin islands': 'united states virgin islands'
    }
    
    return country_mapping.get(name, name)

# 1. Chargement des donnees
covid_path = os.path.join(RAW_DATA_DIR, 'worldometer_coronavirus_daily_data.csv')
mpox_path = os.path.join(RAW_DATA_DIR, 'owid-monkeypox-data.csv')

covid = pd.read_csv(covid_path)
mpox = pd.read_csv(mpox_path)

print(f"Donnees COVID chargees: {covid.shape}")
print(f"Donnees MPOX chargees: {mpox.shape}")
print(f"Colonnes COVID: {list(covid.columns)}")
print(f"Colonnes MPOX: {list(mpox.columns)}")

# 2. Standardisation des schemas
# --- COVID ---
covid_cases = covid[['date', 'location', 'new_cases']].copy()
covid_cases['indicator'] = 'cases'
covid_cases = covid_cases.rename(columns={'location': 'country', 'date': 'date', 'new_cases': 'value'})

covid_deaths = covid[['date', 'location', 'new_deaths']].copy()
covid_deaths['indicator'] = 'deaths'
covid_deaths = covid_deaths.rename(columns={'location': 'country', 'date': 'date', 'new_deaths': 'value'})

covid_std = pd.concat([covid_cases, covid_deaths], ignore_index=True)
covid_std['source'] = 'covid'

# --- MPOX ---
mpox_cases = mpox[['date', 'location', 'new_cases']].copy()
mpox_cases['indicator'] = 'cases'
mpox_cases = mpox_cases.rename(columns={'location': 'country', 'date': 'date', 'new_cases': 'value'})

mpox_deaths = mpox[['date', 'location', 'new_deaths']].copy()
mpox_deaths['indicator'] = 'deaths'
mpox_deaths = mpox_deaths.rename(columns={'location': 'country', 'date': 'date', 'new_deaths': 'value'})

mpox_std = pd.concat([mpox_cases, mpox_deaths], ignore_index=True)
mpox_std['source'] = 'mpox'

# Ajout des codes ISO pour MPOX
mpox_std['iso_code'] = mpox['iso_code']

# Colonnes cibles
TARGET_COLS = ['country', 'date', 'indicator', 'value', 'iso_code', 'population', 'unit', 'source']
for df in [covid_std, mpox_std]:
    for col in TARGET_COLS:
        if col not in df.columns:
            df[col] = np.nan

# 3. Conversion des types
for df in [covid_std, mpox_std]:
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df['country'] = df['country'].astype(str).str.strip()
    df['indicator'] = df['indicator'].astype(str).str.strip().str.lower()
    df['value'] = pd.to_numeric(df['value'], errors='coerce')
    df['unit'] = df['indicator'].map({'cases': 'count', 'deaths': 'count'})

# 4. Ajout population (mapping manuel, a completer si besoin)
pop_ref_path = os.path.join(DOCS_DIR, 'country_population_reference.csv')
iso_ref_path = os.path.join(DOCS_DIR, 'iso_country_codes.csv')

# Nettoyage et jointure population
if os.path.exists(pop_ref_path):
    pop_ref = pd.read_csv(pop_ref_path)
    # Nettoyage des noms de pays et conversion population
    pop_ref['country'] = pop_ref['country'].astype(str).str.strip().str.lower()
    pop_ref['population'] = pd.to_numeric(pop_ref['population'], errors='coerce')
    
    for df in [covid_std, mpox_std]:
        df['country_clean'] = df['country'].astype(str).str.strip().str.lower()
        # Application de la normalisation
        df['country_clean'] = df['country_clean'].apply(normalize_country_name)
        df['population'] = df['country_clean'].map(pop_ref.set_index('country')['population'])
        # Affichage des pays non trouves
        missing_pop = df.loc[df['population'].isna(), 'country'].unique()
        if len(missing_pop) > 0:
            print(f"Attention : population manquante pour {len(missing_pop)} pays : {missing_pop}")
else:
    # Genere un fichier vide a remplir manuellement
    all_countries = pd.Series(pd.concat([covid_std['country'], mpox_std['country']]).unique(), name='country')
    pd.DataFrame({'country': all_countries, 'population': np.nan}).to_csv(pop_ref_path, index=False)
    print(f"Fichier de reference population genere : {pop_ref_path}. Merci de le completer.")

# Mapping ISO (apres nettoyage des noms de pays)
if os.path.exists(iso_ref_path):
    iso_ref = pd.read_csv(iso_ref_path)
    iso_ref['country'] = iso_ref['country'].astype(str).str.strip().str.lower()
    
    for df in [covid_std, mpox_std]:
        if 'country_clean' not in df.columns:
            df['country_clean'] = df['country'].astype(str).str.strip().str.lower()
            df['country_clean'] = df['country_clean'].apply(normalize_country_name)
        
        df['iso_code'] = df['country_clean'].map(iso_ref.set_index('country')['iso_code'])
        missing_iso = df.loc[df['iso_code'].isna(), 'country'].unique()
        if len(missing_iso) > 0:
            print(f"Attention : code ISO manquant pour {len(missing_iso)} pays : {missing_iso}")
else:
    all_countries = pd.Series(pd.concat([covid_std['country'], mpox_std['country']]).unique(), name='country')
    pd.DataFrame({'country': all_countries, 'iso_code': np.nan}).to_csv(iso_ref_path, index=False)
    print(f"Fichier de reference ISO genere : {iso_ref_path}. Merci de le completer.")

# Apres la jointure, on peut supprimer la colonne temporaire
for df in [covid_std, mpox_std]:
    if 'country_clean' in df.columns:
        df.drop(columns=['country_clean'], inplace=True)

# 5. Suppression des doublons
for df in [covid_std, mpox_std]:
    df.drop_duplicates(subset=['country', 'date', 'indicator'], inplace=True)

# 6. Gestion des valeurs manquantes
for df in [covid_std, mpox_std]:
    # Supprime les lignes sans pays, date, ou indicateur
    df.dropna(subset=['country', 'date', 'indicator'], inplace=True)
    # Imputation lineaire sur 'value' par groupe
    df['value'] = df.groupby(['country', 'indicator'])['value'].transform(lambda x: x.interpolate(method='linear'))
    # Si trop de NaN, suppression
    df.dropna(subset=['value'], inplace=True)

# 7. Normalisation (per 100k)
for df in [covid_std, mpox_std]:
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

# 8. Enrichissement : incidence 7j et taux de croissance
def add_derived_metrics(df):
    df = df.sort_values(['country', 'indicator', 'date'])
    df['incidence_7j'] = df.groupby(['country', 'indicator'])['value'].transform(lambda x: x.rolling(window=7, min_periods=1).sum())
    df['growth_rate'] = df.groupby(['country', 'indicator'])['value'].pct_change().replace([np.inf, -np.inf], np.nan)
    return df

covid_std = add_derived_metrics(covid_std)
mpox_std = add_derived_metrics(mpox_std)

# 9. Tri final
covid_std = covid_std.sort_values(['country', 'indicator', 'date'])
mpox_std = mpox_std.sort_values(['country', 'indicator', 'date'])

# 10. Export des fichiers intermediaires
covid_std.to_csv(os.path.join(PROCESSED_DIR, 'fact_covid_history.csv'), index=False)
mpox_std.to_csv(os.path.join(PROCESSED_DIR, 'fact_mpox_history.csv'), index=False)

# 11. Creation des tables de dimension
# Filtrer les pays valides (avec ISO code) et exclure les régions/groups
valid_countries = pd.concat([
    covid_std[['country', 'iso_code', 'population']], 
    mpox_std[['country', 'iso_code', 'population']]
]).drop_duplicates()

# Filtrer les entités avec un code ISO valide (exclure les régions OWID_*)
dim_country = valid_countries[
    (valid_countries['iso_code'].notna()) & 
    (~valid_countries['iso_code'].str.startswith('OWID_', na=False)) &
    (valid_countries['iso_code'].str.len() == 3)  # Codes ISO standard
].copy()

# Trier par nom de pays
dim_country = dim_country.sort_values('country').reset_index(drop=True)

dim_country.to_csv(os.path.join(PROCESSED_DIR, 'dim_country.csv'), index=False)

dim_indicator = pd.DataFrame({'indicator_name': ['cases', 'deaths'], 'description': ['Nombre de cas', 'Nombre de deces']})
dim_indicator.to_csv(os.path.join(PROCESSED_DIR, 'dim_indicator.csv'), index=False)

print('Transformation terminee. Fichiers generes dans processed/.')
print(f"COVID: {covid_std.shape[0]} lignes")
print(f"MPOX: {mpox_std.shape[0]} lignes")
print(f"Pays valides dans dim_country: {dim_country.shape[0]} pays") 