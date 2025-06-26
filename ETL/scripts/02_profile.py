import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import logging
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Configuration du logging
log_dir = '../logs' if not os.path.exists('logs') else 'logs'
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f"etl_profile_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Configuration des graphiques
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10

RAW_DATA_DIR = '../raw_data' if not os.path.exists('raw_data') else 'raw_data'
GRAPHS_DIR = '../graphs' if not os.path.exists('graphs') else 'graphs'
os.makedirs(GRAPHS_DIR, exist_ok=True)

FILES = {
    'covid': 'worldometer_coronavirus_daily_data.csv',
    'mpox': 'owid-monkeypox-data.csv'
}

PROFILE_REPORT = os.path.join(log_dir, f"profiling_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
INTERPRETATION_REPORT = os.path.join(log_dir, f"interpretation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")

def generate_interpretations(df, name):
    """Génère des interprétations automatiques des données"""
    interpretations = []
    
    # Statistiques de base
    total_cases = df['new_cases'].sum() if 'new_cases' in df.columns else 0
    total_deaths = df['new_deaths'].sum() if 'new_deaths' in df.columns else 0
    avg_cases = df['new_cases'].mean() if 'new_cases' in df.columns else 0
    max_cases = df['new_cases'].max() if 'new_cases' in df.columns else 0
    
    # 1. Interprétation de la distribution des cas
    if 'new_cases' in df.columns:
        cases_data = df['new_cases'].dropna()
        cases_data = cases_data[cases_data > 0]
        
        if len(cases_data) > 0:
            median_cases = cases_data.median()
            q75 = cases_data.quantile(0.75)
            q25 = cases_data.quantile(0.25)
            
            interpretation = f"""
## 1. Distribution des nouveaux cas - {name.upper()}

**Observations :**
- **Total de cas** : {total_cases:,.0f} cas sur la période
- **Moyenne quotidienne** : {avg_cases:,.0f} cas par jour
- **Pic maximum** : {max_cases:,.0f} cas en une journée
- **Médiane** : {median_cases:,.0f} cas (50% des jours ont moins de cas)

**Interprétation :**
- La distribution est **asymétrique** (beaucoup de jours avec peu de cas, quelques pics)
- {q75-q25:.0f}% des observations se situent entre {q25:.0f} et {q75:.0f} cas par jour
- Les **pics épidémiques** sont rares mais intenses
- La **propagation** semble suivre un modèle de croissance exponentielle
"""
            interpretations.append(interpretation)
    
    # 2. Interprétation des décès
    if 'new_deaths' in df.columns:
        deaths_data = df['new_deaths'].dropna()
        deaths_data = deaths_data[deaths_data > 0]
        
        if len(deaths_data) > 0:
            avg_deaths = deaths_data.mean()
            max_deaths = deaths_data.max()
            lethality_rate = (total_deaths / total_cases * 100) if total_cases > 0 else 0
            
            interpretation = f"""
## 2. Distribution des nouveaux décès - {name.upper()}

**Observations :**
- **Total de décès** : {total_deaths:,.0f} décès sur la période
- **Moyenne quotidienne** : {avg_deaths:.1f} décès par jour
- **Pic maximum** : {max_deaths:,.0f} décès en une journée
- **Taux de létalité global** : {lethality_rate:.2f}%

**Interprétation :**
- La distribution des décès suit généralement celle des cas avec un **décalage temporel**
- Le taux de létalité de {lethality_rate:.2f}% indique la **gravité** de la maladie
- Les **pics de mortalité** correspondent aux vagues épidémiques
- La **variabilité** des décès quotidiens reflète l'efficacité des mesures sanitaires
"""
            interpretations.append(interpretation)
    
    # 3. Interprétation temporelle
    if 'date' in df.columns and 'new_cases' in df.columns:
        df_temp = df.copy()
        df_temp['date'] = pd.to_datetime(df_temp['date'])
        df_temp = df_temp.sort_values('date')
        
        # Trouver les pics
        daily_cases = df_temp.groupby('date')['new_cases'].sum().reset_index()
        daily_cases = daily_cases[daily_cases['new_cases'] > 0]
        
        if len(daily_cases) > 0:
            peak_date = daily_cases.loc[daily_cases['new_cases'].idxmax(), 'date']
            peak_cases = daily_cases['new_cases'].max()
            start_date = daily_cases['date'].min()
            end_date = daily_cases['date'].max()
            
            interpretation = f"""
## 3. Évolution temporelle des cas - {name.upper()}

**Observations :**
- **Période d'étude** : Du {start_date.strftime('%d/%m/%Y')} au {end_date.strftime('%d/%m/%Y')}
- **Pic épidémique** : {peak_cases:,.0f} cas le {peak_date.strftime('%d/%m/%Y')}
- **Durée totale** : {(end_date - start_date).days} jours

**Interprétation :**
- L'évolution montre des **vagues épidémiques** distinctes
- Le pic du {peak_date.strftime('%d/%m/%Y')} marque le **point culminant** de la pandémie
- Les **fluctuations** reflètent l'impact des mesures de confinement
- La **tendance générale** permet d'évaluer l'efficacité des interventions
"""
            interpretations.append(interpretation)
    
    # 4. Interprétation géographique
    if 'location' in df.columns and 'new_cases' in df.columns:
        country_cases = df.groupby('location')['new_cases'].sum().sort_values(ascending=False)
        top_5 = country_cases.head(5)
        
        interpretation = f"""
## 4. Top 10 des pays par cas - {name.upper()}

**Observations :**
- **Pays le plus touché** : {top_5.index[0]} avec {top_5.iloc[0]:,.0f} cas
- **Top 5** : {', '.join([f'{country} ({cases:,.0f})' for country, cases in top_5.items()])}
- **Répartition** : Les 5 premiers pays concentrent {(top_5.sum() / country_cases.sum() * 100):.1f}% des cas

**Interprétation :**
- La **concentration géographique** révèle des facteurs de risque spécifiques
- Les **pays développés** semblent plus touchés (capacité de détection)
- Les **différences** peuvent s'expliquer par les politiques de santé publique
- La **mondialisation** facilite la propagation internationale
"""
        interpretations.append(interpretation)
    
    # 5. Interprétation des corrélations
    if 'new_cases' in df.columns and 'new_deaths' in df.columns:
        valid_data = df[['new_cases', 'new_deaths']].dropna()
        valid_data = valid_data[(valid_data['new_cases'] > 0) & (valid_data['new_deaths'] > 0)]
        
        if len(valid_data) > 0:
            correlation = valid_data['new_cases'].corr(valid_data['new_deaths'])
            
            interpretation = f"""
## 5. Corrélation Cas vs Décès - {name.upper()}

**Observations :**
- **Coefficient de corrélation** : {correlation:.3f}
- **Relation** : {'Forte corrélation positive' if correlation > 0.7 else 'Corrélation modérée' if correlation > 0.5 else 'Faible corrélation'}
- **Signification** : Plus il y a de cas, plus il y a de décès

**Interprétation :**
- La corrélation de {correlation:.3f} confirme la **relation causale** attendue
- Le **décalage temporel** entre cas et décès n'est pas visible sur ce graphique
- La **dispersion** des points indique la variabilité de la létalité
- Les **outliers** peuvent révéler des événements particuliers (vagues, variants)
"""
        interpretations.append(interpretation)
    
    return interpretations

def create_visualizations(df, name):
    """Crée toutes les visualisations pour un dataset"""
    print(f"\n[GRAPHIQUES] Creation des visualisations pour {name}...")
    logging.info(f"Creation des visualisations pour {name}")
    
    # Générer les interprétations
    interpretations = generate_interpretations(df, name)
    
    # 1. HISTOGRAMME DES CAS
    plt.figure(figsize=(15, 10))
    
    plt.subplot(2, 3, 1)
    if 'new_cases' in df.columns:
        # Filtrer les valeurs positives et non-nulles
        cases_data = df['new_cases'].dropna()
        cases_data = cases_data[cases_data > 0]
        
        plt.hist(cases_data, bins=50, alpha=0.7, color='skyblue', edgecolor='black')
        plt.title(f'Distribution des nouveaux cas - {name.upper()}')
        plt.xlabel('Nouveaux cas par jour')
        plt.ylabel('Frequence')
        plt.yscale('log')  # Échelle log pour mieux voir la distribution
        plt.grid(True, alpha=0.3)
    
    # 2. BOXPLOT DES DÉCÈS
    plt.subplot(2, 3, 2)
    if 'new_deaths' in df.columns:
        deaths_data = df['new_deaths'].dropna()
        deaths_data = deaths_data[deaths_data > 0]
        
        plt.boxplot(deaths_data, patch_artist=True, 
                   boxprops=dict(facecolor='lightcoral', alpha=0.7))
        plt.title(f'Distribution des nouveaux deces - {name.upper()}')
        plt.ylabel('Nouveaux deces par jour')
        plt.grid(True, alpha=0.3)
    
    # 3. ÉVOLUTION TEMPORELLE DES CAS
    plt.subplot(2, 3, 3)
    if 'date' in df.columns and 'new_cases' in df.columns:
        df_temp = df.copy()
        df_temp['date'] = pd.to_datetime(df_temp['date'])
        df_temp = df_temp.sort_values('date')
        
        # Agréger par date pour avoir une vue globale
        daily_cases = df_temp.groupby('date')['new_cases'].sum().reset_index()
        daily_cases = daily_cases[daily_cases['new_cases'] > 0]
        
        plt.plot(daily_cases['date'], daily_cases['new_cases'], 
                linewidth=1, alpha=0.8, color='blue')
        plt.title(f'Evolution temporelle des cas - {name.upper()}')
        plt.xlabel('Date')
        plt.ylabel('Nouveaux cas (global)')
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)
    
    # 4. TOP 10 DES PAYS PAR CAS
    plt.subplot(2, 3, 4)
    if 'location' in df.columns and 'new_cases' in df.columns:
        country_cases = df.groupby('location')['new_cases'].sum().sort_values(ascending=False)
        top_10 = country_cases.head(10)
        
        plt.barh(range(len(top_10)), top_10.values, color='lightgreen', alpha=0.7)
        plt.yticks(range(len(top_10)), top_10.index)
        plt.title(f'Top 10 des pays par cas - {name.upper()}')
        plt.xlabel('Total des cas')
        plt.gca().invert_yaxis()
    
    # 5. HEATMAP DES CORRÉLATIONS
    plt.subplot(2, 3, 5)
    # Sélectionner les colonnes numériques pour la corrélation
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 1:
        correlation_matrix = df[numeric_cols].corr()
        
        # Masquer les valeurs NaN
        mask = np.triu(np.ones_like(correlation_matrix, dtype=bool))
        
        sns.heatmap(correlation_matrix, mask=mask, annot=True, cmap='coolwarm', 
                   center=0, square=True, linewidths=0.5)
        plt.title(f'Matrice de correlation - {name.upper()}')
    
    # 6. COMPARAISON CAS VS DÉCÈS
    plt.subplot(2, 3, 6)
    if 'new_cases' in df.columns and 'new_deaths' in df.columns:
        # Créer un scatter plot avec une ligne de tendance
        valid_data = df[['new_cases', 'new_deaths']].dropna()
        valid_data = valid_data[(valid_data['new_cases'] > 0) & (valid_data['new_deaths'] > 0)]
        
        if len(valid_data) > 0:
            plt.scatter(valid_data['new_cases'], valid_data['new_deaths'], 
                       alpha=0.5, s=20, color='purple')
            
            # Ligne de tendance
            z = np.polyfit(valid_data['new_cases'], valid_data['new_deaths'], 1)
            p = np.poly1d(z)
            plt.plot(valid_data['new_cases'], p(valid_data['new_cases']), 
                    "r--", alpha=0.8, linewidth=2)
            
            plt.title(f'Correlation Cas vs Deces - {name.upper()}')
            plt.xlabel('Nouveaux cas')
            plt.ylabel('Nouveaux deces')
            plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(os.path.join(GRAPHS_DIR, f'{name}_analysis.png'), 
                dpi=300, bbox_inches='tight')
    plt.close()
    
    # Sauvegarder les interprétations
    with open(INTERPRETATION_REPORT, 'a', encoding='utf-8') as f:
        f.write(f"\n# ANALYSE ET INTERPRETATION - {name.upper()}\n")
        f.write("=" * 60 + "\n")
        for interpretation in interpretations:
            f.write(interpretation)
        f.write("\n" + "=" * 60 + "\n")
    
    print(f"[SUCCES] Visualisations sauvegardees: {GRAPHS_DIR}/{name}_analysis.png")
    print(f"[SUCCES] Interpretations sauvegardees: {INTERPRETATION_REPORT}")

def create_comparative_analysis(df_covid, df_mpox):
    """Crée des graphiques comparatifs entre COVID et MPOX"""
    print("\n[COMPARAISON] Creation de l'analyse comparative...")
    
    # Générer les interprétations comparatives
    comparative_interpretations = generate_comparative_interpretations(df_covid, df_mpox)
    
    plt.figure(figsize=(20, 12))
    
    # 1. COMPARAISON DES DISTRIBUTIONS
    plt.subplot(2, 4, 1)
    covid_cases = df_covid['new_cases'].dropna()
    covid_cases = covid_cases[covid_cases > 0]
    mpox_cases = df_mpox['new_cases'].dropna()
    mpox_cases = mpox_cases[mpox_cases > 0]
    
    plt.hist(covid_cases, bins=50, alpha=0.6, label='COVID-19', color='red', density=True)
    plt.hist(mpox_cases, bins=50, alpha=0.6, label='MPOX', color='orange', density=True)
    plt.title('Distribution des cas - COVID vs MPOX')
    plt.xlabel('Nouveaux cas par jour')
    plt.ylabel('Densite')
    plt.legend()
    plt.yscale('log')
    
    # 2. ÉVOLUTION TEMPORELLE COMPARATIVE
    plt.subplot(2, 4, 2)
    # COVID
    df_covid_temp = df_covid.copy()
    df_covid_temp['date'] = pd.to_datetime(df_covid_temp['date'])
    covid_daily = df_covid_temp.groupby('date')['new_cases'].sum().reset_index()
    covid_daily = covid_daily[covid_daily['new_cases'] > 0]
    
    # MPOX
    df_mpox_temp = df_mpox.copy()
    df_mpox_temp['date'] = pd.to_datetime(df_mpox_temp['date'])
    mpox_daily = df_mpox_temp.groupby('date')['new_cases'].sum().reset_index()
    mpox_daily = mpox_daily[mpox_daily['new_cases'] > 0]
    
    plt.plot(covid_daily['date'], covid_daily['new_cases'], 
            label='COVID-19', color='red', alpha=0.8, linewidth=1)
    plt.plot(mpox_daily['date'], mpox_daily['new_cases'], 
            label='MPOX', color='orange', alpha=0.8, linewidth=1)
    plt.title('Evolution temporelle comparee')
    plt.xlabel('Date')
    plt.ylabel('Nouveaux cas (global)')
    plt.legend()
    plt.xticks(rotation=45)
    
    # 3. BOXPLOT COMPARATIF
    plt.subplot(2, 4, 3)
    data_to_plot = [covid_cases, mpox_cases]
    plt.boxplot(data_to_plot, labels=['COVID-19', 'MPOX'], 
               patch_artist=True,
               boxprops=dict(facecolor='lightblue', alpha=0.7),
               medianprops=dict(color='red', linewidth=2))
    plt.title('Distribution comparative des cas')
    plt.ylabel('Nouveaux cas par jour')
    plt.yscale('log')
    
    # 4. HEATMAP DES CORRÉLATIONS COMBINÉES
    plt.subplot(2, 4, 4)
    # Combiner les données pour une analyse globale
    combined_df = pd.concat([
        df_covid[['new_cases', 'new_deaths', 'total_cases', 'total_deaths']].assign(source='covid'),
        df_mpox[['new_cases', 'new_deaths', 'total_cases', 'total_deaths']].assign(source='mpox')
    ], ignore_index=True)
    
    numeric_cols = combined_df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 1:
        correlation_matrix = combined_df[numeric_cols].corr()
        sns.heatmap(correlation_matrix, annot=True, cmap='viridis', 
                   center=0, square=True, linewidths=0.5)
        plt.title('Correlations globales')
    
    # 5. TOP PAYS PAR MALADIE
    plt.subplot(2, 4, 5)
    covid_top = df_covid.groupby('location')['new_cases'].sum().sort_values(ascending=False).head(5)
    mpox_top = df_mpox.groupby('location')['new_cases'].sum().sort_values(ascending=False).head(5)
    
    x = np.arange(len(covid_top))
    width = 0.35
    
    plt.bar(x - width/2, covid_top.values, width, label='COVID-19', alpha=0.7, color='red')
    plt.bar(x + width/2, mpox_top.values, width, label='MPOX', alpha=0.7, color='orange')
    
    plt.xlabel('Pays')
    plt.ylabel('Total des cas')
    plt.title('Top 5 pays par maladie')
    plt.xticks(x, covid_top.index, rotation=45)
    plt.legend()
    
    # 6. TAUX DE LÉTALITÉ
    plt.subplot(2, 4, 6)
    # Calculer le taux de létalité par pays
    covid_lethality = df_covid.groupby('location').agg({
        'new_cases': 'sum',
        'new_deaths': 'sum'
    }).reset_index()
    covid_lethality['lethality_rate'] = (covid_lethality['new_deaths'] / covid_lethality['new_cases']) * 100
    
    mpox_lethality = df_mpox.groupby('location').agg({
        'new_cases': 'sum',
        'new_deaths': 'sum'
    }).reset_index()
    mpox_lethality['lethality_rate'] = (mpox_lethality['new_deaths'] / mpox_lethality['new_cases']) * 100
    
    # Filtrer les pays avec suffisamment de données
    covid_lethality = covid_lethality[covid_lethality['new_cases'] > 1000]
    mpox_lethality = mpox_lethality[mpox_lethality['new_cases'] > 100]
    
    plt.hist(covid_lethality['lethality_rate'].dropna(), bins=20, alpha=0.6, 
            label='COVID-19', color='red', density=True)
    plt.hist(mpox_lethality['lethality_rate'].dropna(), bins=20, alpha=0.6, 
            label='MPOX', color='orange', density=True)
    plt.title('Distribution des taux de letalite')
    plt.xlabel('Taux de letalite (%)')
    plt.ylabel('Densite')
    plt.legend()
    
    # 7. SAISONNALITÉ
    plt.subplot(2, 4, 7)
    # Analyser la saisonnalité par mois
    df_covid_temp['month'] = df_covid_temp['date'].dt.month
    df_mpox_temp['month'] = df_mpox_temp['date'].dt.month
    
    covid_monthly = df_covid_temp.groupby('month')['new_cases'].sum()
    mpox_monthly = df_mpox_temp.groupby('month')['new_cases'].sum()
    
    months = ['Jan', 'Fev', 'Mar', 'Avr', 'Mai', 'Jun', 
              'Jul', 'Aou', 'Sep', 'Oct', 'Nov', 'Dec']
    
    plt.plot(range(1, 13), covid_monthly.values, 'o-', label='COVID-19', color='red', linewidth=2)
    plt.plot(range(1, 13), mpox_monthly.values, 's-', label='MPOX', color='orange', linewidth=2)
    plt.title('Saisonnalite des cas')
    plt.xlabel('Mois')
    plt.ylabel('Total des cas')
    plt.xticks(range(1, 13), months, rotation=45)
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # 8. RÉSUMÉ STATISTIQUE
    plt.subplot(2, 4, 8)
    plt.axis('off')
    
    # Calculer les statistiques
    covid_stats = f"""COVID-19:
• Total cas: {df_covid['new_cases'].sum():,.0f}
• Total deces: {df_covid['new_deaths'].sum():,.0f}
• Pays: {df_covid['location'].nunique()}
• Periode: {df_covid['date'].min()} a {df_covid['date'].max()}

MPOX:
• Total cas: {df_mpox['new_cases'].sum():,.0f}
• Total deces: {df_mpox['new_deaths'].sum():,.0f}
• Pays: {df_mpox['location'].nunique()}
• Periode: {df_mpox['date'].min()} a {df_mpox['date'].max()}"""
    
    plt.text(0.1, 0.5, covid_stats, fontsize=12, verticalalignment='center',
             bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray", alpha=0.8))
    
    plt.tight_layout()
    plt.savefig(os.path.join(GRAPHS_DIR, 'comparative_analysis.png'), 
                dpi=300, bbox_inches='tight')
    plt.close()
    
    # Sauvegarder les interprétations comparatives
    with open(INTERPRETATION_REPORT, 'a', encoding='utf-8') as f:
        f.write(f"\n# ANALYSE COMPARATIVE COVID-19 vs MPOX\n")
        f.write("=" * 60 + "\n")
        for interpretation in comparative_interpretations:
            f.write(interpretation)
        f.write("\n" + "=" * 60 + "\n")
    
    print(f"[SUCCES] Analyse comparative sauvegardee: {GRAPHS_DIR}/comparative_analysis.png")

def generate_comparative_interpretations(df_covid, df_mpox):
    """Génère des interprétations comparatives entre COVID et MPOX"""
    interpretations = []
    
    # Statistiques comparatives
    covid_cases = df_covid['new_cases'].sum()
    mpox_cases = df_mpox['new_cases'].sum()
    covid_deaths = df_covid['new_deaths'].sum()
    mpox_deaths = df_mpox['new_deaths'].sum()
    
    covid_lethality = (covid_deaths / covid_cases * 100) if covid_cases > 0 else 0
    mpox_lethality = (mpox_deaths / mpox_cases * 100) if mpox_cases > 0 else 0
    
    interpretation = f"""
## COMPARAISON GLOBALE COVID-19 vs MPOX

**Statistiques comparatives :**

### COVID-19
- **Total cas** : {covid_cases:,.0f}
- **Total décès** : {covid_deaths:,.0f}
- **Taux de létalité** : {covid_lethality:.2f}%
- **Pays touchés** : {df_covid['location'].nunique()}

### MPOX
- **Total cas** : {mpox_cases:,.0f}
- **Total décès** : {mpox_deaths:,.0f}
- **Taux de létalité** : {mpox_lethality:.2f}%
- **Pays touchés** : {df_mpox['location'].nunique()}

**Interprétation comparative :**

1. **Échelle de propagation** : COVID-19 a touché {covid_cases/mpox_cases:.0f}x plus de personnes que MPOX
2. **Gravité** : Le taux de létalité de COVID-19 ({covid_lethality:.2f}%) est {'plus élevé' if covid_lethality > mpox_lethality else 'plus faible'} que celui de MPOX ({mpox_lethality:.2f}%)
3. **Géographie** : COVID-19 a eu un impact plus global avec {df_covid['location'].nunique()} pays touchés vs {df_mpox['location'].nunique()} pour MPOX
4. **Dynamique** : COVID-19 montre des vagues épidémiques plus marquées, MPOX une propagation plus progressive

**Facteurs explicatifs :**
- **Mode de transmission** : COVID-19 (respiratoire) vs MPOX (contact)
- **Période d'étude** : COVID-19 (2020-2024) vs MPOX (2022-2024)
- **Mesures de prévention** : Plus développées pour COVID-19
- **Variants** : COVID-19 a connu plusieurs variants majeurs
"""
    interpretations.append(interpretation)
    
    return interpretations

def profile_csv(file_path, name):
    print(f"\n--- Profiling {name} ---")
    logging.info(f"Profiling {name} ({file_path})")
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        logging.error(f"Erreur lors de la lecture de {file_path}: {e}")
        print(f"Erreur lors de la lecture de {file_path}: {e}")
        return None
    
    # Rapport textuel
    with open(PROFILE_REPORT, 'a', encoding='utf-8') as report:
        report.write(f"\n===== Profiling {name} ({file_path}) =====\n")
        report.write(f"Shape: {df.shape}\n")
        report.write(f"Colonnes: {list(df.columns)}\n")
        report.write(f"Types:\n{df.dtypes}\n")
        report.write(f"\nValeurs manquantes par colonne:\n{df.isna().sum()}\n")
        report.write(f"\nPremieres lignes:\n{df.head(5).to_string()}\n")
        report.write(f"\nStatistiques descriptives:\n{df.describe(include='all').to_string()}\n")
        
        # Doublons
        nb_total = len(df)
        nb_unique = df.drop_duplicates().shape[0]
        report.write(f"\nDoublons (lignes identiques): {nb_total - nb_unique}\n")
        
        # Statistiques supplémentaires
        if 'new_cases' in df.columns:
            report.write(f"\nStatistiques des cas:\n")
            report.write(f"Total cas: {df['new_cases'].sum():,.0f}\n")
            report.write(f"Moyenne cas/jour: {df['new_cases'].mean():,.2f}\n")
            report.write(f"Max cas/jour: {df['new_cases'].max():,.0f}\n")
        
        if 'new_deaths' in df.columns:
            report.write(f"\nStatistiques des deces:\n")
            report.write(f"Total deces: {df['new_deaths'].sum():,.0f}\n")
            report.write(f"Moyenne deces/jour: {df['new_deaths'].mean():,.2f}\n")
            report.write(f"Max deces/jour: {df['new_deaths'].max():,.0f}\n")
    
    # Affichage console
    print(f"Shape: {df.shape}")
    print(f"Colonnes: {list(df.columns)}")
    print(f"Types:\n{df.dtypes}")
    print(f"Valeurs manquantes par colonne:\n{df.isna().sum()}")
    print(f"Premieres lignes:\n{df.head(3)}")
    print(f"Statistiques descriptives:\n{df.describe(include='all').head(3)}")
    print(f"Doublons (lignes identiques): {nb_total - nb_unique}")
    
    # Créer les visualisations
    create_visualizations(df, name)
    
    logging.info(f"Profiling {name} termine.")
    return df

def main():
    print("DEBUT du profiling et de l'analyse exploratoire des fichiers CSV...")
    print(f"Dossier des graphiques: {GRAPHS_DIR}")
    print(f"Rapport d'interpretation: {INTERPRETATION_REPORT}")
    logging.info("Debut du profiling et de l'analyse exploratoire des fichiers CSV.")
    
    # Initialiser le rapport d'interprétation
    with open(INTERPRETATION_REPORT, 'w', encoding='utf-8') as f:
        f.write("# RAPPORT D'INTERPRETATION DES GRAPHIQUES\n")
        f.write("=" * 60 + "\n")
        f.write(f"Généré le : {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}\n")
        f.write("=" * 60 + "\n\n")
    
    dataframes = {}
    
    for name, fname in FILES.items():
        file_path = os.path.join(RAW_DATA_DIR, fname)
        if not os.path.exists(file_path):
            logging.error(f"Fichier manquant: {file_path}")
            print(f"ERREUR: Fichier manquant: {file_path}")
            continue
        
        df = profile_csv(file_path, name)
        if df is not None:
            dataframes[name] = df
    
    # Créer l'analyse comparative si les deux datasets sont disponibles
    if len(dataframes) == 2:
        create_comparative_analysis(dataframes['covid'], dataframes['mpox'])
    
    print(f"\nSUCCES: Profiling termine!")
    print(f"Rapport detaille: {PROFILE_REPORT}")
    print(f"Rapport d'interpretation: {INTERPRETATION_REPORT}")
    print(f"Graphiques sauvegardes dans: {GRAPHS_DIR}")
    print(f"Fichiers generes:")
    for name in dataframes.keys():
        print(f"   • {name}_analysis.png")
    if len(dataframes) == 2:
        print(f"   • comparative_analysis.png")
    
    logging.info("Profiling et analyse exploratoire termines.")

if __name__ == "__main__":
    main() 