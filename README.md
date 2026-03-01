# 🛒 Superstore BI — API FastAPI + Dashboard Streamlit

Système complet d'analyse Business Intelligence (BI) construit sur le dataset **Sample Superstore**. Le projet combine une API backend robuste pour le calcul des indicateurs et un dashboard frontend interactif pour la visualisation et l'aide à la décision.

> **Auteurs** : Mohamed Yanis BENADROUCHE, Cyprien BROCHE, Yousra ZAABAT

> **Légende** : ⬜ Fonctionnalité présente dans la version de base — 🟩 Ajout réalisé dans le cadre de l'atelier

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

#### 3. Lancer le frontend (Dashboard)

```bash
streamlit run frontend/dashboard.py
```

---

## 📊 KPIs & Analyses implémentés

### 💰 Finance & Rentabilité

| Indicateur | Formule | Impact décisionnel | |
|---|---|---|---|
| CA Total & Profit Total | Somme des ventes / profits | Suivi global de l'activité | ⬜ |
| Nombre de commandes | Count distinct Order ID | Volume d'activité | ⬜ |
| Nombre de clients | Count distinct Customer ID | Taille de la base client | ⬜ |
| Panier moyen | CA / Nb commandes | Pilote la stratégie de montée en gamme | ⬜ |
| Marge moyenne | Profit / CA × 100 | Mesure l'efficacité commerciale | ⬜ |
| Articles par commande | Quantité / Nb commandes | Mesure le cross-selling | ⬜ |
| Delta CA & Profit vs période précédente | (CA N − CA N-1) / CA N-1 × 100 | Suit la dynamique en temps réel | 🟩 |
| Tranches de marge | Déficitaire / Faible / Correct / Excellent | Détecte les zones de perte | 🟩 |
| Remise moyenne par catégorie | Moyenne des taux de remise | Évalue l'impact des promotions | 🟩 |
| Produits déficitaires | Top 10 produits à profit négatif | Permet de revoir le catalogue | 🟩 |
| ROI par catégorie | Profit / (CA − Profit) × 100 | Identifie les segments les plus rentables | 🟩 |

### 📦 Produits & Catégories

| Indicateur | Formule | Impact décisionnel | |
|---|---|---|---|
| Top N produits | Classement par CA, Profit ou Quantité | Identifie les best-sellers | ⬜ |
| Répartition CA par catégorie | Agrégation par catégorie | Vision macro des segments produits | ⬜ |
| Évolution CA dans le temps | Agrégation jour / mois / année | Suivi de l'activité | ⬜ |
| Taux de croissance mensuel (MoM) | ((CA mois N − CA mois N-1) / CA mois N-1) × 100 | Suit la dynamique business en temps réel | 🟩 |
| Performance trimestrielle | CA et Profit par trimestre | Détecte la saisonnalité | 🟩 |
| Meilleur / Pire mois historique | Détection automatique des extremes | Anticipe les pics et creux | 🟩 |
| **ABC Analysis (Pareto)** | Classe A = 80% CA cumulé / B = 15% / C = 5% | Optimise stocks et stratégie commerciale | 🟩 |

### 👥 Clients

| Indicateur | Formule | Impact décisionnel | |
|---|---|---|---|
| Top 10 clients par CA | Agrégation par client | Identifie les comptes clés | ⬜ |
| Clients récurrents vs 1 achat | Count par nb commandes | Vue globale de la fidélité | ⬜ |
| Performance par segment | Consumer / Corporate / Home Office | Cible les actions marketing | ⬜ |
| **Taux de rétention client** | (Clients 2+ commandes / Total clients) × 100 | Mesure la fidélisation | 🟩 |
| Distribution des commandes | Nb clients par tranche de commandes | Révèle le profil de fidélité | 🟩 |
| Évolution de la rétention | Taux de rétention par année | Suit la tendance dans le temps | 🟩 |
| **Segmentation RFM** | Score R + Score F + Score M (quartiles) | Classe les clients en 4 segments actionnables | 🟩 |

### 🌍 Géographie

| Indicateur | Description | |
|---|---|---|
| Performance par région | CA, Profit, Clients, Commandes | ⬜ |
| Carte thermique USA | Choroplèthe par État (code ISO) | 🟩 |

---

## 🔌 Endpoints API

| Méthode | Endpoint | Description | |
|---|---|---|---|
| GET | `/` | Informations générales sur l'API | ⬜ |
| GET | `/kpi/globaux` | KPI globaux filtrables | ⬜ |
| GET | `/kpi/produits/top` | Top produits par CA, Profit ou Quantité | ⬜ |
| GET | `/kpi/categories` | Performance par catégorie | ⬜ |
| GET | `/kpi/temporel` | Évolution temporelle (jour / mois / année) | ⬜ |
| GET | `/kpi/geographique` | Performance par région | ⬜ |
| GET | `/kpi/clients` | Top clients, récurrence, segments | ⬜ |
| GET | `/filters/valeurs` | Valeurs disponibles pour les filtres | ⬜ |
| GET | `/data/commandes` | Données brutes paginées | ⬜ |
| GET | `/kpi/comparaison` | Comparaison période courante vs précédente | 🟩 |
| GET | `/kpi/geographique/états` | Performance par État avec codes ISO | 🟩 |
| GET | `/kpi/rentabilite` | Déficitaires, remises, tranches de marge | 🟩 |
| GET | `/kpi/tendances` | MoM, trimestriel, extremes historiques | 🟩 |
| GET | `/kpi/clients/retention` | Taux de rétention, distribution, évolution | 🟩 |
| GET | `/kpi/clients/rfm` | Segmentation RFM des clients | 🟩 |
| GET | `/kpi/produits/abc` | ABC Analysis — classement Pareto | 🟩 |

---

## 🖥️ Sections du Dashboard

| # | Section | |
|---|---|---|
| 1 | **Storytelling & Analyse Comparative** — alertes dynamiques CA/Profit vs période précédente | 🟩 |
| 2 | **KPI Globaux** — 8 métriques avec deltas | ⬜ (enrichi 🟩) |
| 3 | **Analyses Détaillées** — 4 onglets : Produits, Catégories, Temporel, Géographique | ⬜ (enrichi 🟩) |
| 4 | **Analyse Clients** — Top clients, récurrence, segments | ⬜ |
| 5 | **Rentabilité** — tranches de marge, alertes remises, produits déficitaires | 🟩 |
| 6 | **Tendances & Saisonnalité** — MoM, records historiques, trimestriel | 🟩 |
| 7 | **Taux de Rétention Client** — taux global, distribution, évolution annuelle | 🟩 |
| 8 | **ABC Analysis** — Pareto, courbe cumulée, tableau filtrable par classe | 🟩 |
| 9 | **Segmentation RFM** — 4 segments avec recommandations actionnables | 🟩 |
| 10 | **Synthèse Décisionnelle** — constats, actions prioritaires, opportunités | 🟩 |

---

## 💡 Choix techniques

| Technologie | Raison | |
|---|---|---|
| **FastAPI** | Validation native via Pydantic, documentation Swagger automatique | ⬜ |
| **Pandas** | Vectorisation des calculs financiers, séries temporelles | ⬜ |
| **Plotly** | Graphiques interactifs, cartes choroplèthes USA | ⬜ |
| **Streamlit** | Déploiement rapide, widgets interactifs | ⬜ |
| **`@st.cache_data`** | Évite les appels API redondants lors des changements de filtres | ⬜ |
| **Docker Compose** | Orchestration backend/frontend, DNS interne (`http://backend:8000`) | 🟩 |
| **`math.isnan` / `nettoyer_nan()`** | Nettoyage des `NaN`/`Inf` avant sérialisation JSON | 🟩 |

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