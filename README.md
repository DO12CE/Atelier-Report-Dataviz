# 🛒 Superstore BI — API FastAPI + Dashboard Streamlit

Système complet d'analyse Business Intelligence (BI) construit sur le dataset **Sample Superstore**. Le projet combine une API backend robuste pour le calcul des indicateurs et un dashboard frontend interactif pour la visualisation et l'aide à la décision.

> **Auteurs** : Mohamed Yanis BENADROUCHE, Cyprien BROCHE, Yousra ZAABAT

---

## 📁 Structure du projet

```
superstore-bi/
│
├── backend/
│   └── main.py          # API FastAPI — calculs, filtres, endpoints KPI
│
├── frontend/
│   └── dashboard.py     # Dashboard Streamlit — visualisations, storytelling
│
├── ressources/
│   └── ...
│
├── docker-compose.yml   # Orchestration des services (backend + frontend)
├── requirements.txt     # Dépendances Python
└── README.md
```

---

## 🛠️ Installation & Démarrage

### Prérequis

- Python 3.9+
- pip
- Docker & Docker Compose (recommandé)

### Option 1 — Avec Docker Compose (recommandé)

```bash
docker-compose up --build
```

> ⚠️ Le flag `--build` est obligatoire au premier lancement ou après toute modification du code.

Une fois les conteneurs démarrés :

| Service | URL | Description |
|---|---|---|
| 🖥️ Dashboard | http://localhost:8501 | Interface Streamlit |
| ⚙️ API Backend | http://localhost:8000 | API FastAPI |
| 📚 Documentation Swagger | http://localhost:8000/docs | Documentation interactive des endpoints |
| 📖 Documentation ReDoc | http://localhost:8000/redoc | Documentation alternative |

> La variable d'environnement `API_URL=http://backend:8000` est gérée automatiquement par Docker Compose — aucune configuration manuelle nécessaire.

### Option 2 — En local sans Docker

#### 1. Installer les dépendances

```bash
pip install -r requirements.txt
```

#### 2. Lancer le backend (API)

```bash
python backend/main.py
```

> API disponible sur `http://localhost:8000`  
> Documentation Swagger interactive : `http://localhost:8000/docs`

#### 3. Lancer le frontend (Dashboard)

```bash
streamlit run frontend/dashboard.py
```

> Dashboard disponible sur `http://localhost:8501`

---

## 📊 KPIs & Analyses implémentés

### 💰 Finance & Rentabilité

| Indicateur | Formule | Impact décisionnel |
|---|---|---|
| CA Total & Profit Total | Somme des ventes / profits | Avec delta vs période précédente (%) |
| Marge moyenne | Profit / CA × 100 | Mesure l'efficacité commerciale |
| ROI par catégorie | Profit / (CA − Profit) × 100 | Identifie les segments les plus rentables |
| Panier moyen | CA / Nb commandes | Pilote la stratégie de montée en gamme |
| Articles par commande | Quantité / Nb commandes | Mesure le cross-selling |
| Tranches de marge | Déficitaire / Faible / Correct / Excellent | Détecte les zones de perte |
| Remise moyenne par catégorie | Moyenne des taux de remise | Évalue l'impact des promotions sur les marges |
| Produits déficitaires | Top 10 produits à profit négatif | Permet de revoir le catalogue ou la politique tarifaire |

### 📦 Produits & Catégories

| Indicateur | Formule | Impact décisionnel |
|---|---|---|
| Top N produits | Classement par CA, Profit ou Quantité | Identifie les best-sellers |
| Performance par catégorie | CA, Profit, Marge, ROI, Nb commandes | Vision macro des segments produits |
| Taux de croissance mensuel (MoM) | ((CA mois N − CA mois N-1) / CA mois N-1) × 100 | Suit la dynamique business en temps réel |
| Performance trimestrielle | CA et Profit agrégés par trimestre | Détecte la saisonnalité |
| Meilleur / Pire mois historique | Détection automatique des extremes | Anticipe les pics et creux d'activité |
| **ABC Analysis (Pareto)** | Classe A = 80% CA cumulé / B = 15% / C = 5% | Optimise la gestion des stocks et la stratégie commerciale |

### 👥 Clients

| Indicateur | Formule | Impact décisionnel |
|---|---|---|
| Top 10 clients par CA | Agrégation par client | Identifie les comptes clés à chouchouter |
| **Taux de rétention client** | (Clients 2+ commandes / Total clients) × 100 | Mesure la fidélisation — plus rentable que l'acquisition |
| Distribution des commandes | Nb clients par tranche de commandes | Révèle le profil de fidélité de la base |
| Évolution de la rétention | Taux de rétention par année | Suit la tendance de fidélisation dans le temps |
| Analyse par segment | Consumer / Corporate / Home Office | Cible les actions marketing par profil |
| **Segmentation RFM** | Score R + Score F + Score M (quartiles) | Classe les clients en Champions / Fidèles / À risque / Perdus |

### 🌍 Géographie

| Indicateur | Description |
|---|---|
| Performance par région | CA, Profit, Clients, Commandes |
| Carte thermique USA | Choroplèthe par État (code ISO) |

---

## 🔌 Endpoints API

| Méthode | Endpoint | Description |
|---|---|---|
| GET | `/` | Informations générales sur l'API et le dataset |
| GET | `/kpi/globaux` | KPI globaux filtrables (date, catégorie, région, segment) |
| GET | `/kpi/comparaison` | Comparaison période courante vs période précédente |
| GET | `/kpi/produits/top` | Top produits par CA, Profit ou Quantité |
| GET | `/kpi/produits/abc` | ABC Analysis — classement Pareto de tous les produits |
| GET | `/kpi/categories` | Performance par catégorie avec ROI |
| GET | `/kpi/temporel` | Évolution temporelle (jour / mois / année) |
| GET | `/kpi/geographique` | Performance par région |
| GET | `/kpi/geographique/états` | Performance par État (avec codes ISO) |
| GET | `/kpi/clients` | Top clients, récurrence, segments |
| GET | `/kpi/clients/retention` | Taux de rétention, distribution, évolution annuelle |
| GET | `/kpi/clients/rfm` | Segmentation RFM des clients |
| GET | `/kpi/rentabilite` | Déficitaires, remises, tranches de marge |
| GET | `/kpi/tendances` | MoM, trimestriel, extremes historiques |
| GET | `/filters/valeurs` | Valeurs disponibles pour les filtres |
| GET | `/data/commandes` | Données brutes paginées |

---

## 🖥️ Sections du Dashboard

### 1. Storytelling & Analyse Comparative
Génération automatique de messages contextuels (alertes, succès, avertissements) basés sur l'évolution du CA et du Profit par rapport à la période précédente.

### 2. KPI Globaux
Huit indicateurs clés avec deltas : CA, Profit, Marge, Commandes, Clients, Panier moyen, Quantité, Articles/commande.

### 3. Analyses Détaillées (4 onglets)
- **🏆 Produits** : Top N produits avec sélecteur de critère et tableau détaillé
- **📦 Catégories** : CA vs Profit et ROI par catégorie
- **📅 Temporel** : Évolution jour/mois/année du CA, Profit et Commandes
- **🌍 Géographique** : Barres par région, camembert clients, carte thermique USA

### 4. Analyse Clients
Top clients, statistiques de récurrence, performance par segment.

### 5. Rentabilité
Répartition par tranche de marge, alertes sur les remises excessives, visualisation des produits déficitaires.

### 6. Tendances & Saisonnalité
Croissance MoM colorée (vert/rouge), records historiques, performance trimestrielle.

### 7. Taux de Rétention Client
Taux global avec interprétation automatique, distribution du nombre de commandes par client, évolution annuelle du taux de rétention.

### 8. ABC Analysis — Pareto des Produits
Résumé par classe (A/B/C), camembert des classes, courbe de Pareto avec seuil 80%, tableau filtrable du catalogue complet.

### 9. Segmentation RFM
Répartition des clients en 4 segments avec montant moyen, récence et recommandations actionnables par segment.

### 10. Synthèse Décisionnelle
Tableau de bord narratif synthétisant les constats, les actions prioritaires et les opportunités détectées automatiquement.

---

## 💡 Choix techniques

| Technologie | Raison |
|---|---|
| **FastAPI** | Validation native via Pydantic, documentation Swagger automatique, haute performance |
| **Pandas** | Vectorisation des calculs financiers, manipulation des séries temporelles |
| **Plotly** | Graphiques interactifs, support natif des cartes choroplèthes USA |
| **Streamlit** | Déploiement rapide, widgets interactifs, système de cache intégré |
| **Docker Compose** | Orchestration des services backend/frontend, résolution DNS interne (`http://backend:8000`) |
| **`@st.cache_data`** | Évite les appels API redondants lors des changements de filtres |
| **`math.isnan` / `nettoyer_nan()`** | Nettoyage des valeurs `NaN`/`Inf` avant sérialisation JSON (non supportées nativement par `json.dumps`) |

---

## 🗃️ Dataset

**Source** : [Sample Superstore — GitHub](https://github.com/leonism/sample-superstore)

Environ **10 000 transactions** e-commerce couvrant la période **2014–2017**, avec des données de ventes, profits, remises, géographie et segments clients.

---

## 📐 Formules clés

$$
\text{Marge} = \frac{\text{Profit}}{\text{CA}} \times 100
$$

$$
\text{ROI} = \frac{\text{Profit}}{\text{CA} - \text{Profit}} \times 100
$$

$$
\text{Panier moyen} = \frac{\text{CA}}{\text{Nombre de commandes}}
$$

$$
\text{Taux de croissance MoM} = \frac{\text{CA}_N - \text{CA}_{N-1}}{\text{CA}_{N-1}} \times 100
$$

$$
\text{Taux de rétention} = \frac{\text{Clients avec } 2+ \text{ commandes}}{\text{Total clients}} \times 100
$$

$$
\text{Score RFM} = \text{Score}_R + \text{Score}_F + \text{Score}_M \quad \in [3,\ 12]
$$

$$
\text{Classe ABC} = \begin{cases} A & \text{si CA cumulé} \leq 80\% \\ B & \text{si CA cumulé} \leq 95\% \\ C & \text{sinon} \end{cases}
$$