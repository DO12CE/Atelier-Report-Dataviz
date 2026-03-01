"""
Dashboard Streamlit pour l'analyse Superstore
🎯 Niveau débutant - Interface intuitive et code commenté
📊 Visualisations interactives avec Plotly
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import pandas as pd
from datetime import datetime, timedelta
import time
import os

# === CONFIGURATION PAGE ===
st.set_page_config(
    page_title="Superstore BI Dashboard",
    page_icon="🛒",
    layout="wide",  # Mode large pour utiliser tout l'écran
    initial_sidebar_state="expanded"
)

# === STYLES CSS PERSONNALISÉS ===
st.markdown("""
<style>
    /* Style pour les cartes KPI */
    .kpi-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Amélioration des métriques Streamlit */
    [data-testid="stMetric"] {
        background-color: #1a1c24;
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #3d414d;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    [data-testid="stMetricLabel"] p {
        color: #94a3b8 !important;
        font-weight: 500 !important;
        font-size: 1rem !important;
    }
    
    [data-testid="stMetricValue"] div {
        font-weight: 700 !important;
    }
    
    /* Style des titres */
    h1, h2, h3 {
        font-family: 'Inter', sans-serif;
    }
    
    /* Style du sidebar */
    .css-1d391kg {
        background-color: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)

# === CONFIGURATION API ===
# Utilise la variable d'environnement API_URL si définie (pour Docker),
# sinon utilise localhost (pour développement local)
API_URL = os.getenv("API_URL", "http://localhost:8000")

# === FONCTIONS HELPERS ===

@st.cache_data(ttl=300)  # Cache de 5 minutes
def appeler_api(endpoint: str, params: dict = None):
    """
    Appelle l'API et retourne les données
    Le cache évite de recharger les mêmes données
    
    Args:
        endpoint: Chemin de l'endpoint (ex: "/kpi/globaux")
        params: Paramètres de requête (optionnel)
        
    Returns:
        dict ou list: Données retournées par l'API
    """
    try:
        url = f"{API_URL}{endpoint}"
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()  # Lève une exception si erreur HTTP
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error("❌ **Impossible de se connecter à l'API**")
        st.info(f"💡 Vérifiez que l'API est démarrée sur: {API_URL}")
        st.info("📝 Commande: `python backend/main.py` ou `docker-compose up`")
        st.stop()
    except requests.exceptions.Timeout:
        st.error("⏱️ **Timeout : l'API met trop de temps à répondre**")
        st.stop()
    except requests.exceptions.HTTPError as e:
        st.error(f"⚠️ **Erreur HTTP** : {e}")
        st.stop()
    except Exception as e:
        st.error(f"⚠️ **Erreur inattendue** : {e}")
        st.stop()

def formater_euro(valeur: float) -> str:
    """Formate un nombre en euros"""
    return f"{valeur:,.2f} €".replace(",", " ").replace(".", ",")

def formater_nombre(valeur: int) -> str:
    """Formate un grand nombre avec espaces"""
    return f"{valeur:,}".replace(",", " ")

def formater_pourcentage(valeur: float) -> str:
    """Formate un pourcentage"""
    return f"{valeur:.2f}%"

# === VÉRIFICATION CONNEXION API ===
with st.spinner("🔄 Connexion à l'API..."):
    try:
        info_api = appeler_api("/")
        st.success(f"✅ Connecté à l'API - Dataset : {info_api['dataset']} ({info_api['nb_lignes']} lignes)")
    except:
        st.error(f"❌ L'API n'est pas accessible sur {API_URL}")
        st.stop()

# === HEADER ===
st.title("🛒 Superstore BI Dashboard")
st.markdown("**Analyse Business Intelligence du dataset Superstore - Tableau de bord interactif**")
st.divider()

# === SIDEBAR - FILTRES ===
st.sidebar.header("🎯 Filtres d'analyse")
st.sidebar.markdown("*Ajustez les filtres pour analyser des segments spécifiques*")

# Récupération des valeurs disponibles pour les filtres
valeurs_filtres = appeler_api("/filters/valeurs")

# --- Filtre temporel ---
st.sidebar.subheader("📅 Période")
date_min = datetime.strptime(valeurs_filtres['plage_dates']['min'], '%Y-%m-%d')
date_max = datetime.strptime(valeurs_filtres['plage_dates']['max'], '%Y-%m-%d')

col1, col2 = st.sidebar.columns(2)
with col1:
    date_debut = st.date_input(
        "Du",
        value=date_min,
        min_value=date_min,
        max_value=date_max
    )
with col2:
    date_fin = st.date_input(
        "Au",
        value=date_max,
        min_value=date_min,
        max_value=date_max
    )

# --- Filtre catégorie ---
st.sidebar.subheader("📦 Catégorie")
categorie = st.sidebar.selectbox(
    "Sélectionner une catégorie",
    options=["Toutes"] + valeurs_filtres['categories'],
    help="Filtrer par catégorie de produits"
)

# --- Filtre région ---
st.sidebar.subheader("🌍 Région")
region = st.sidebar.selectbox(
    "Sélectionner une région",
    options=["Toutes"] + valeurs_filtres['regions'],
    help="Filtrer par région géographique"
)

# --- Filtre segment ---
st.sidebar.subheader("👥 Segment client")
segment = st.sidebar.selectbox(
    "Sélectionner un segment",
    options=["Tous"] + valeurs_filtres['segments'],
    help="Consumer / Corporate / Home Office"
)

# Bouton pour réinitialiser les filtres
if st.sidebar.button("🔄 Réinitialiser les filtres", use_container_width=True):
    st.rerun()

st.sidebar.divider()
st.sidebar.info("💡 **Astuce** : Les graphiques sont interactifs ! Passez la souris pour voir les détails.")

# === PRÉPARATION DES PARAMÈTRES ===
params_filtres = {
    'date_debut': date_debut.strftime('%Y-%m-%d'),
    'date_fin': date_fin.strftime('%Y-%m-%d')
}
if categorie != "Toutes":
    params_filtres['categorie'] = categorie
if region != "Toutes":
    params_filtres['region'] = region
if segment != "Tous":
    params_filtres['segment'] = segment

# === SECTION 1 : COMPARAISON ET STORYTELLING ===
st.header("📖 Storytelling & Analyse Comparative")

with st.spinner("🔍 Analyse des tendances..."):
    # Appel de la nouvelle API de comparaison
    try:
        comp_data = appeler_api("/kpi/comparaison", params=params_filtres)
        
        # Section Storytelling Automatisé
        col_story, col_insight = st.columns([2, 1])
        
        with col_story:
            st.subheader("💡 Ce que disent les chiffres")
            
            diff_ca = comp_data['evolution_ca_pct']
            diff_profit = comp_data['evolution_profit_pct']
            
            if diff_ca > 0:
                st.success(f"📈 **Croissance positive** : Le chiffre d'affaires a progressé de **{diff_ca}%** par rapport à la période précédente.")
            else:
                st.warning(f"📉 **Baisse de régime** : Le chiffre d'affaires a reculé de **{abs(diff_ca)}%**. Une analyse des causes est recommandée.")
                
            if diff_profit > diff_ca:
                st.info("🎯 **Optimisation des marges** : Le profit croît plus vite que le CA, signe d'une meilleure efficacité opérationnelle.")
            elif diff_profit < 0 and diff_ca > 0:
                st.error("⚠️ **Alerte Rentabilité** : Malgré une hausse du CA, les profits chutent. Attention aux coûts ou aux remises excessives.")
                
        with col_insight:
            st.subheader("🎯 Objectif Décisionnel")
            st.info("""
            L'objectif de ce dashboard est de passer du **constat** (ce qui s'est passé) à la **décision** (ce qu'il faut faire). 
            Utilisez les filtres à gauche pour isoler les régions ou segments sous-performants.
            """)
    except Exception as e:
        st.warning("⚠️ Les données de comparaison ne sont pas disponibles pour cette période.")
        comp_data = None

st.divider()

# === SECTION 2 : KPI GLOBAUX ===

st.header("📊 Indicateurs Clés de Performance (KPI)")

with st.spinner("📈 Chargement des KPI..."):
    kpi_data = appeler_api("/kpi/globaux", params=params_filtres)

# Affichage des KPI en 4 colonnes
col1, col2, col3, col4 = st.columns(4)

# Récupération des deltas si disponibles
delta_ca = comp_data['evolution_ca_pct'] if comp_data else None
delta_profit = comp_data['evolution_profit_pct'] if comp_data else None

with col1:
    st.metric(
        label="💰 Chiffre d'affaires",
        value=formater_euro(kpi_data['ca_total']),
        delta=f"{delta_ca}%" if delta_ca is not None else None,
        help="Somme totale des ventes (Delta vs période précédente)"
    )
    st.metric(
        label="📈 Marge moyenne",
        value=formater_pourcentage(kpi_data['marge_moyenne']),
        help="Profit / CA * 100"
    )

with col2:
    st.metric(
        label="🧾 Commandes",
        value=formater_nombre(kpi_data['nb_commandes']),
        help="Nombre total de commandes"
    )
    st.metric(
        label="💵 Profit total",
        value=formater_euro(kpi_data['profit_total']),
        delta=f"{delta_profit}%" if delta_profit is not None else None,
        help="Bénéfice total généré (Delta vs période précédente)"
    )

with col3:
    st.metric(
        label="👥 Clients",
        value=formater_nombre(kpi_data['nb_clients']),
        help="Nombre de clients uniques"
    )
    st.metric(
        label="🛒 Panier moyen",
        value=formater_euro(kpi_data['panier_moyen']),
        help="CA / Nombre de commandes"
    )

with col4:
    st.metric(
        label="📦 Quantité vendue",
        value=formater_nombre(kpi_data['quantite_vendue']),
        help="Total des produits vendus"
    )
    # Calcul du nombre moyen d'articles par commande
    articles_par_commande = kpi_data['quantite_vendue'] / kpi_data['nb_commandes'] if kpi_data['nb_commandes'] > 0 else 0
    st.metric(
        label="📊 Articles/commande",
        value=f"{articles_par_commande:.2f}",
        help="Quantité moyenne par commande"
    )

st.divider()

# === SECTION 2 : GRAPHIQUES PRINCIPAUX ===
st.header("📈 Analyses Détaillées")

# Tabs pour organiser les différentes analyses
tab1, tab2, tab3, tab4 = st.tabs(["🏆 Produits", "📦 Catégories", "📅 Temporel", "🌍 Géographique"])

# --- TAB 1 : PRODUITS ---
with tab1:
    st.subheader("Top 10 Produits")
    
    # Sélecteur pour le critère de tri
    col_tri, col_limite = st.columns([3, 1])
    with col_tri:
        critere_tri = st.radio(
            "Trier par",
            options=['ca', 'profit', 'quantite'],
            format_func=lambda x: {'ca': '💰 CA', 'profit': '💵 Profit', 'quantite': '📦 Quantité'}[x],
            horizontal=True
        )
    with col_limite:
        nb_produits = st.number_input("Afficher", min_value=5, max_value=50, value=10, step=5)
    
    # Récupération des données
    top_produits = appeler_api("/kpi/produits/top", params={'limite': nb_produits, 'tri_par': critere_tri})
    df_produits = pd.DataFrame(top_produits)
    
    # Dictionnaire des labels pour le titre du graphique
    labels_criteres = {
        'ca': 'CA',
        'profit': 'Profit',
        'quantite': 'Quantité'
    }
    
    # Graphique en barres horizontales
    fig_produits = px.bar(
        df_produits,
        x=critere_tri,
        y='produit',
        color='categorie',
        orientation='h',
        title=f"Top {nb_produits} Produits par {labels_criteres[critere_tri]}",
        labels={
            'ca': 'Chiffre d\'affaires (€)',
            'profit': 'Profit (€)',
            'quantite': 'Quantité vendue',
            'produit': 'Produit',
            'categorie': 'Catégorie'
        },
        color_discrete_sequence=px.colors.qualitative.Set3,
        height=500
    )
    fig_produits.update_layout(
        showlegend=True,
        hovermode='closest',
        yaxis={'categoryorder':'total ascending'}
    )
    st.plotly_chart(fig_produits, use_container_width=True)
    
    # Tableau détaillé
    with st.expander("📋 Voir le tableau détaillé"):
        st.dataframe(
            df_produits[['produit', 'categorie', 'ca', 'profit', 'quantite']].rename(columns={
                'produit': 'Produit',
                'categorie': 'Catégorie',
                'ca': 'CA (€)',
                'profit': 'Profit (€)',
                'quantite': 'Quantité'
            }),
            use_container_width=True,
            hide_index=True
        )

# --- TAB 2 : CATÉGORIES ---
with tab2:
    st.subheader("Performance par Catégorie")
    
    categories = appeler_api("/kpi/categories")
    df_cat = pd.DataFrame(categories)
    
    # Graphiques côte à côte
    col_left, col_right = st.columns(2)
    
    with col_left:
        # Graphique CA vs Profit
        fig_cat = go.Figure()
        fig_cat.add_trace(go.Bar(
            name='CA',
            x=df_cat['categorie'],
            y=df_cat['ca'],
            marker_color='#667eea',
            text=df_cat['ca'].apply(lambda x: f"{x:,.0f}€"),
            textposition='outside'
        ))
        fig_cat.add_trace(go.Bar(
            name='Profit',
            x=df_cat['categorie'],
            y=df_cat['profit'],
            marker_color='#764ba2',
            text=df_cat['profit'].apply(lambda x: f"{x:,.0f}€"),
            textposition='outside'
        ))
        fig_cat.update_layout(
            title="CA et Profit par Catégorie",
            barmode='group',
            xaxis_title="Catégorie",
            yaxis_title="Montant (€)",
            height=400,
            showlegend=True
        )
        st.plotly_chart(fig_cat, use_container_width=True)
    
    with col_right:
        # Graphique ROI
        fig_roi = px.bar(
            df_cat,
            x='categorie',
            y='roi',
            title="ROI par Catégorie (%)",
            labels={'categorie': 'Catégorie', 'roi': 'ROI (%)'},
            color='roi',
            color_continuous_scale='RdYlGn',
            text='roi',
            height=400
        )
        fig_roi.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
        st.plotly_chart(fig_roi, use_container_width=True)
    
    # Tableau récapitulatif
    st.markdown("### 📊 Tableau récapitulatif avec Rentabilité")
    st.dataframe(
        df_cat[['categorie', 'ca', 'profit', 'marge_pct', 'roi', 'nb_commandes']].rename(columns={
            'categorie': 'Catégorie',
            'ca': 'CA (€)',
            'profit': 'Profit (€)',
            'marge_pct': 'Marge (%)',
            'roi': 'ROI (%)',
            'nb_commandes': 'Nb Commandes'
        }),
        use_container_width=True,
        hide_index=True
    )

# --- TAB 3 : TEMPOREL ---
with tab3:
    st.subheader("Évolution Temporelle")
    
    # Sélecteur de granularité
    granularite = st.radio(
        "Période d'analyse",
        options=['jour', 'mois', 'annee'],
        format_func=lambda x: {'jour': '📅 Par jour', 'mois': '📊 Par mois', 'annee': '📈 Par année'}[x],
        horizontal=True
    )
    
    temporal = appeler_api("/kpi/temporel", params={'periode': granularite})
    df_temporal = pd.DataFrame(temporal)
    
    # Graphique d'évolution
    fig_temporal = make_subplots(
        rows=2, cols=1,
        subplot_titles=("Évolution du CA et Profit", "Évolution du Nombre de Commandes"),
        vertical_spacing=0.12,
        specs=[[{"secondary_y": False}], [{"secondary_y": False}]]
    )
    
    # Graphique CA et Profit
    fig_temporal.add_trace(
        go.Scatter(
            x=df_temporal['periode'],
            y=df_temporal['ca'],
            mode='lines+markers',
            name='CA',
            line=dict(color='#667eea', width=3),
            fill='tozeroy'
        ),
        row=1, col=1
    )
    
    fig_temporal.add_trace(
        go.Scatter(
            x=df_temporal['periode'],
            y=df_temporal['profit'],
            mode='lines+markers',
            name='Profit',
            line=dict(color='#764ba2', width=3)
        ),
        row=1, col=1
    )
    
    # Graphique nombre de commandes
    fig_temporal.add_trace(
        go.Bar(
            x=df_temporal['periode'],
            y=df_temporal['nb_commandes'],
            name='Commandes',
            marker_color='#f39c12'
        ),
        row=2, col=1
    )
    
    fig_temporal.update_xaxes(title_text="Période", row=2, col=1)
    fig_temporal.update_yaxes(title_text="Montant (€)", row=1, col=1)
    fig_temporal.update_yaxes(title_text="Nombre", row=2, col=1)
    fig_temporal.update_layout(height=700, showlegend=True)
    
    st.plotly_chart(fig_temporal, use_container_width=True)
    
    # Statistiques temporelles
    col_stats1, col_stats2, col_stats3 = st.columns(3)
    with col_stats1:
        st.metric("📈 CA moyen/période", formater_euro(df_temporal['ca'].mean()))
    with col_stats2:
        st.metric("📊 Commandes moy/période", formater_nombre(int(df_temporal['nb_commandes'].mean())))
    with col_stats3:
        meilleure_periode = df_temporal.loc[df_temporal['ca'].idxmax()]
        st.metric("🏆 Meilleure période", meilleure_periode['periode'])

# --- TAB 4 : GÉOGRAPHIQUE ---
with tab4:
    st.subheader("Performance Géographique")
    
    geo = appeler_api("/kpi/geographique")
    df_geo = pd.DataFrame(geo)
    
    col_geo1, col_geo2 = st.columns(2)
    
    with col_geo1:
        # Graphique CA par région
        fig_geo_ca = px.bar(
            df_geo,
            x='region',
            y='ca',
            title="Chiffre d'affaires par Région",
            labels={'region': 'Région', 'ca': 'CA (€)'},
            color='ca',
            color_continuous_scale='Blues',
            text='ca',
            height=400
        )
        fig_geo_ca.update_traces(texttemplate='%{text:,.0f}€', textposition='outside')
        st.plotly_chart(fig_geo_ca, use_container_width=True)
    
    with col_geo2:
        # Graphique nombre de clients par région
        fig_geo_clients = px.pie(
            df_geo,
            values='nb_clients',
            names='region',
            title="Répartition des Clients par Région",
            color_discrete_sequence=px.colors.qualitative.Set3,
            height=400
        )
        fig_geo_clients.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_geo_clients, use_container_width=True)
    
    # Heatmap par état (USA)
    st.subheader("🗺️ Carte thermique des ventes par État")
    
    etats_data = appeler_api("/kpi/geographique/états")
    df_etats = pd.DataFrame(etats_data)
    
    # Mapping des noms d'états vers codes (simplifié pour le dataset Superstore qui utilise les noms complets)
    # Plotly a besoin des codes ISO (ex: CA, NY) ou des noms exacts si configuré
    fig_map = px.choropleth(
        df_etats,
        locations='code',
        locationmode="USA-states",
        color='ca',
        scope="usa",
        title="Chiffre d'affaires par État (USD)",
        labels={'ca': 'CA ($)', 'code': 'État'},
        color_continuous_scale="Viridis",
        template="plotly_white"
    )

    fig_map.update_layout(height=500, margin={"r":0,"t":50,"l":0,"b":0})
    st.plotly_chart(fig_map, use_container_width=True)

    # Tableau géographique
    st.markdown("### 📊 Tableau géographique détaillé")
    st.dataframe(
        df_geo[['region', 'ca', 'profit', 'nb_clients', 'nb_commandes']].rename(columns={
            'region': 'Région',
            'ca': 'CA (€)',
            'profit': 'Profit (€)',
            'nb_clients': 'Nb Clients',
            'nb_commandes': 'Nb Commandes'
        }),
        use_container_width=True,
        hide_index=True
    )

st.divider()

# === SECTION 3 : ANALYSE CLIENTS ===
st.header("👥 Analyse Clients")

clients_data = appeler_api("/kpi/clients", params={'limite': 10})

col_client1, col_client2 = st.columns([2, 1])

with col_client1:
    st.subheader("🏆 Top 10 Clients")
    df_top_clients = pd.DataFrame(clients_data['top_clients'])
    
    fig_clients = px.bar(
        df_top_clients,
        x='ca_total',
        y='nom',
        orientation='h',
        title="Top Clients par CA",
        labels={'ca_total': 'CA Total (€)', 'nom': 'Client'},
        color='nb_commandes',
        color_continuous_scale='Viridis',
        height=400
    )
    st.plotly_chart(fig_clients, use_container_width=True)

with col_client2:
    st.subheader("📊 Statistiques clients")
    rec = clients_data['recurrence']
    
    st.metric("Total clients", formater_nombre(rec['total_clients']))
    st.metric("Clients récurrents", formater_nombre(rec['clients_recurrents']))
    st.metric("Clients 1 achat", formater_nombre(rec['clients_1_achat']))
    st.metric("Commandes/client", f"{rec['nb_commandes_moyen']:.2f}")
    
    # Calcul du taux de fidélisation
    taux_fidelisation = (rec['clients_recurrents'] / rec['total_clients'] * 100) if rec['total_clients'] > 0 else 0
    st.metric("Taux de fidélisation", f"{taux_fidelisation:.1f}%")

# Analyse par segment
st.subheader("💼 Performance par Segment Client")
df_segments = pd.DataFrame(clients_data['segments'])

fig_segments = go.Figure()
fig_segments.add_trace(go.Bar(
    name='CA',
    x=df_segments['segment'],
    y=df_segments['ca'],
    marker_color='#3498db'
))
fig_segments.add_trace(go.Bar(
    name='Profit',
    x=df_segments['segment'],
    y=df_segments['profit'],
    marker_color='#2ecc71'
))
fig_segments.update_layout(
    title="CA et Profit par Segment",
    barmode='group',
    height=350
)
st.plotly_chart(fig_segments, use_container_width=True)

st.divider()

# === SECTION 4 : RENTABILITÉ ===
st.header("💸 Analyse de Rentabilité")

with st.spinner("🔍 Calcul de la rentabilité..."):
    rentabilite = appeler_api("/kpi/rentabilite")

# --- Tranches de marge ---
st.subheader("📊 Répartition des ventes par tranche de marge")

df_tranches = pd.DataFrame(rentabilite['tranches_marge'])

col_t1, col_t2 = st.columns([2, 1])

with col_t1:
    fig_tranches = px.bar(
        df_tranches,
        x='tranche',
        y='ca',
        color='tranche',
        title="Chiffre d'affaires par tranche de marge",
        labels={'tranche': 'Tranche de marge', 'ca': 'CA (€)', 'nb_lignes': 'Lignes de commande'},
        text='nb_lignes',
        color_discrete_sequence=['#e74c3c', '#f39c12', '#2ecc71', '#1abc9c'],
        height=350
    )
    fig_tranches.update_traces(texttemplate='%{text} lignes', textposition='outside')
    st.plotly_chart(fig_tranches, use_container_width=True)

with col_t2:
    st.markdown("#### 🎯 Lecture décisionnelle")
    total_ca = df_tranches['ca'].sum()
    for _, row in df_tranches.iterrows():
        pct = row['ca'] / total_ca * 100 if total_ca > 0 else 0
        st.metric(row['tranche'], f"{pct:.1f}% du CA")

# --- Remises par catégorie ---
st.subheader("🏷️ Taux de remise moyen par catégorie")
df_remises = pd.DataFrame(rentabilite['remises_par_categorie'])

col_r1, col_r2 = st.columns(2)

with col_r1:
    fig_remises = px.bar(
        df_remises,
        x='categorie',
        y='remise_moy',
        title="Remise moyenne appliquée par catégorie (%)",
        labels={'categorie': 'Catégorie', 'remise_moy': 'Remise moyenne (%)'},
        color='remise_moy',
        color_continuous_scale='RdYlGn_r',
        text='remise_moy',
        height=350
    )
    fig_remises.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    st.plotly_chart(fig_remises, use_container_width=True)

with col_r2:
    st.markdown("#### ⚠️ Alerte remises")
    for row in rentabilite['remises_par_categorie']:
        if row['remise_moy'] > 20:
            st.error(f"🔴 **{row['categorie']}** : remise de {row['remise_moy']:.1f}% — impact fort sur les marges")
        elif row['remise_moy'] > 10:
            st.warning(f"🟡 **{row['categorie']}** : remise de {row['remise_moy']:.1f}% — à surveiller")
        else:
            st.success(f"🟢 **{row['categorie']}** : remise de {row['remise_moy']:.1f}% — sous contrôle")

# --- Produits déficitaires ---
st.subheader("🚨 Top 10 Produits Déficitaires")
df_def = pd.DataFrame(rentabilite['produits_deficitaires'])
if not df_def.empty:
    fig_def = px.bar(
        df_def,
        x='profit',
        y='produit',
        orientation='h',
        color='categorie',
        title="Produits générant des pertes (profit négatif)",
        labels={'profit': 'Profit (€)', 'produit': 'Produit'},
        color_discrete_sequence=px.colors.qualitative.Set2,
        height=400
    )
    fig_def.update_layout(yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig_def, use_container_width=True)

    with st.expander("📋 Tableau détaillé des produits déficitaires"):
        st.dataframe(
            df_def[['produit', 'categorie', 'profit', 'ca', 'remise_moy', 'marge_pct']].rename(columns={
                'produit': 'Produit', 'categorie': 'Catégorie',
                'profit': 'Profit (€)', 'ca': 'CA (€)',
                'remise_moy': 'Remise moy.', 'marge_pct': 'Marge (%)'
            }),
            use_container_width=True, hide_index=True
        )

st.divider()

# === SECTION 5 : TENDANCES & SAISONNALITÉ ===
st.header("📐 Tendances & Saisonnalité")

with st.spinner("📈 Calcul des tendances..."):
    tendances = appeler_api("/kpi/tendances")

df_mensuel = pd.DataFrame(tendances['mensuel'])

col_m1, col_m2 = st.columns([2, 1])

with col_m1:
    # Graphique MoM
    df_mom = df_mensuel.dropna(subset=['ca_mom_pct'])  # Exclut le premier mois sans valeur

    fig_mom = go.Figure()
    fig_mom.add_trace(go.Bar(
        x=df_mom['mois'],
        y=df_mom['ca_mom_pct'],
        name='Croissance MoM (%)',
        marker_color=df_mom['ca_mom_pct'].apply(lambda v: '#2ecc71' if v >= 0 else '#e74c3c'),
        text=df_mom['ca_mom_pct'].apply(lambda v: f"{v:+.1f}%"),
        textposition='outside'
    ))
    fig_mom.update_layout(
        title="Croissance mensuelle du CA (Mois sur Mois)",
        xaxis_title="Mois",
        yaxis_title="Variation (%)",
        height=400
    )
    st.plotly_chart(fig_mom, use_container_width=True)

with col_m2:
    st.markdown("#### 🏆 Records historiques")
    m = tendances['meilleur_mois']
    p = tendances['pire_mois']
    st.success(f"**Meilleur mois** : {m['mois']}\n\nCA : {m['ca']:,.0f} €")
    st.error(f"**Pire mois** : {p['mois']}\n\nCA : {p['ca']:,.0f} €")

# Graphique trimestriel
df_trim = pd.DataFrame(tendances['trimestriel'])
fig_trim = px.bar(
    df_trim,
    x='trimestre',
    y=['ca', 'profit'],
    title="Performance par trimestre",
    labels={'value': 'Montant (€)', 'trimestre': 'Trimestre', 'variable': 'Indicateur'},
    barmode='group',
    color_discrete_map={'ca': '#3498db', 'profit': '#2ecc71'},
    height=380
)
st.plotly_chart(fig_trim, use_container_width=True)

st.divider()

# === SECTION 6 : ANALYSE RFM ===
st.header("🎯 Segmentation Clients — Analyse RFM")
st.markdown("""
> **RFM** = **R**écence (dernier achat), **F**réquence (nb de commandes), **M**ontant (CA total)  
> Cette segmentation permet d'identifier les clients à fidéliser, réactiver ou conquérir.
""")

with st.spinner("🔍 Calcul de la segmentation RFM..."):
    rfm_data = appeler_api("/kpi/clients/rfm")

df_rfm_resume = pd.DataFrame(rfm_data['resume_segments'])

# Graphique segments RFM
col_rfm1, col_rfm2 = st.columns(2)

with col_rfm1:
    fig_rfm_nb = px.pie(
        df_rfm_resume,
        values='nb_clients',
        names='segment',
        title="Répartition des clients par segment RFM",
        color_discrete_sequence=['#1abc9c', '#3498db', '#f39c12', '#e74c3c'],
        height=380
    )
    fig_rfm_nb.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_rfm_nb, use_container_width=True)

with col_rfm2:
    fig_rfm_ca = px.bar(
        df_rfm_resume,
        x='segment',
        y='montant_moyen',
        title="Montant moyen par segment RFM",
        labels={'segment': 'Segment', 'montant_moyen': 'Montant moyen (€)'},
        color='segment',
        color_discrete_sequence=['#1abc9c', '#3498db', '#f39c12', '#e74c3c'],
        text='montant_moyen',
        height=380
    )
    fig_rfm_ca.update_traces(texttemplate='%{text:,.0f}€', textposition='outside')
    st.plotly_chart(fig_rfm_ca, use_container_width=True)

# Tableau RFM + recommandations
st.subheader("📋 Recommandations par segment")
recommandations = {
    'Champions':        ('🥇', '#1abc9c', "Ces clients achètent souvent et récemment. **Fidélisez-les** avec des offres exclusives et programmes VIP."),
    'Fidèles':          ('🤝', '#3498db', "Clients réguliers mais pas nécessairement récents. **Proposez des ventes croisées** et upselling."),
    'À risque':         ('⚠️', '#f39c12', "N'ont pas acheté depuis un moment. **Lancez une campagne de réactivation** avec une offre personnalisée."),
    'Perdus / Inactifs':('💤', '#e74c3c', "Clients très inactifs. **Décidez** : campagne de reconquête ou abandon. Coût de réactivation élevé."),
}

for _, row in df_rfm_resume.iterrows():
    seg = row['segment']
    if seg in recommandations:
        emoji, color, conseil = recommandations[seg]
        with st.expander(f"{emoji} **{seg}** — {row['nb_clients']} clients | Montant moyen : {row['montant_moyen']:,.0f} €"):
            st.markdown(f"**Récence moyenne** : {row['recence_moyenne']:.0f} jours | "
                        f"**Fréquence moyenne** : {row['frequence_moyenne']:.1f} commandes")
            st.info(conseil)

# TOP 10 clients detail
with st.expander("🔍 Voir le détail des 50 meilleurs clients RFM"):
    df_detail = pd.DataFrame(rfm_data['detail_clients'])
    st.dataframe(
        df_detail[['nom', 'recence', 'frequence', 'montant', 'score_rfm', 'segment']].rename(columns={
            'nom': 'Client', 'recence': 'Récence (j)', 'frequence': 'Fréquence',
            'montant': 'Montant (€)', 'score_rfm': 'Score RFM', 'segment': 'Segment'
        }),
        use_container_width=True, hide_index=True
    )

st.divider()

# === SECTION 7 : RECOMMANDATIONS DÉCISIONNELLES ===
st.header("🧭 Synthèse & Recommandations Décisionnelles")
st.markdown("""
> Cette section transforme les indicateurs en **messages actionnables** — c'est l'essence du data storytelling.
""")

col_rec1, col_rec2, col_rec3 = st.columns(3)

with col_rec1:
    st.markdown("### 🔍 Constats")
    df_def_check = pd.DataFrame(rentabilite['produits_deficitaires'])
    nb_def = len(df_def_check)
    remise_max = max(r['remise_moy'] for r in rentabilite['remises_par_categorie'])
    cat_risque = next(r['categorie'] for r in rentabilite['remises_par_categorie'] if r['remise_moy'] == remise_max)

    st.warning(f"⚠️ **{nb_def} produits déficitaires** identifiés dans le catalogue")
    st.warning(f"⚠️ La catégorie **{cat_risque}** affiche la remise la plus élevée ({remise_max:.1f}%)")

    seg_perdus = next((r for r in rfm_data['resume_segments'] if r['segment'] == 'Perdus / Inactifs'), None)
    if seg_perdus:
        st.warning(f"⚠️ **{seg_perdus['nb_clients']} clients inactifs** n'ont pas commandé depuis longtemps")

with col_rec2:
    st.markdown("### 🎯 Actions prioritaires")
    st.success("✅ **Réduire les remises** sur les catégories à faible marge pour restaurer la rentabilité")
    st.success("✅ **Revoir ou retirer** les produits déficitaires chroniques du catalogue")
    st.success("✅ **Lancer une campagne** de réactivation ciblée sur les clients 'À risque'")
    st.success("✅ **Renforcer les offres** pour les clients Champions (programme fidélité)")

with col_rec3:
    st.markdown("### 📈 Opportunités")
    seg_champ = next((r for r in rfm_data['resume_segments'] if r['segment'] == 'Champions'), None)
    if seg_champ:
        st.info(f"💎 **{seg_champ['nb_clients']} Champions** : fort potentiel d'upselling et d'ambassadeurs")

    meilleur = tendances['meilleur_mois']
    st.info(f"📅 **Saisonnalité** : {meilleur['mois']} est historiquement le meilleur mois — anticipez les stocks")
    st.info("🌍 **Géographie** : analysez les régions sous-performantes via les filtres pour cibler vos actions commerciales")


st.divider()

# === SECTION : TAUX DE RÉTENTION CLIENT ===
st.header("🔁 Taux de Rétention Client")
st.markdown("""
> **Formule** : (Clients avec 2+ commandes / Total clients) × 100  
> Un taux de rétention élevé signifie que les clients reviennent — bien plus rentable que d'en acquérir de nouveaux.
""")

with st.spinner("📊 Calcul de la rétention..."):
    retention_data = appeler_api("/kpi/clients/retention")

# --- KPI principal ---
col_ret1, col_ret2, col_ret3, col_ret4 = st.columns(4)

with col_ret1:
    st.metric(
        label="🔁 Taux de rétention",
        value=f"{retention_data['taux_retention_pct']}%",
        help="(Clients avec 2+ commandes / Total clients) × 100"
    )
with col_ret2:
    st.metric(
        label="👥 Total clients",
        value=formater_nombre(retention_data['total_clients'])
    )
with col_ret3:
    st.metric(
        label="✅ Clients récurrents",
        value=formater_nombre(retention_data['clients_recurrents']),
        help="Ont passé au moins 2 commandes"
    )
with col_ret4:
    st.metric(
        label="⚠️ Clients 1 achat",
        value=formater_nombre(retention_data['clients_1_achat']),
        help="N'ont commandé qu'une seule fois"
    )

# --- Interprétation automatique ---
taux = retention_data['taux_retention_pct']
if taux >= 70:
    st.success(f"✅ **Excellente rétention ({taux}%)** : la majorité des clients reviennent. Maintenez la qualité de service et capitalisez sur ce levier.")
elif taux >= 50:
    st.warning(f"🟡 **Rétention correcte ({taux}%)** : un client sur deux revient. Des actions de fidélisation ciblées permettraient d'améliorer ce ratio.")
else:
    st.error(f"🔴 **Rétention faible ({taux}%)** : plus de la moitié des clients ne reviennent pas. Analysez les causes (qualité, prix, expérience) et lancez des campagnes de réactivation.")

col_rv1, col_rv2 = st.columns(2)

with col_rv1:
    # Distribution du nombre de commandes par client
    df_distrib = pd.DataFrame(retention_data['distribution_commandes'])
    fig_distrib = px.bar(
        df_distrib,
        x='nb_commandes',
        y='nb_clients',
        title="Distribution du nombre de commandes par client",
        labels={'nb_commandes': 'Nombre de commandes', 'nb_clients': 'Nombre de clients'},
        color='nb_clients',
        color_continuous_scale='Blues',
        text='nb_clients',
        height=380
    )
    fig_distrib.update_traces(textposition='outside')
    st.plotly_chart(fig_distrib, use_container_width=True)

with col_rv2:
    # Évolution du taux de rétention par année
    df_ret_annee = pd.DataFrame(retention_data['retention_par_annee'])
    fig_ret_annee = go.Figure()
    fig_ret_annee.add_trace(go.Bar(
        x=df_ret_annee['annee'].astype(str),
        y=df_ret_annee['taux_retention_pct'],
        name='Taux de rétention (%)',
        marker_color='#3498db',
        text=df_ret_annee['taux_retention_pct'].apply(lambda v: f"{v}%"),
        textposition='outside'
    ))
    fig_ret_annee.update_layout(
        title="Évolution du taux de rétention par année",
        xaxis_title="Année",
        yaxis_title="Taux de rétention (%)",
        height=380
    )
    st.plotly_chart(fig_ret_annee, use_container_width=True)

st.divider()

# === SECTION : ABC ANALYSIS DES PRODUITS ===
st.header("📦 ABC Analysis — Analyse Pareto des Produits")
st.markdown("""
> **Principe** : 20% des produits génèrent 80% du CA (loi de Pareto).  
> - **Classe A** 🥇 : 80% du CA cumulé → produits stratégiques à protéger  
> - **Classe B** 🥈 : 15% suivants → importance secondaire  
> - **Classe C** 🥉 : 5% restants → faible valeur, à optimiser ou retirer  
""")

with st.spinner("🔍 Calcul de l'analyse ABC..."):
    abc_data = appeler_api("/kpi/produits/abc")

df_resume_abc = pd.DataFrame(abc_data['resume_abc'])

# --- KPI résumé par classe ---
col_a, col_b, col_c = st.columns(3)
couleurs_abc = {'A': '#2ecc71', 'B': '#f39c12', 'C': '#e74c3c'}
labels_abc   = {
    'A': ('🥇 Classe A', 'Produits stratégiques — 80% du CA'),
    'B': ('🥈 Classe B', 'Importance secondaire — 15% du CA'),
    'C': ('🥉 Classe C', 'Faible contribution — 5% du CA')
}
cols_abc = [col_a, col_b, col_c]

for i, (_, row) in enumerate(df_resume_abc.iterrows()):
    classe = row['classe']
    titre, desc = labels_abc.get(classe, (classe, ''))
    with cols_abc[i]:
        st.metric(
            label=titre,
            value=f"{row['nb_produits']} produits",
            delta=f"{row['ca_pct_total']:.1f}% du CA total"
        )
        st.caption(desc)

# --- Graphiques ABC ---
col_abc1, col_abc2 = st.columns(2)

with col_abc1:
    # Camembert des classes
    fig_abc_pie = px.pie(
        df_resume_abc,
        values='nb_produits',
        names='classe',
        title="Répartition des produits par classe ABC",
        color='classe',
        color_discrete_map={'A': '#2ecc71', 'B': '#f39c12', 'C': '#e74c3c'},
        hole=0.4,
        height=400
    )
    fig_abc_pie.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_abc_pie, use_container_width=True)

with col_abc2:
    # CA par classe
    fig_abc_ca = px.bar(
        df_resume_abc,
        x='classe',
        y='ca_total',
        title="CA total généré par classe ABC",
        labels={'classe': 'Classe ABC', 'ca_total': 'CA (€)'},
        color='classe',
        color_discrete_map={'A': '#2ecc71', 'B': '#f39c12', 'C': '#e74c3c'},
        text='ca_pct_total',
        height=400
    )
    fig_abc_ca.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    st.plotly_chart(fig_abc_ca, use_container_width=True)

# --- Courbe de Pareto ---
st.subheader("📈 Courbe de Pareto — Top 20 produits")
df_pareto = pd.DataFrame(abc_data['top_pareto'])

fig_pareto = make_subplots(specs=[[{"secondary_y": True}]])

fig_pareto.add_trace(
    go.Bar(
        x=df_pareto['produit'].apply(lambda x: x[:30] + '…' if len(x) > 30 else x),
        y=df_pareto['ca'],
        name='CA (€)',
        marker_color=df_pareto['classe'].map({'A': '#2ecc71', 'B': '#f39c12', 'C': '#e74c3c'}),
    ),
    secondary_y=False
)

fig_pareto.add_trace(
    go.Scatter(
        x=df_pareto['produit'].apply(lambda x: x[:30] + '…' if len(x) > 30 else x),
        y=df_pareto['ca_cumule_pct'],
        name='CA cumulé (%)',
        mode='lines+markers',
        line=dict(color='#8e44ad', width=3),
        marker=dict(size=6)
    ),
    secondary_y=True
)

# Ligne de seuil 80%
fig_pareto.add_hline(
    y=80,
    line_dash="dash",
    line_color="red",
    annotation_text="Seuil 80% (Classe A)",
    secondary_y=True
)

fig_pareto.update_layout(
    title="Courbe de Pareto — CA et % cumulé (Top 20 produits)",
    xaxis_title="Produit",
    height=500,
    xaxis_tickangle=-45
)
fig_pareto.update_yaxes(title_text="CA (€)", secondary_y=False)
fig_pareto.update_yaxes(title_text="CA cumulé (%)", secondary_y=True, range=[0, 105])

st.plotly_chart(fig_pareto, use_container_width=True)

# --- Tableau complet avec filtre par classe ---
st.subheader("📋 Catalogue produits classifié ABC")
filtre_classe = st.radio(
    "Afficher la classe",
    options=['Toutes', 'A', 'B', 'C'],
    horizontal=True
)

df_detail_abc = pd.DataFrame(abc_data['detail_complet'])
if filtre_classe != 'Toutes':
    df_detail_abc = df_detail_abc[df_detail_abc['classe'] == filtre_classe]

st.dataframe(
    df_detail_abc[['produit', 'categorie', 'sous_categorie', 'ca', 'ca_pct', 'ca_cumule_pct', 'classe']].rename(columns={
        'produit': 'Produit',
        'categorie': 'Catégorie',
        'sous_categorie': 'Sous-catégorie',
        'ca': 'CA (€)',
        'ca_pct': 'CA (%)',
        'ca_cumule_pct': 'CA cumulé (%)',
        'classe': 'Classe ABC'
    }),
    use_container_width=True,
    hide_index=True
)

# === FOOTER ===
st.divider()
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #7f8c8d;'>
        <p>📊 <b>Superstore BI Dashboard</b> | Propulsé par FastAPI + Streamlit + Plotly</p>
        <p>💡 Dashboard pédagogique pour l'apprentissage de la Business Intelligence</p>
    </div>
    """,
    unsafe_allow_html=True
)
