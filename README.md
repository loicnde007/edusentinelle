# 🛡️ EduSentinelle — Système de détection précoce d'abandon scolaire

> Plateforme intelligente de détection de l'abandon scolaire développée dans le cadre d'un mémoire de DIPES II à l'École Normale Supérieure de Bertoua, Cameroun.

---

## 📋 Description

**EduSentinelle** est une application web Streamlit permettant à une équipe pédagogique (enseignants, conseillers, administration) de surveiller les élèves à risque d'abandon scolaire grâce à un moteur de prédiction basé sur un algorithme **Random Forest**.

### Modules principaux

| Module | Rôle |
|--------|------|
| 🏠 **Accueil** | Tableau de bord avec KPIs en temps réel |
| 📝 **Admin** | Inscription des élèves, liste, flux de suivi, diagnostic IA |
| 📊 **Enseignants** | Saisie des notes, absences et comportements |
| 🔍 **Conseiller** | Suivi des élèves à risque et plans d'intervention |
| 💬 **Chat** | Messagerie partagée entre les acteurs |

---

## 🚀 Lancer l'application localement

### Prérequis

- Python 3.9 ou supérieur
- pip

### Installation

```bash
# 1. Cloner le dépôt
git clone https://github.com/TON_USERNAME/EduSentinelle.git
cd EduSentinelle

# 2. Créer un environnement virtuel (recommandé)
python -m venv venv
source venv/bin/activate  # Windows : venv\Scripts\activate

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Lancer l'application
streamlit run app.py
```

L'application s'ouvre automatiquement sur `http://localhost:8501`

---

## 🔐 Comptes de démonstration

| Utilisateur | Mot de passe | Rôle |
|-------------|-------------|------|
| `admin` | `admin123` | Administrateur |
| `enseignant` | `ens123` | Enseignant |
| `conseiller` | `cons123` | Conseiller |

---

## 🗄️ Base de données

L'application utilise **SQLite** par défaut (aucune installation requise). La base de données `edu_database.db` est créée automatiquement au premier lancement.

Pour basculer en mode MySQL (développement local avec XAMPP) :
```python
# Dans app.py, ligne 11 :
DB_MODE = "mysql"  # au lieu de "sqlite"
```

---

## 🤖 Modèle IA

Le fichier `modele_abandon.pkl` (Random Forest entraîné) doit être placé à la racine du projet pour activer le diagnostic IA complet. Sans ce fichier, l'application fonctionne en **mode manuel** avec un calcul de score par règles.

Les 8 variables utilisées par le modèle :
1. Moyenne générale
2. Total des absences
3. Âge de l'élève
4. Distance domicile–école
5. Sexe
6. Situation sanitaire
7. Revenu des parents
8. Statut marital des parents

---

## 🛠️ Stack technique

- **Frontend** : Streamlit + HTML/CSS/JS personnalisé
- **Backend** : Python 3.x
- **Base de données** : SQLite (prod) / MySQL (dev)
- **Machine Learning** : scikit-learn (Random Forest)
- **Visualisation** : Canvas JS, SVG, Plotly (via Streamlit)

---

## 📁 Structure du projet

```
EduSentinelle/
├── app.py                  # Application principale
├── requirements.txt        # Dépendances Python
├── .gitignore
├── README.md
├── .streamlit/
│   └── config.toml         # Configuration thème Streamlit
├── modele_abandon.pkl      # Modèle IA (non versionné)
└── images/                 # Photos pour le slideshow login (non versionné)
```

---

## 👨‍💻 Auteur

Développé par **Loïc** — Étudiant en informatique, ENS Bertoua  
Encadré par **Dr. ATANGANA Virginie**  
Année académique 2025–2026

---

## 📄 Licence

Projet académique — Usage éducatif uniquement.
