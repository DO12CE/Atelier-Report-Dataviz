"""
API FastAPI pour l'analyse du dataset Superstore
🎯 Niveau débutant - Code simple et bien commenté
📊 Tous les KPI e-commerce implémentés
"""

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List, Dict, Any
from datetime import datetime
import pandas as pd
from pydantic import BaseModel
import logging

# Configuration du logger pour faciliter le débogage
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialisation de l'application FastAPI
app = FastAPI(
    title="Superstore BI API",
    description="API d'analyse Business Intelligence pour le dataset Superstore",
    version="1.0.0",
    docs_url="/docs",  # Documentation Swagger accessible via /docs
    redoc_url="/redoc"  # Documentation ReDoc accessible via /redoc
)

# Configuration CORS pour permettre les appels depuis Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifier l'URL exacte de Streamlit
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === CHARGEMENT DES DONNÉES ===

# URL du dataset Superstore sur GitHub
DATASET_URL = "https://raw.githubusercontent.com/leonism/sample-superstore/master/data/superstore.csv"

def load_data() -> pd.DataFrame:
    """
    Charge le dataset Superstore depuis GitHub
    Nettoie et prépare les données pour l'analyse
    
    Returns:
        pd.DataFrame: Dataset nettoyé et prêt à l'emploi
    """
    try:
        logger.info(f"Chargement du dataset depuis {DATASET_URL}")
        
        # Lecture du CSV
        df = pd.read_csv(DATASET_URL, encoding='latin-1')
        
        # Nettoyage des noms de colonnes (suppression espaces)
        df.columns = df.columns.str.strip()
        
        # Conversion des dates au format datetime
        df['Order Date'] = pd.to_datetime(df['Order Date'])
        df['Ship Date'] = pd.to_datetime(df['Ship Date'])
        
        # Suppression des lignes avec valeurs manquantes critiques
        df = df.dropna(subset=['Order ID', 'Customer ID', 'Sales'])
        
        logger.info(f"✅ Dataset chargé : {len(df)} commandes")
        return df
        
    except Exception as e:
        logger.error(f"❌ Erreur lors du chargement des données : {e}")
        raise HTTPException(status_code=500, detail=f"Erreur de chargement : {str(e)}")

# Chargement des données au démarrage de l'application
df = load_data()

# === MODÈLES PYDANTIC (pour la validation des réponses) ===

class KPIGlobaux(BaseModel):
    """Modèle pour les KPI globaux"""
    ca_total: float
    nb_commandes: int
    nb_clients: int
    panier_moyen: float
    quantite_vendue: int
    profit_total: float
    marge_moyenne: float

class ProduitTop(BaseModel):
    """Modèle pour les produits top performers"""
    produit: str
    categorie: str
    ca: float
    quantite: int
    profit: float

class CategoriePerf(BaseModel):
    """Modèle pour la performance par catégorie"""
    categorie: str
    ca: float
    profit: float
    nb_commandes: int
    marge_pct: float
    roi: float

# === FONCTIONS UTILITAIRES ===

def filtrer_dataframe(
    df: pd.DataFrame,
    date_debut: Optional[str] = None,
    date_fin: Optional[str] = None,
    categorie: Optional[str] = None,
    region: Optional[str] = None,
    segment: Optional[str] = None
) -> pd.DataFrame:
    """
    Applique les filtres sur le dataframe
    
    Args:
        df: DataFrame source
        date_debut: Date de début (YYYY-MM-DD)
        date_fin: Date de fin (YYYY-MM-DD)
        categorie: Catégorie de produit
        region: Région géographique
        segment: Segment client
        
    Returns:
        pd.DataFrame: DataFrame filtré
    """
    df_filtered = df.copy()
    
    # Filtre par date
    if date_debut:
        df_filtered = df_filtered[df_filtered['Order Date'] >= date_debut]
    if date_fin:
        df_filtered = df_filtered[df_filtered['Order Date'] <= date_fin]
    
    # Filtre par catégorie
    if categorie and categorie != "Toutes":
        df_filtered = df_filtered[df_filtered['Category'] == categorie]
    
    # Filtre par région
    if region and region != "Toutes":
        df_filtered = df_filtered[df_filtered['Region'] == region]
    
    # Filtre par segment
    if segment and segment != "Tous":
        df_filtered = df_filtered[df_filtered['Segment'] == segment]
    
    return df_filtered

# === ENDPOINTS API ===

@app.get("/", tags=["Info"])
def root():
    """
    Endpoint racine - Informations sur l'API
    """
    return {
        "message": "🛒 API Superstore BI",
        "version": "1.0.0",
        "dataset": "Sample Superstore",
        "nb_lignes": len(df),
        "periode": {
            "debut": df['Order Date'].min().strftime('%Y-%m-%d'),
            "fin": df['Order Date'].max().strftime('%Y-%m-%d')
        },
        "endpoints": {
            "documentation": "/docs",
            "kpi_globaux": "/kpi/globaux",
            "top_produits": "/kpi/produits/top",
            "categories": "/kpi/categories",
            "evolution_temporelle": "/kpi/temporel",
            "performance_geo": "/kpi/geographique",
            "analyse_clients": "/kpi/clients"
        }
    }

@app.get("/kpi/globaux", response_model=KPIGlobaux, tags=["KPI"])
def get_kpi_globaux(
    date_debut: Optional[str] = Query(None, description="Date début (YYYY-MM-DD)"),
    date_fin: Optional[str] = Query(None, description="Date fin (YYYY-MM-DD)"),
    categorie: Optional[str] = Query(None, description="Catégorie produit"),
    region: Optional[str] = Query(None, description="Région"),
    segment: Optional[str] = Query(None, description="Segment client")
):
    """
    📊 KPI GLOBAUX
    
    Calcule les indicateurs clés globaux :
    - Chiffre d'affaires total
    - Nombre de commandes
    - Nombre de clients uniques
    - Panier moyen
    - Quantité totale vendue
    - Profit total
    - Marge moyenne (%)
    """
    # Application des filtres
    df_filtered = filtrer_dataframe(df, date_debut, date_fin, categorie, region, segment)
    
    # Calcul des KPI
    ca_total = df_filtered['Sales'].sum()
    nb_commandes = df_filtered['Order ID'].nunique()
    nb_clients = df_filtered['Customer ID'].nunique()
    panier_moyen = ca_total / nb_commandes if nb_commandes > 0 else 0
    quantite_vendue = int(df_filtered['Quantity'].sum())
    profit_total = df_filtered['Profit'].sum()
    marge_moyenne = (profit_total / ca_total * 100) if ca_total > 0 else 0
    
    return KPIGlobaux(
        ca_total=round(ca_total, 2),
        nb_commandes=nb_commandes,
        nb_clients=nb_clients,
        panier_moyen=round(panier_moyen, 2),
        quantite_vendue=quantite_vendue,
        profit_total=round(profit_total, 2),
        marge_moyenne=round(marge_moyenne, 2)
    )

@app.get("/kpi/comparaison", tags=["KPI"])
def get_comparaison_periode(
    date_debut: str = Query(..., description="Date début (YYYY-MM-DD)"),
    date_fin: str = Query(..., description="Date fin (YYYY-MM-DD)"),
    categorie: Optional[str] = Query(None),
    region: Optional[str] = Query(None)
):
    """
    🔄 COMPARAISON SUR DEUX PÉRIODES
    
    Compare la période sélectionnée avec la période précédente de même durée.
    """
    d_debut = pd.to_datetime(date_debut)
    d_fin = pd.to_datetime(date_fin)
    duree = d_fin - d_debut
    
    # Période complémentaire (immédiatement avant)
    d_debut_prec = d_debut - duree - pd.Timedelta(days=1)
    d_fin_prec = d_debut - pd.Timedelta(days=1)
    
    # Données actuelles
    df_actuel = filtrer_dataframe(df, date_debut, date_fin, categorie, region)
    ca_actuel = df_actuel['Sales'].sum()
    profit_actuel = df_actuel['Profit'].sum()
    
    # Données précédentes
    df_prec = filtrer_dataframe(df, d_debut_prec.strftime('%Y-%m-%d'), d_fin_prec.strftime('%Y-%m-%d'), categorie, region)
    ca_prec = df_prec['Sales'].sum()
    profit_prec = df_prec['Profit'].sum()
    
    # Calcul de l'évolution
    evol_ca = ((ca_actuel - ca_prec) / ca_prec * 100) if ca_prec > 0 else 0
    evol_profit = ((profit_actuel - profit_prec) / profit_prec * 100) if profit_prec > 0 else 0
    
    return {
        "actuel": {
            "ca": round(ca_actuel, 2),
            "profit": round(profit_actuel, 2),
            "debut": date_debut,
            "fin": date_fin
        },
        "precedent": {
            "ca": round(ca_prec, 2),
            "profit": round(profit_prec, 2),
            "debut": d_debut_prec.strftime('%Y-%m-%d'),
            "fin": d_fin_prec.strftime('%Y-%m-%d')
        },
        "evolution_ca_pct": round(evol_ca, 2),
        "evolution_profit_pct": round(evol_profit, 2)
    }

@app.get("/kpi/produits/top", tags=["KPI"])
def get_top_produits(
    limite: int = Query(10, ge=1, le=50, description="Nombre de produits à retourner"),
    tri_par: str = Query("ca", regex="^(ca|profit|quantite)$", description="Critère de tri")
):
    """
    🏆 TOP PRODUITS
    
    Retourne les meilleurs produits selon le critère choisi :
    - ca : Chiffre d'affaires
    - profit : Profit
    - quantite : Quantité vendue
    """
    # Agrégation par produit
    produits = df.groupby(['Product Name', 'Category']).agg({
        'Sales': 'sum',
        'Quantity': 'sum',
        'Profit': 'sum'
    }).reset_index()
    
    # Tri selon le critère
    if tri_par == "ca":
        produits = produits.sort_values('Sales', ascending=False)
    elif tri_par == "profit":
        produits = produits.sort_values('Profit', ascending=False)
    else:  # quantite
        produits = produits.sort_values('Quantity', ascending=False)
    
    # Sélection du top
    top = produits.head(limite)
    
    # Formatage de la réponse
    result = []
    for _, row in top.iterrows():
        result.append({
            "produit": row['Product Name'],
            "categorie": row['Category'],
            "ca": round(row['Sales'], 2),
            "quantite": int(row['Quantity']),
            "profit": round(row['Profit'], 2)
        })
    
    return result

@app.get("/kpi/categories", tags=["KPI"])
def get_performance_categories():
    """
    📦 PERFORMANCE PAR CATÉGORIE
    
    Analyse la performance de chaque catégorie :
    - CA total
    - Profit
    - Nombre de commandes
    - Marge (%)
    """
    # Agrégation par catégorie
    categories = df.groupby('Category').agg({
        'Sales': 'sum',
        'Profit': 'sum',
        'Order ID': 'nunique'
    }).reset_index()
    
    # Calcul de la marge et ROI (simplifié : ROI = Profit / (CA - Profit) * 100 si CA-Profit > 0)
    # Dans ce dataset on n'a pas le coût direct, on peut estimer Coût = CA - Profit
    categories['marge_pct'] = (categories['Profit'] / categories['Sales'] * 100).round(2)
    categories['roi'] = (categories['Profit'] / (categories['Sales'] - categories['Profit']) * 100).round(2)
    
    # Renommage des colonnes
    categories.columns = ['categorie', 'ca', 'profit', 'nb_commandes', 'marge_pct', 'roi']
    
    # Tri par CA décroissant
    categories = categories.sort_values('ca', ascending=False)
    
    return categories.to_dict('records')

@app.get("/kpi/temporel", tags=["KPI"])
def get_evolution_temporelle(
    periode: str = Query('mois', regex='^(jour|mois|annee)$', description="Granularité temporelle")
):
    """
    📈 ÉVOLUTION TEMPORELLE
    
    Analyse l'évolution du CA, profit et commandes dans le temps
    Granularités disponibles : jour, mois, annee
    """
    df_temp = df.copy()
    
    # Création de la colonne période selon la granularité
    if periode == 'jour':
        df_temp['periode'] = df_temp['Order Date'].dt.strftime('%Y-%m-%d')
    elif periode == 'mois':
        df_temp['periode'] = df_temp['Order Date'].dt.strftime('%Y-%m')
    else:  # annee
        df_temp['periode'] = df_temp['Order Date'].dt.strftime('%Y')
    
    # Agrégation
    temporal = df_temp.groupby('periode').agg({
        'Sales': 'sum',
        'Profit': 'sum',
        'Order ID': 'nunique',
        'Quantity': 'sum'
    }).reset_index()
    
    temporal.columns = ['periode', 'ca', 'profit', 'nb_commandes', 'quantite']
    
    # Tri chronologique
    temporal = temporal.sort_values('periode')
    
    return temporal.to_dict('records')

@app.get("/kpi/geographique", tags=["KPI"])
def get_performance_geographique():
    """
    🌍 PERFORMANCE GÉOGRAPHIQUE
    
    Analyse la performance par région :
    - CA par région
    - Profit par région
    - Nombre de clients
    - Nombre de commandes
    """
    geo = df.groupby('Region').agg({
        'Sales': 'sum',
        'Profit': 'sum',
        'Customer ID': 'nunique',
        'Order ID': 'nunique'
    }).reset_index()
    
    geo.columns = ['region', 'ca', 'profit', 'nb_clients', 'nb_commandes']
    geo = geo.sort_values('ca', ascending=False)
    
    return geo.to_dict('records')

@app.get("/kpi/geographique/états", tags=["KPI"])
def get_performance_etats():
    """
    🇺🇸 PERFORMANCE PAR ÉTAT
    
    Analyse détaillée par État pour la cartographie
    """
    etats = df.groupby('State').agg({
        'Sales': 'sum',
        'Profit': 'sum',
        'Order ID': 'nunique'
    }).reset_index()
    
    etats.columns = ['etat', 'ca', 'profit', 'nb_commandes']
    
    # Mapping des noms complets vers les codes ISO (nécessaires pour Plotly USA-states)
    state_to_code = {
        'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR', 'California': 'CA',
        'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE', 'Florida': 'FL', 'Georgia': 'GA',
        'Hawaii': 'HI', 'Idaho': 'ID', 'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA',
        'Kansas': 'KS', 'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD',
        'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS',
        'Missouri': 'MO', 'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV', 'New Hampshire': 'NH',
        'New Jersey': 'NJ', 'New Mexico': 'NM', 'New York': 'NY', 'North Carolina': 'NC',
        'North Dakota': 'ND', 'Ohio': 'OH', 'Oklahoma': 'OK', 'Oregon': 'OR', 'Pennsylvania': 'PA',
        'Rhode Island': 'RI', 'South Carolina': 'SC', 'South Dakota': 'SD', 'Tennessee': 'TN',
        'Texas': 'TX', 'Utah': 'UT', 'Vermont': 'VT', 'Virginia': 'VA', 'Washington': 'WA',
        'West Virginia': 'WV', 'Wisconsin': 'WI', 'Wyoming': 'WY', 'District of Columbia': 'DC'
    }
    etats['code'] = etats['etat'].map(state_to_code)
    
    return etats.to_dict('records')

@app.get("/kpi/clients", tags=["KPI"])
def get_analyse_clients(
    limite: int = Query(10, ge=1, le=100, description="Nombre de top clients")
):
    """
    👥 ANALYSE CLIENTS
    
    Retourne :
    - Top clients par CA
    - Statistiques de récurrence
    - Analyse par segment
    """
    # Top clients
    clients = df.groupby('Customer ID').agg({
        'Sales': 'sum',
        'Profit': 'sum',
        'Order ID': 'nunique',
        'Customer Name': 'first'
    }).reset_index()
    
    clients.columns = ['customer_id', 'ca_total', 'profit_total', 'nb_commandes', 'nom']
    clients['valeur_commande_moy'] = (clients['ca_total'] / clients['nb_commandes']).round(2)
    
    top_clients = clients.sort_values('ca_total', ascending=False).head(limite)
    
    # Statistiques de récurrence
    recurrence = {
        "clients_1_achat": len(clients[clients['nb_commandes'] == 1]),
        "clients_recurrents": len(clients[clients['nb_commandes'] > 1]),
        "nb_commandes_moyen": round(clients['nb_commandes'].mean(), 2),
        "total_clients": len(clients)
    }
    
    # Analyse par segment
    segments = df.groupby('Segment').agg({
        'Sales': 'sum',
        'Profit': 'sum',
        'Customer ID': 'nunique'
    }).reset_index()
    segments.columns = ['segment', 'ca', 'profit', 'nb_clients']
    
    return {
        "top_clients": top_clients.to_dict('records'),
        "recurrence": recurrence,
        "segments": segments.to_dict('records')
    }

@app.get("/filters/valeurs", tags=["Filtres"])
def get_valeurs_filtres():
    """
    🎯 VALEURS POUR LES FILTRES
    
    Retourne toutes les valeurs uniques disponibles pour les filtres
    """
    return {
        "categories": sorted(df['Category'].unique().tolist()),
        "regions": sorted(df['Region'].unique().tolist()),
        "segments": sorted(df['Segment'].unique().tolist()),
        "etats": sorted(df['State'].unique().tolist()),
        "plage_dates": {
            "min": df['Order Date'].min().strftime('%Y-%m-%d'),
            "max": df['Order Date'].max().strftime('%Y-%m-%d')
        }
    }

@app.get("/data/commandes", tags=["Données brutes"])
def get_commandes(
    limite: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """
    📋 DONNÉES BRUTES
    
    Retourne les commandes brutes avec pagination
    """
    total = len(df)
    commandes = df.iloc[offset:offset+limite]
    
    # Conversion des dates en string pour JSON
    commandes_dict = commandes.copy()
    commandes_dict['Order Date'] = commandes_dict['Order Date'].dt.strftime('%Y-%m-%d')
    commandes_dict['Ship Date'] = commandes_dict['Ship Date'].dt.strftime('%Y-%m-%d')
    
    return {
        "total": total,
        "limite": limite,
        "offset": offset,
        "data": commandes_dict.to_dict('records')
    }

# === DÉMARRAGE DU SERVEUR ===

if __name__ == "__main__":
    import uvicorn
    print("🚀 Démarrage de l'API Superstore BI sur http://localhost:8000")
    print("📚 Documentation disponible sur http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
