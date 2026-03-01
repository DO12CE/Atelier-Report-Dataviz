# 🛒 Superstore BI - API FastAPI + Dashboard Streamlit

Système complet d'analyse Business Intelligence (BI) utilisant le dataset **Sample Superstore**. Ce projet combine une API robuste pour le calcul des indicateurs et un dashboard interactif pour la visualisation des données.

## 🚀 Évolutions Majeures (Version 1.1)

Cette version apporte des fonctionnalités analytiques avancées qui transforment le projet d'un simple affichage de données en un véritable outil d'aide à la décision.

### 🔹 1. Analyse Comparative Temporelle (Deltas)

* **Nouveauté** : Endpoint `/kpi/comparaison`.
* **Fonctionnalité** : L'API compare désormais la période sélectionnée avec la période précédente de même durée.
* **Impact** : Affichage de **Deltas** (indicateurs de croissance/baisse en %) sur le dashboard pour le CA et le Profit.

### 🔹 2. Indicateur de Rentabilité (ROI)

* **Nouveauté** : Ajout du calcul du **ROI (Return on Investment)** par catégorie.
* **Formule** : 
  $$
  ROI = \frac{Profit}{Sales - Profit} \times 100
  $$
* **Impact** : Permet d'identifier les segments les plus rentables au-delà du simple volume de ventes.

### 🔹 3. Cartographie Dynamique des USA

* **Nouveauté** : Endpoint `/kpi/geographique/états`.
* **Technique** : Implémentation d'un mapping ISO (ex: `California -> CA`) pour la compatibilité avec les cartes Plotly.
* **Impact** : Visualisation par carte thermique (Choroplèthe) pour détecter les zones géographiques sous-performantes.

### 🔹 4. Storytelling Automatisé

* **Nouveauté** : Section "Ce que disent les chiffres" dans le dashboard.
* **Impact** : Génération d'alertes textuelles dynamiques (Success/Warning) basées sur les tendances détectées par l'API.

---

## 📊 KPI Implémentés

### 💰 Finance & Rentabilité

- **CA Total** & **Profit Total** (avec évolution en %)
- **Marge Moyenne** et **ROI** par catégorie
- **Panier Moyen** & **Nombre d'articles par commande**

### 📦 Produits & Catégories

- **Top 10 Produits** par CA, Profit ou Quantité
- **Répartition du CA** par catégorie et sous-catégorie
- **Analyse de la performance croisée** (Ventes vs Profit)

### 👥 Clients & Géographie

- **Top 10 Clients** par CA
- **Taux de fidélisation** (Clients récurrents vs nouveaux)
- **Analyse par Segment** (Consumer, Corporate, Home Office)
- **Carte Thermique** des ventes par État américain

---

## 📁 Structure du Projet

```

superstore-bi/
│
├── backend/
│   └── main.py              # API FastAPI (Calculs, Filtres, Nouveaux Endpoints)
│
├── frontend/
│   └── dashboard.py         # Dashboard Streamlit (Visualisation, Storytelling, Cartes)
│
├── tests/
│   └── test_api.py          # Tests unitaires
│
├── requirements.txt         # Dépendances Python
└── README.md                # Documentation

```

---

## 🛠️ Installation et Démarrage

### 1. Prérequis

- Python 3.9+
- Pip

### 2. Installation des dépendances

```bash
pip install -r requirements.txt

```

### 3. Lancement de l'API (Backend)

```bash
python backend/main.py

```

> L'API est accessible sur `http://localhost:8000`. Consultez la documentation interactive Swagger sur `http://localhost:8000/docs`.

### 4. Lancement du Dashboard (Frontend)

```bash
streamlit run frontend/dashboard.py

```

> Le dashboard s'ouvrira automatiquement sur `http://localhost:8501`.

---

## 💡 Choix Techniques

* **FastAPI** : Choisi pour sa rapidité d'exécution et sa gestion native de la validation de données avec Pydantic.
* **Pandas** : Utilisé pour la vectorisation des calculs financiers et la manipulation des séries temporelles.
* **Plotly** : Pour des graphiques hautement interactifs et la gestion de la cartographie `USA-states`.
* **Streamlit Cache** : Optimisation des performances via `@st.cache_data` pour éviter les appels API redondants lors du changement de filtres.

---

## 🗃️ Dataset Utilisé

**Source** : [Sample Superstore Dataset](https://github.com/leonism/sample-superstore)
Contient environ 10 000 transactions e-commerce (2014-2017) avec des données de ventes, profits, géographie et segments clients.



## 📝 Auteurs

*Mohamed Yanis BENADROUCHE, Cyprien BROCHE et Yousra ZAABAT*
