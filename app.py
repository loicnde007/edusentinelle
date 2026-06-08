import streamlit as st
import pandas as pd
import joblib
import numpy as np

# ════════════════════════════════════════
#   CONFIGURATION BASE DE DONNÉES
#   "mysql"  → développement (XAMPP)
#   "sqlite" → soutenance (sans XAMPP)
# ════════════════════════════════════════
DB_MODE = "sqlite"

def get_connection():
    if DB_MODE == "mysql":
        import mysql.connector
        from mysql.connector import Error
        try:
            conn = mysql.connector.connect(
                host='localhost',
                user='root',
                password='',
                database='edu_db'
            )
            return conn
        except Error as e:
            st.error(f"Connection error: {e}")
            return None
    else:
        import sqlite3
        conn = sqlite3.connect('edu_database.db', check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

def get_cursor(conn, dictionary=False):
    if DB_MODE == "mysql":
        return conn.cursor(dictionary=dictionary)
    else:
        return conn.cursor()

def db_execute(cursor, query, params=()):
    if DB_MODE == "sqlite":
        query = query.replace("%s", "?")
        query = query.replace("AUTO_INCREMENT", "AUTOINCREMENT")
        query = query.replace("INSERT IGNORE", "INSERT OR IGNORE")
    cursor.execute(query, params)

def db_read_sql(query, conn, params=None):
    if DB_MODE == "sqlite":
        query = query.replace("%s", "?")
    if params:
        return pd.read_sql(query, conn, params=params)
    return pd.read_sql(query, conn)

def row_to_dict(row):
    if row is None:
        return None
    if DB_MODE == "sqlite":
        return dict(row)
    return row

def rows_to_dict(rows):
    if not rows:
        return []
    if DB_MODE == "sqlite":
        return [dict(r) for r in rows]
    return rows



# Initialisation de la variable si elle n'existe pas encore
if "last_clear" not in st.session_state:
    # Vous pouvez l'initialiser avec une date par défaut ou None
    st.session_state.last_clear = '1900-01-01' 




def marquer_comme_lu():
    conn = get_connection()
    if conn:
        cursor = get_cursor(conn)
        # On récupère l'ID le plus récent pour dire que l'admin a tout vu jusqu'ici
        db_execute(cursor, "SELECT MAX(id) FROM suivi")
        raw = cursor.fetchone()
        max_id = (raw[0] if raw and raw[0] is not None else 0)
        db_execute(cursor, "UPDATE configuration SET valeur = %s WHERE cle = 'derniere_vue'", (max_id,))
        conn.commit()
        conn.close()




def load_css():
    """Design EduSentinelle — Style LSF Platform"""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700;800&display=swap');

    :root {
        --primary:    #064E3B;
        --primary-2:  #065F46;
        --accent:     #10B981;
        --accent-2:   #34D399;
        --surface:    #FFFFFF;
        --bg:         #F8FAFC;
        --border:     #D1FAE5;
        --text-primary:   #064E3B;
        --text-secondary: #6B7280;
        --sidebar-muted:  #6EE7B7;
    }

    @keyframes fadeInDown {
        from { opacity:0; transform:translateY(-18px); }
        to   { opacity:1; transform:translateY(0); }
    }
    @keyframes slideUp {
        from { opacity:0; transform:translateY(20px); }
        to   { opacity:1; transform:translateY(0); }
    }
    @keyframes pulse-green {
        0%,100% { box-shadow: 0 0 0 0 rgba(16,185,129,0.3); }
        50%      { box-shadow: 0 0 0 8px rgba(16,185,129,0); }
    }
    @keyframes magic-shimmer {
        0%   { background-position: -200% center; }
        100% { background-position: 200% center; }
    }
    @keyframes magic-glow {
        0%,100% { box-shadow: 0 4px 15px rgba(16,185,129,0.4), 0 0 0 0 rgba(52,211,153,0.3); }
        50%      { box-shadow: 0 8px 30px rgba(16,185,129,0.65), 0 0 20px rgba(52,211,153,0.25); }
    }
    @keyframes btn-float {
        0%,100% { transform: translateY(0px); }
        50%      { transform: translateY(-2px); }
    }

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif !important;
        background-color: var(--bg) !important;
    }

    /* ═══════════════════════════════════════
       SIDEBAR
    ═══════════════════════════════════════ */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #064E3B 0%, #065F46 100%) !important;
        border-right: 1px solid rgba(255,255,255,0.08) !important;
        min-width: 270px !important;
    }
    [data-testid="stSidebar"]::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, #10B981, #34D399);
    }

    /* ── Tous les textes de la sidebar en blanc ── */
    [data-testid="stSidebar"] * {
        color: #FFFFFF !important;
    }
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] .stMarkdown h2 {
        color: #FFFFFF !important;
        font-weight: 700 !important;
    }

    /* ── Label "Main Navigation:" ── */
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stRadio > label,
    [data-testid="stSidebar"] p {
        color: #FFFFFF !important;
        font-size: 0.75rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 1.5px !important;
    }

    /* ── Items radio (Accueil, Inscription, etc.) ── */
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
        background: rgba(255,255,255,0.08) !important;
        border: 1px solid rgba(255,255,255,0.18) !important;
        border-radius: 10px !important;
        padding: 10px 14px !important;
        color: #FFFFFF !important;
        font-size: 0.92rem !important;
        font-weight: 600 !important;
        text-transform: none !important;
        letter-spacing: 0 !important;
        transition: all 0.2s !important;
        cursor: pointer !important;
        width: 100% !important;
        margin-bottom: 4px !important;
    }
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover {
        background: rgba(16,185,129,0.25) !important;
        border-color: #34D399 !important;
        color: #FFFFFF !important;
    }
    /* ── Option sélectionnée ── */
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:has(input:checked) {
        background: rgba(16,185,129,0.30) !important;
        border-color: #10B981 !important;
        color: #FFFFFF !important;
        box-shadow: 0 0 0 2px rgba(52,211,153,0.35) !important;
    }
    /* ── Texte enfant des items radio ── */
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label p,
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label span,
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label div {
        color: #FFFFFF !important;
        font-size: 0.92rem !important;
        font-weight: 600 !important;
        text-transform: none !important;
        letter-spacing: 0 !important;
    }
    /* ── Cache TOUS les cercles radio natifs ── */
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] input[type="radio"] {
        display: none !important;
    }
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label > div:first-child {
        display: none !important;
    }
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label > p {
        margin: 0 !important;
    }
    [data-testid="stSidebar"] span[data-baseweb="radio"] > div:first-child {
        display: none !important;
    }
    [data-testid="stSidebar"] hr {
        border-color: rgba(255,255,255,0.15) !important;
    }

    /* ═══════════════════════════════════════
       CONTENU PRINCIPAL
    ═══════════════════════════════════════ */
    .main .block-container {
        padding: 0rem 3rem 2.5rem 3rem !important;
        max-width: 1100px;
    }
    [data-testid="stAppViewContainer"] > .main > div:first-child {
        padding-top: 2rem !important;
    }
    div[data-testid="stDecoration"] { display: none !important; }
    #root > div:nth-child(1) > div > div > div > div > section > div {
        padding-top: 2rem !important;
    }

    /* ═══════════════════════════════════════
       BANNIÈRE AN-HEADER (style LSF)
    ═══════════════════════════════════════ */
    .an-header {
        background: linear-gradient(135deg, #022c22 0%, #065F46 55%, #10B981 100%);
        border-radius: 22px;
        padding: 34px 40px;
        margin-bottom: 28px;
        margin-top: 20px;
        position: relative;
        overflow: hidden;
        animation: fadeInDown 0.6s ease both;
    }
    .an-header::before {
        content: '';
        position: absolute;
        top: -60px; right: -60px;
        width: 220px; height: 220px;
        background: rgba(255,255,255,0.06);
        border-radius: 50%;
    }
    .an-header::after {
        content: '';
        position: absolute;
        bottom: -40px; left: 30%;
        width: 160px; height: 160px;
        background: rgba(255,255,255,0.04);
        border-radius: 50%;
    }
    .an-header h2 {
        color: #FFFFFF !important;
        font-size: 2rem !important;
        font-weight: 800 !important;
        margin: 0 0 8px 0 !important;
        letter-spacing: -0.03em !important;
        position: relative; z-index: 1;
    }
    .an-header p {
        color: rgba(255,255,255,0.75) !important;
        font-size: 0.95rem !important;
        margin: 0 !important;
        font-weight: 500 !important;
        position: relative; z-index: 1;
    }

    /* ═══════════════════════════════════════
       TITRES
    ═══════════════════════════════════════ */
    h1, h2 {
        font-family: 'DM Sans', sans-serif !important;
        color: var(--primary) !important;
        font-weight: 800 !important;
        letter-spacing: -0.03em !important;
        animation: slideUp 0.5s ease both;
    }
    h3, h4 {
        font-family: 'DM Sans', sans-serif !important;
        color: var(--primary-2) !important;
        font-weight: 700 !important;
    }

    /* ═══════════════════════════════════════
       ✨ BOUTONS MAGIQUES
    ═══════════════════════════════════════ */
    .stButton > button {
        font-family: 'DM Sans', sans-serif !important;
        font-weight: 700 !important;
        font-size: 0.92rem !important;
        border-radius: 14px !important;
        padding: 12px 28px !important;
        border: none !important;
        position: relative !important;
        overflow: hidden !important;
        color: #FFFFFF !important;
        letter-spacing: 0.03em !important;
        cursor: pointer !important;

        /* Dégradé animé façon "shimmer magique" */
        background: linear-gradient(
            120deg,
            #065F46 0%,
            #10B981 30%,
            #34D399 50%,
            #10B981 70%,
            #065F46 100%
        ) !important;
        background-size: 200% auto !important;
        animation: magic-shimmer 3s linear infinite, magic-glow 2.5s ease-in-out infinite !important;

        /* Ombre douce avec halo vert */
        box-shadow:
            0 4px 15px rgba(16,185,129,0.45),
            0 1px 3px rgba(0,0,0,0.15),
            inset 0 1px 0 rgba(255,255,255,0.20) !important;

        transition: transform 0.18s cubic-bezier(.4,0,.2,1),
                    box-shadow 0.18s cubic-bezier(.4,0,.2,1) !important;
    }

    /* Ligne lumineuse en ::before */
    .stButton > button::before {
        content: '' !important;
        position: absolute !important;
        top: 0 !important; left: -75% !important;
        width: 50% !important; height: 100% !important;
        background: linear-gradient(
            to right,
            rgba(255,255,255,0) 0%,
            rgba(255,255,255,0.28) 50%,
            rgba(255,255,255,0) 100%
        ) !important;
        transform: skewX(-20deg) !important;
        transition: left 0.55s ease !important;
    }
    .stButton > button:hover::before {
        left: 130% !important;
    }

    .stButton > button:hover {
        transform: translateY(-3px) scale(1.03) !important;
        box-shadow:
            0 10px 32px rgba(16,185,129,0.60),
            0 4px 10px rgba(0,0,0,0.12),
            inset 0 1px 0 rgba(255,255,255,0.25) !important;
        animation: magic-shimmer 1.5s linear infinite, btn-float 2s ease-in-out infinite !important;
    }

    .stButton > button:active {
        transform: translateY(-1px) scale(0.98) !important;
        box-shadow: 0 4px 12px rgba(16,185,129,0.35) !important;
    }

    /* Bouton dans les formulaires (form_submit_button) */
    .stFormSubmitButton > button {
        font-family: 'DM Sans', sans-serif !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        border-radius: 14px !important;
        padding: 13px 32px !important;
        border: none !important;
        position: relative !important;
        overflow: hidden !important;
        color: #FFFFFF !important;
        letter-spacing: 0.03em !important;
        background: linear-gradient(
            120deg,
            #022c22 0%,
            #065F46 25%,
            #10B981 50%,
            #065F46 75%,
            #022c22 100%
        ) !important;
        background-size: 200% auto !important;
        animation: magic-shimmer 3s linear infinite, magic-glow 2.5s ease-in-out infinite !important;
        box-shadow:
            0 5px 18px rgba(16,185,129,0.50),
            inset 0 1px 0 rgba(255,255,255,0.20) !important;
        transition: transform 0.18s ease, box-shadow 0.18s ease !important;
    }
    .stFormSubmitButton > button:hover {
        transform: translateY(-3px) scale(1.03) !important;
        box-shadow: 0 12px 35px rgba(16,185,129,0.65) !important;
    }
    .stFormSubmitButton > button:active {
        transform: scale(0.98) !important;
    }

    /* ═══════════════════════════════════════
       MÉTRIQUES / KPI CARDS
    ═══════════════════════════════════════ */
    [data-testid="stMetric"] {
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: 16px !important;
        padding: 20px 24px !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06) !important;
        transition: transform 0.2s, box-shadow 0.2s !important;
        animation: slideUp 0.5s ease both;
    }
    [data-testid="stMetric"]:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 20px rgba(16,185,129,0.15) !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.72rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.1em !important;
        color: var(--primary-2) !important;
    }
    [data-testid="stMetricValue"] {
        font-size: 1.85rem !important;
        font-weight: 800 !important;
        color: var(--primary) !important;
    }

    /* ═══════════════════════════════════════
       ALERTES
    ═══════════════════════════════════════ */
    .stAlert {
        background-color: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-left: 4px solid var(--accent) !important;
        border-radius: 12px !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.04) !important;
    }

    /* ═══════════════════════════════════════
       INPUTS & SELECTBOX
    ═══════════════════════════════════════ */
    input, textarea, [data-baseweb="input"] input {
        border-radius: 10px !important;
        border: 1.5px solid var(--border) !important;
        font-family: 'DM Sans', sans-serif !important;
    }
    input:focus, textarea:focus {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 3px rgba(16,185,129,0.15) !important;
    }
    div[data-baseweb="select"] > div {
        border-radius: 10px !important;
        border: 1.5px solid var(--border) !important;
        background: var(--surface) !important;
    }

    /* ═══════════════════════════════════════
       ONGLETS
    ═══════════════════════════════════════ */
    .stTabs [data-baseweb="tab-list"] {
        background: #F0FDF4 !important;
        border-radius: 12px !important;
        padding: 4px !important;
        border: 1px solid var(--border) !important;
        gap: 2px !important;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 9px !important;
        font-weight: 600 !important;
        color: var(--primary-2) !important;
        padding: 8px 18px !important;
    }
    .stTabs [aria-selected="true"] {
        background: var(--accent) !important;
        color: #FFFFFF !important;
        box-shadow: 0 2px 8px rgba(16,185,129,0.3) !important;
    }

    /* ═══════════════════════════════════════
       DATAFRAME
    ═══════════════════════════════════════ */
    [data-testid="stDataFrame"] {
        border-radius: 12px !important;
        border: 1px solid var(--border) !important;
        overflow: hidden !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06) !important;
    }

    /* ═══════════════════════════════════════
       SCROLLBAR
    ═══════════════════════════════════════ */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: var(--accent-2); border-radius: 99px; }

    </style>
    """, unsafe_allow_html=True)



def vider_le_flux():
    conn = get_connection()
    if conn:
        cursor = get_cursor(conn)
        # On récupère l'ID le plus élevé actuellement dans la table suivi
        db_execute(cursor, "SELECT MAX(id) FROM suivi")
        raw = cursor.fetchone()
        max_id = (raw[0] if raw and raw[0] is not None else 0)
        # On met à jour la configuration pour que 'derniere_vue' soit égal à ce MAX
        db_execute(cursor, "UPDATE configuration SET valeur = %s WHERE cle = 'derniere_vue'", (max_id,))
        conn.commit()
        conn.close()




# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="EduSentinelle - Dropout Detection", 
    page_icon="🛡️", 
    layout="wide"
)
load_css()

# ── Surcharge login : annule les paddings de load_css sur la page connexion ──


# Gestion du compteur de notifications consultées
if 'derniere_consultation' not in st.session_state:
    st.session_state.derniere_consultation = 0

# --- CHARGEMENT DU MODÈLE IA ---
@st.cache_resource
def load_model():
    try:
        return joblib.load('modele_abandon.pkl')
    except:
        return None

model_ia = load_model()
model_statut = "✅ IA Operational" if model_ia else "⚠️ Manual mode (Fichier .pkl absent)"


# Si l'utilisateur clique sur l'onglet Notifications, on enregistre qu'il a "vu" les alertes
# Note : Cette logique sera activée plus bas dans le code



# --- INITIALISATION DES TABLES ---
def init_db():
    conn = get_connection()
    if conn:
        cursor = get_cursor(conn)
        # Table Eleves (11 champs d'inscription)
        db_execute(cursor, """
            CREATE TABLE IF NOT EXISTS eleves (
                matricule TEXT PRIMARY KEY,
                nom TEXT, prenom TEXT, sexe TEXT,
                age INTEGER, classe TEXT, distance_ecole REAL,
                situation_sante TEXT, salaire_parents TEXT,
                nb_enfants INTEGER, statut_marital TEXT
            )
        """)
        db_execute(cursor, """
            CREATE TABLE IF NOT EXISTS configuration (
                cle TEXT PRIMARY KEY,
                valeur INTEGER
            )
        """)
        db_execute(cursor, "INSERT OR IGNORE INTO configuration VALUES ('derniere_vue', 0)")

        db_execute(cursor, """
            CREATE TABLE IF NOT EXISTS suivi (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                matricule_eleve TEXT, note REAL, absences INTEGER,
                comportement TEXT, matiere TEXT,
                classe_concernee TEXT, nom_enseignant TEXT,
                date_saisie DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        db_execute(cursor, """
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                auteur TEXT, role_auteur TEXT,
                message TEXT,
                date_msg DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        cursor.close()
        conn.close()

init_db()

# ══════════════════════════════════════════
#   COMPTES UTILISATEURS (accès complet pour tous)
# ══════════════════════════════════════════
USERS = {
    "admin":      {"password": "admin123", "role": "Admin"},
    "enseignant": {"password": "ens123",   "role": "Teacher"},
    "conseiller": {"password": "cons123",  "role": "Counselor"},
}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_role" not in st.session_state:
    st.session_state.user_role = ""

def get_derniere_vue():
    conn = get_connection()
    valeur = 0
    if conn:
        cursor = get_cursor(conn)
        db_execute(cursor, "SELECT valeur FROM configuration WHERE cle = 'derniere_vue'")
        raw = cursor.fetchone()
        if raw:
            valeur = raw[0] if raw[0] is not None else 0
        conn.close()
    return valeur

def set_derniere_vue(nouvel_id):
    conn = get_connection()
    if conn:
        cursor = get_cursor(conn)
        db_execute(cursor, "UPDATE configuration SET valeur = %s WHERE cle = 'derniere_vue'", (nouvel_id,))
        conn.commit()
        conn.close()



# ══════════════════════════════════════════
#   PAGE LOGIN
# ══════════════════════════════════════════
if not st.session_state.logged_in:

    import os, base64
    from PIL import Image as PILImage
    import io

    # ── Charger les images pour le slideshow (racine du projet) ──
    img_b64_list = []
    for fname in sorted(os.listdir(".")):
        if fname.lower().endswith((".png",".jpg",".jpeg",".webp")) and len(img_b64_list) < 4:
            try:
                img = PILImage.open(fname).convert("RGB")
                img.thumbnail((600, 300), PILImage.LANCZOS)
                buf = io.BytesIO()
                img.save(buf, format="JPEG", quality=70)
                b64 = base64.b64encode(buf.getvalue()).decode()
                img_b64_list.append(b64)
            except:
                pass

    # Construire les balises <img> du slideshow
    slides_tags = ""
    for i, b64 in enumerate(img_b64_list):
        slides_tags += (
            f'<img src="data:image/jpeg;base64,{b64}" '
            f'style="position:absolute;inset:0;width:100%;height:100%;'
            f'object-fit:cover;opacity:0;animation:ssShow 16s {i*4}s infinite"/>'
        )

    # ── Récupérer l'erreur de login éventuelle ──
    error_html = ""
    if st.session_state.get("_login_error"):
        error_html = '''
        <div class="lr-err">❌ Incorrect username or password.</div>'''
        st.session_state["_login_error"] = False

    # ══════════════════════════════════════════════════════
    #  PAGE LOGIN — overlay fixed 100vw×100vh via st.markdown
    #  Le formulaire Streamlit (inputs + bouton) est positionné
    #  dans la zone droite grâce à un wrapper fixed.
    # ══════════════════════════════════════════════════════

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;600;700;800;900&display=swap');
    @keyframes ssShow{{0%,22%{{opacity:1}}27%,97%{{opacity:0}}100%{{opacity:1}}}}
    @keyframes shimmer{{0%{{background-position:-200% center}}100%{{background-position:200% center}}}}
    @keyframes glow{{0%,100%{{box-shadow:0 4px 15px rgba(16,185,129,.45)}}50%{{box-shadow:0 8px 30px rgba(16,185,129,.7)}}}}
    @keyframes fadeIn{{from{{opacity:0;transform:translateY(10px)}}to{{opacity:1;transform:translateY(0)}}}}

    /* ── Masquer tout le chrome Streamlit ── */
    [data-testid="stHeader"], footer, #MainMenu,
    [data-testid="stToolbar"], [data-testid="stDecoration"],
    [data-testid="stStatusWidget"] {{ display:none!important; }}

    /* ── Reset global ── */
    html, body {{
        margin:0!important; padding:0!important;
        background:#F9FAFB!important;
        height:100vh!important; overflow:hidden!important;
    }}

    /* ── Panneau GAUCHE : fixed, couvre 58vw ── */
    #lp-left {{
        position:fixed; top:0; left:0;
        width:58vw; height:100vh;
        background:linear-gradient(150deg,#012118 0%,#064E3B 48%,#059669 100%);
        display:flex; flex-direction:column; justify-content:center;
        padding:32px 44px; box-sizing:border-box;
        overflow:hidden; z-index:1000;
    }}
    #lp-left::before{{content:'';position:absolute;top:-70px;right:-70px;
        width:260px;height:260px;background:rgba(255,255,255,.05);border-radius:50%;}}
    #lp-left::after{{content:'';position:absolute;bottom:-55px;left:8%;
        width:210px;height:210px;background:rgba(52,211,153,.07);border-radius:50%;}}
    .lp-logo{{font-size:2.6rem;text-align:center;margin-bottom:3px;position:relative;z-index:1;}}
    .lp-title{{font-size:1.75rem;font-weight:900;color:#fff;letter-spacing:-.03em;
        text-align:center;margin:0 0 4px;position:relative;z-index:1;}}
    .lp-sub{{font-size:.82rem;color:rgba(255,255,255,.65);text-align:center;line-height:1.5;
        margin:0 0 16px;position:relative;z-index:1;}}
    .lp-ss{{width:100%;border-radius:13px;overflow:hidden;position:relative;height:170px;
        box-shadow:0 6px 24px rgba(0,0,0,.35);margin-bottom:14px;z-index:1;}}
    .lp-ss-ov{{position:absolute;inset:0;
        background:linear-gradient(to top,rgba(1,33,24,.5) 0%,transparent 55%);z-index:1;}}
    .lp-ss-cap{{position:absolute;bottom:8px;left:12px;font-size:.67rem;font-weight:700;
        color:#fff;letter-spacing:.05em;text-shadow:0 1px 5px rgba(0,0,0,.6);z-index:2;}}
    .lp-feats{{display:flex;flex-direction:column;gap:8px;position:relative;z-index:1;}}
    .lp-feat{{display:flex;align-items:center;gap:11px;background:rgba(255,255,255,.09);
        border:1px solid rgba(255,255,255,.13);border-radius:10px;padding:9px 13px;}}
    .lp-fi{{font-size:1rem;width:32px;height:32px;background:rgba(255,255,255,.13);
        border-radius:8px;display:flex;align-items:center;justify-content:center;flex-shrink:0;}}
    .lp-fn{{font-size:.78rem;font-weight:700;color:#fff;}}
    .lp-fd{{font-size:.67rem;color:#6EE7B7;margin-top:1px;}}
    .lp-foot{{margin-top:12px;font-size:.63rem;color:rgba(255,255,255,.27);
        text-align:center;position:relative;z-index:1;}}

    /* ── Panneau DROIT : fond blanc fixed ── */
    #lp-right-bg {{
        position:fixed; top:0; left:58vw;
        width:42vw; height:100vh;
        background:#F9FAFB; z-index:999;
        pointer-events:none;
    }}
    .lr-h{{font-family:'DM Sans',sans-serif;font-size:1.65rem;font-weight:900;
        color:#064E3B;letter-spacing:-.03em;margin:0 0 4px;}}
    .lr-s{{font-family:'DM Sans',sans-serif;font-size:.81rem;color:#6B7280;margin:0 0 6px;}}
    .lr-f{{font-family:'DM Sans',sans-serif;font-size:.64rem;color:#9CA3AF;
        text-align:center;margin-top:10px;}}
    .lr-err{{background:#FEF2F2;border:1px solid #FCA5A5;border-left:4px solid #EF4444;
        border-radius:10px;padding:10px 14px;margin-bottom:12px;
        font-size:.82rem;color:#991B1B;font-weight:600;font-family:'DM Sans',sans-serif;}}

    /* ── Décaler tout le contenu Streamlit vers la droite ──
       On pousse le stMain (le scroll container) et on center verticalement */
    [data-testid="stMain"] {{
        padding-left: 58vw !important;
        background: #F9FAFB !important;
        display: flex !important;
        align-items: center !important;
        min-height: 100vh !important;
    }}
    [data-testid="stMain"] > div {{
        width: 42vw !important;
        padding: 0 52px !important;
        box-sizing: border-box !important;
    }}
    .main .block-container {{
        padding: 0 !important;
        max-width: 100% !important;
        width: 100% !important;
    }}

    /* Labels inputs */
    label[data-testid="stWidgetLabel"] p {{
        font-family:'DM Sans',sans-serif!important; font-size:.68rem!important;
        font-weight:800!important; text-transform:uppercase!important;
        letter-spacing:1.1px!important; color:#064E3B!important;
    }}
    /* Inputs */
    input[type="text"], input[type="password"] {{
        font-family:'DM Sans',sans-serif!important; font-size:.88rem!important;
        border-radius:9px!important; border:1.5px solid #D1FAE5!important;
        background:#fff!important; color:#111!important;
        transition:border-color .2s,box-shadow .2s!important;
    }}
    input[type="text"]:focus, input[type="password"]:focus {{
        border-color:#10B981!important;
        box-shadow:0 0 0 3px rgba(16,185,129,.15)!important;
    }}
    /* Bouton */
    .stButton > button {{
        background:linear-gradient(120deg,#065F46 0%,#10B981 30%,#34D399 50%,#10B981 70%,#065F46 100%)!important;
        background-size:200% auto!important;
        animation:shimmer 3s linear infinite,glow 2.5s ease-in-out infinite!important;
        color:#fff!important; font-weight:700!important; border-radius:14px!important;
        border:none!important; font-size:.95rem!important;
    }}
    /* Cacher les éléments Streamlit inutiles sur la page login */
    [data-testid="stSidebar"] {{ display:none!important; }}
    </style>

    <div id="lp-left">
      <div class="lp-logo">🛡️</div>
      <div class="lp-title">EduSentinelle</div>
      <div class="lp-sub">Intelligent early dropout<br>detection system</div>
      <div class="lp-ss">
        {slides_tags}
        <div class="lp-ss-ov"></div>
        <div class="lp-ss-cap">📸 School Preview</div>
      </div>
      <div class="lp-feats">
        <div class="lp-feat"><div class="lp-fi">🎓</div><div><div class="lp-fn">Student Tracking</div><div class="lp-fd">Grades, absences, behavior</div></div></div>
        <div class="lp-feat"><div class="lp-fi">🔮</div><div><div class="lp-fn">AI Diagnosis</div><div class="lp-fd">Dropout risk prediction</div></div></div>
        <div class="lp-feat"><div class="lp-fi">🔔</div><div><div class="lp-fn">Real-Time Alerts</div><div class="lp-fd">Immediate counselor notifications</div></div></div>
        <div class="lp-feat"><div class="lp-fi">💬</div><div><div class="lp-fn">Shared Messaging</div><div class="lp-fd">Teacher &amp; admin collaboration</div></div></div>
      </div>
      <div class="lp-foot">EduSentinelle v1.0 · © 2025–2026</div>

      <!-- Canvas particules JS -->
      <canvas id="lp-canvas" style="position:absolute;inset:0;width:100%;height:100%;pointer-events:none;z-index:0;"></canvas>
    </div>

    <script>
    (function() {{
      const cvs = document.getElementById('lp-canvas');
      if (!cvs) return;
      function resize() {{
        cvs.width  = cvs.parentElement.offsetWidth  || window.innerWidth * 0.58;
        cvs.height = cvs.parentElement.offsetHeight || window.innerHeight;
      }}
      resize();
      const ctx2 = cvs.getContext('2d');
      const pts = Array.from({{length:30}}, () => ({{
        x: Math.random()*cvs.width,
        y: Math.random()*cvs.height,
        r: Math.random()*2+.8,
        vy: -(Math.random()*.5+.2),
        vx: (Math.random()-.5)*.3,
        a: Math.random()*.45+.15
      }}));
      function draw() {{
        ctx2.clearRect(0,0,cvs.width,cvs.height);
        pts.forEach(p => {{
          ctx2.beginPath();
          ctx2.arc(p.x,p.y,p.r,0,Math.PI*2);
          ctx2.fillStyle=`rgba(52,211,153,${{p.a}})`;
          ctx2.fill();
          p.x+=p.vx; p.y+=p.vy;
          if(p.y<0){{p.y=cvs.height; p.x=Math.random()*cvs.width;}}
          if(p.x<0||p.x>cvs.width){{p.vx*=-1;}}
        }});
        requestAnimationFrame(draw);
      }}
      draw();
    }})();
    </script>
    """, unsafe_allow_html=True)

    # Titre + formulaire dans le flux Streamlit (zone droite)
    if error_html:
        st.markdown(error_html, unsafe_allow_html=True)
    st.markdown('<p class="lr-h">Login</p>', unsafe_allow_html=True)
    st.markdown('<p class="lr-s">Enter your credentials to access your space</p>', unsafe_allow_html=True)
    login_id  = st.text_input("USERNAME", placeholder="Enter your username")
    login_pwd = st.text_input("PASSWORD", type="password", placeholder="Enter your password")
    if st.button("🚀 Sign In", use_container_width=True):
        u = USERS.get(login_id.strip().lower())
        if u and login_pwd == u["password"]:
            st.session_state.logged_in = True
            st.session_state.user_role = u["role"]
            st.rerun()
        else:
            st.session_state["_login_error"] = True
            st.rerun()
    st.markdown('<p class="lr-f">EduSentinelle Pro v1.0 · © 2025–2026</p>', unsafe_allow_html=True)
    st.stop()

# ══════════════════════════════════════════
#   APPLICATION (utilisateur connecté)
# ══════════════════════════════════════════

# --- NAVIGATION ---
with st.sidebar:
    st.markdown(f'''
        <div style="text-align:center;padding:24px 0 16px 0;">
            <div style="font-size:2.8rem;">🛡️</div>
            <h2 style="color:white;font-size:1.25rem;font-weight:800;margin:8px 0 4px 0;letter-spacing:-0.02em;">
                EduSentinelle
            </h2>
            <p style="color:#6EE7B7;font-size:0.78rem;margin:0;font-weight:500;">
                Early Dropout Detection
            </p>
        </div>
    ''', unsafe_allow_html=True)

    # ── Horloge live JavaScript ──
    import streamlit.components.v1 as components
    components.html("""
    <style>
      * { box-sizing: border-box; margin: 0; padding: 0; }
      body { background: transparent; }

      @keyframes pulseBlue {
        0%, 100% { box-shadow: 0 0 0 0 rgba(96,165,250,0.5); }
        50%       { box-shadow: 0 0 0 5px rgba(96,165,250,0); }
      }

      .clock-row {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 7px;
        background: rgba(255,255,255,0.07);
        border: 1px solid rgba(255,255,255,0.13);
        border-radius: 9px;
        padding: 7px 12px;
        margin: 0 4px 4px 4px;
      }
      .clock-dot {
        width: 7px; height: 7px;
        background: #60A5FA;
        border-radius: 50%;
        flex-shrink: 0;
        animation: pulseBlue 2s ease-in-out infinite;
      }
      .clock-time {
        font-size: 0.8rem;
        font-weight: 800;
        color: #93C5FD;
        letter-spacing: 0.06em;
        font-family: monospace;
      }
      .clock-date {
        font-size: 0.68rem;
        font-weight: 700;
        color: #6EE7B7;
        letter-spacing: 0.03em;
        font-family: monospace;
        margin-left: 2px;
      }
    </style>

    <div class="clock-row">
      <div class="clock-dot"></div>
      <span class="clock-time" id="live-clock">--:--:--</span>
      <span class="clock-date" id="live-date">--/--/----</span>
    </div>

    <script>
      function updateClock() {
        const now = new Date();
        const h = String(now.getHours()).padStart(2,'0');
        const m = String(now.getMinutes()).padStart(2,'0');
        const s = String(now.getSeconds()).padStart(2,'0');
        const d  = String(now.getDate()).padStart(2,'0');
        const mo = String(now.getMonth()+1).padStart(2,'0');
        const y  = now.getFullYear();
        const el = document.getElementById('live-clock');
        const dt = document.getElementById('live-date');
        if (el) el.textContent = h + ':' + m + ':' + s;
        if (dt) dt.textContent = d + '/' + mo + '/' + y;
      }
      updateClock();
      setInterval(updateClock, 1000);
    </script>
    """, height=48)

    st.markdown("---")

    conn = get_connection()
    nb_alertes = 0
    if conn:
        cursor = get_cursor(conn)
        db_execute(cursor, "SELECT MAX(id) FROM suivi WHERE note < 10")
        raw = cursor.fetchone()
        dernier_id_alerte = (raw[0] if raw and raw[0] is not None else 0)
        vue_permanente = get_derniere_vue()
        if dernier_id_alerte > vue_permanente:
            db_execute(cursor, "SELECT COUNT(*) FROM suivi WHERE note < 10 AND id > %s", (vue_permanente,))
            raw2 = cursor.fetchone()
            nb_alertes = raw2[0] if raw2 else 0
        conn.close()

    label_conseiller = f"Counselor & Monitoring  🔵 {nb_alertes}" if nb_alertes > 0 else "Counselor & Monitoring"

    role = st.radio("Main Navigation:", [
        "Home",
        "Registration & Admin",
        "Teachers Section",
        label_conseiller,
        "💬 Chat"
    ])

    if nb_alertes > 0:
        st.markdown(f'''
            <div style="background:rgba(96,165,250,0.15);border:1px solid #60A5FA;
                border-radius:10px;padding:10px 14px;margin-top:8px;">
                <p style="margin:0;color:#93C5FD;font-size:0.85rem;font-weight:700;">
                    🔵 {nb_alertes} new alert(s)
                </p>
            </div>
        ''', unsafe_allow_html=True)

    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user_role = ""
        st.rerun()


# --- 1. ACCUEIL ---
if role == "Home":
    # ── Stats live ──
    conn = get_connection()
    nb_eleves, nb_alertes = 0, 0
    if conn:
        df_e = db_read_sql("SELECT COUNT(*) as total FROM eleves", conn)
        df_s = db_read_sql("SELECT COUNT(*) as total FROM suivi WHERE note < 10", conn)
        nb_eleves  = int(df_e['total'].iloc[0]) if not df_e.empty else 0
        nb_alertes = int(df_s['total'].iloc[0]) if not df_s.empty else 0
        conn.close()

    ia_label = "Operational" if model_ia else "Manual mode"
    ia_dot   = "#10B981"        if model_ia else "#F59E0B"

    import streamlit.components.v1 as components
    components.html(f"""
<!DOCTYPE html>
<html>
<head>
<style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;600;700;800;900&display=swap');
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'DM Sans', sans-serif; background: #F8FAFC; padding: 0; overflow-x: hidden; }}

  @keyframes wFade    {{ from {{ opacity:0; transform:translateY(-14px); }} to {{ opacity:1; transform:translateY(0); }} }}
  @keyframes wBar     {{ from {{ width:0; }} to {{ width:100%; }} }}
  @keyframes wPop     {{ 0%,100% {{ transform:scale(1); }} 50% {{ transform:scale(1.07); }} }}
  @keyframes shimmer  {{ 0% {{ background-position:-200% center; }} 100% {{ background-position:200% center; }} }}
  @keyframes floatUp  {{ 0% {{ transform:translateY(0) scale(1); opacity:.7; }} 100% {{ transform:translateY(-60px) scale(0.4); opacity:0; }} }}
  @keyframes ripple   {{ 0% {{ transform:scale(0); opacity:.5; }} 100% {{ transform:scale(4); opacity:0; }} }}
  @keyframes pulseGlow{{ 0%,100% {{ box-shadow:0 0 0 0 rgba(16,185,129,.35); }} 50% {{ box-shadow:0 0 0 8px rgba(16,185,129,0); }} }}
  @keyframes slideUp  {{ from {{ opacity:0; transform:translateY(20px); }} to {{ opacity:1; transform:translateY(0); }} }}
  @keyframes countUp  {{ from {{ opacity:0; transform:translateY(10px); }} to {{ opacity:1; transform:translateY(0); }} }}
  @keyframes typewriter {{ from {{ width:0; }} to {{ width:100%; }} }}
  @keyframes blink    {{ 0%,100% {{ border-color:transparent; }} 50% {{ border-color:#34D399; }} }}

  .w-wrap {{ animation: wFade .55s ease both; }}

  /* ── HERO ── */
  .w-hero {{
    background: linear-gradient(135deg,#012118 0%,#064E3B 52%,#059669 100%);
    border-radius: 22px; padding: 36px 42px 30px;
    position: relative; overflow: hidden; margin-bottom: 20px; margin-top: 18px;
  }}
  .w-hero::before {{ content:''; position:absolute; top:-55px; right:-55px;
    width:200px; height:200px; background:rgba(255,255,255,.06); border-radius:50%; }}
  .w-hero::after  {{ content:''; position:absolute; bottom:-45px; left:28%;
    width:170px; height:170px; background:rgba(52,211,153,.07); border-radius:50%; }}

  /* Particules */
  .particle {{
    position: absolute; width: 5px; height: 5px;
    background: rgba(52,211,153,0.6); border-radius: 50%;
    animation: floatUp linear infinite; pointer-events: none; z-index: 0;
  }}

  .w-badge {{
    display: inline-flex; align-items: center; gap: 7px;
    background: rgba(255,255,255,.12); border: 1px solid rgba(255,255,255,.22);
    border-radius: 99px; padding: 5px 14px;
    font-size: .72rem; font-weight: 700; color: #6EE7B7;
    letter-spacing: .06em; margin-bottom: 14px;
  }}
  .w-badge-dot {{
    width: 7px; height: 7px; background: #34D399; border-radius: 50%;
    animation: wPop 2s ease-in-out infinite;
  }}

  /* Titre avec effet typewriter JS */
  .w-title {{
    font-size: 2.1rem; font-weight: 900; color: #fff;
    letter-spacing: -.04em; line-height: 1.15;
    margin: 0 0 8px; position: relative; z-index: 1;
  }}
  .w-sub {{
    font-size: .92rem; color: rgba(255,255,255,.68); font-weight: 500;
    line-height: 1.55; max-width: 580px;
    position: relative; z-index: 1; margin-bottom: 22px;
  }}
  .w-line {{
    height: 2px;
    background: linear-gradient(90deg,#10B981,#34D399,transparent);
    background-size: 200% auto;
    animation: shimmer 3s linear infinite, wBar .8s .3s ease both;
    border-radius: 99px; position: relative; z-index: 1;
  }}
  .w-ia {{
    display: inline-flex; align-items: center; gap: 6px;
    font-size: .72rem; font-weight: 700; color: {ia_dot};
    margin-top: 6px; position: relative; z-index: 1;
  }}
  .w-ia-dot {{
    width: 8px; height: 8px; background: {ia_dot};
    border-radius: 50%; box-shadow: 0 0 0 3px {ia_dot}33;
    animation: wPop 2s ease-in-out infinite;
  }}

  /* ── KPI CARDS ── */
  .w-kpis {{ display: flex; gap: 14px; margin-bottom: 20px; flex-wrap: wrap; }}
  .w-kpi {{
    flex: 1; min-width: 140px; background: #fff;
    border: 1px solid #D1FAE5; border-radius: 16px;
    padding: 18px 20px; box-shadow: 0 2px 8px rgba(0,0,0,.06);
    cursor: default; position: relative; overflow: hidden;
    transition: transform .25s cubic-bezier(.4,0,.2,1), box-shadow .25s;
    animation: slideUp .5s ease both;
  }}
  .w-kpi:hover {{
    transform: translateY(-5px) scale(1.02);
    box-shadow: 0 12px 28px rgba(16,185,129,.2);
    border-color: #10B981;
  }}
  .w-kpi-ripple {{
    position: absolute; border-radius: 50%;
    background: rgba(16,185,129,.18); pointer-events: none;
    width: 10px; height: 10px;
    transform: scale(0); animation: ripple .6s linear;
  }}
  .w-kpi-val {{
    font-size: 1.9rem; font-weight: 900; color: #064E3B;
    letter-spacing: -.04em; animation: countUp .6s ease both;
  }}
  .w-kpi-lbl {{
    font-size: .68rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: .1em; color: #6B7280; margin-top: 2px;
  }}
  .w-kpi-sub {{ font-size: .72rem; color: #10B981; font-weight: 600; margin-top: 4px; }}
  .w-kpi-bar {{
    height: 3px; background: #D1FAE5; border-radius: 99px;
    margin-top: 10px; overflow: hidden;
  }}
  .w-kpi-bar-fill {{
    height: 100%; border-radius: 99px;
    background: linear-gradient(90deg,#10B981,#34D399);
    background-size: 200% auto;
    animation: shimmer 2s linear infinite;
    width: 0; transition: width 1.2s cubic-bezier(.4,0,.2,1);
  }}

  /* ── MODULES ── */
  .w-modules {{
    display: grid; grid-template-columns: repeat(3,1fr);
    gap: 12px; margin-bottom: 20px;
  }}
  .w-mod:nth-child(4) {{ grid-column: 1; }}
  .w-mod:nth-child(5) {{ grid-column: 2; }}
  .w-mod {{
    background: #fff; border: 1px solid #D1FAE5; border-radius: 14px;
    padding: 16px 18px; box-shadow: 0 2px 8px rgba(0,0,0,.05);
    cursor: pointer; position: relative; overflow: hidden;
    transition: transform .2s cubic-bezier(.4,0,.2,1), box-shadow .2s, border-color .2s;
    animation: slideUp .5s ease both;
  }}
  .w-mod:hover {{
    transform: translateY(-4px) scale(1.02);
    box-shadow: 0 12px 28px rgba(16,185,129,.18);
    border-color: #10B981;
  }}
  .w-mod-ripple {{
    position: absolute; border-radius: 50%;
    background: rgba(16,185,129,.15); pointer-events: none;
    width: 10px; height: 10px;
    transform: scale(0); animation: ripple .55s linear;
  }}
  .w-mod-icon {{ font-size: 1.5rem; margin-bottom: 8px; }}
  .w-mod-name {{ font-size: .82rem; font-weight: 800; color: #064E3B; margin-bottom: 3px; }}
  .w-mod-desc {{ font-size: .72rem; color: #6B7280; line-height: 1.4; }}

  /* ── TIP ── */
  .w-tip {{
    display: flex; align-items: center; gap: 11px;
    background: linear-gradient(135deg,#F0FDF4,#ECFDF5);
    border: 1px solid #BBF7D0; border-left: 4px solid #10B981;
    border-radius: 12px; padding: 13px 18px;
    animation: pulseGlow 3s ease-in-out infinite;
  }}
  .w-tip-txt {{ font-size: .82rem; color: #065F46; font-weight: 600; }}

</style>

<div class="w-wrap">

  <!-- HERO avec particules JS -->
  <div class="w-hero" id="hero-box">
    <canvas id="particle-canvas" style="position:absolute;inset:0;width:100%;height:100%;pointer-events:none;z-index:0;"></canvas>
    <div class="w-badge" style="position:relative;z-index:1;"><div class="w-badge-dot"></div>EDUCATIONAL PLATFORM · VERSION 2025</div>
    <div class="w-title" style="position:relative;z-index:1;">Welcome to<br>EduSentinelle 🛡️</div>
    <div class="w-sub" style="position:relative;z-index:1;">Intelligent early detection system for school dropout.<br>
      Analyze, anticipate and intervene before it's too late.</div>
    <div class="w-ia" style="position:relative;z-index:1;"><div class="w-ia-dot"></div>IA · {ia_label}</div>
    <div class="w-line" style="position:relative;z-index:1;margin-top:16px;"></div>
  </div>

  <!-- KPI CARDS avec compteurs animés -->
  <div class="w-kpis">
    <div class="w-kpi" id="kpi-0">
      <div class="w-kpi-val" id="kpi-val-0">0</div>
      <div class="w-kpi-lbl">Enrolled Students</div>
      <div class="w-kpi-sub">↗ Active database</div>
      <div class="w-kpi-bar"><div class="w-kpi-bar-fill" id="bar-0"></div></div>
    </div>
    <div class="w-kpi" id="kpi-1">
      <div class="w-kpi-val" id="kpi-val-1">0</div>
      <div class="w-kpi-lbl">Grades &lt; 10</div>
      <div class="w-kpi-sub">⚠ To monitor</div>
      <div class="w-kpi-bar"><div class="w-kpi-bar-fill" id="bar-1"></div></div>
    </div>
    <div class="w-kpi" id="kpi-2">
      <div class="w-kpi-val" id="kpi-val-2">0</div>
      <div class="w-kpi-lbl">AI Variables</div>
      <div class="w-kpi-sub">✦ Predictive engine</div>
      <div class="w-kpi-bar"><div class="w-kpi-bar-fill" id="bar-2"></div></div>
    </div>
  </div>

  <!-- MODULES avec ripple JS -->
  <div class="w-modules">
    <div class="w-mod js-ripple"><div class="w-mod-icon">📝</div>
      <div class="w-mod-name">Registration &amp; Admin</div>
      <div class="w-mod-desc">Register students, manage the database and run AI diagnostics.</div></div>
    <div class="w-mod js-ripple"><div class="w-mod-icon">📊</div>
      <div class="w-mod-name">Academic Monitoring</div>
      <div class="w-mod-desc">Enter grades, absences and behavior by class and subject.</div></div>
    <div class="w-mod js-ripple"><div class="w-mod-icon">🔔</div>
      <div class="w-mod-name">Notifications</div>
      <div class="w-mod-desc">Real-time alert feed on detected at-risk profiles.</div></div>
    <div class="w-mod js-ripple"><div class="w-mod-icon">🔮</div>
      <div class="w-mod-name">AI Prediction</div>
      <div class="w-mod-desc">Assess dropout risk on a student profile in one click.</div></div>
    <div class="w-mod js-ripple"><div class="w-mod-icon">💬</div>
      <div class="w-mod-name">Messaging</div>
      <div class="w-mod-desc">Exchange space for teachers, counselors and administration.</div></div>
  </div>

  <div class="w-tip">
    <span style="font-size:1.2rem">💡</span>
    <span class="w-tip-txt">Use the side menu to navigate between application modules.</span>
  </div>

</div>

<script>
// ── 1. Compteurs animés ──
function animateCount(id, target, duration) {{
  const el = document.getElementById(id);
  if (!el) return;
  const start = performance.now();
  function step(now) {{
    const progress = Math.min((now - start) / duration, 1);
    const ease = 1 - Math.pow(1 - progress, 3);
    el.textContent = Math.round(ease * target);
    if (progress < 1) requestAnimationFrame(step);
    else el.textContent = (id === 'kpi-val-2') ? target : target;
  }}
  requestAnimationFrame(step);
}}
setTimeout(() => {{
  animateCount('kpi-val-0', {nb_eleves}, 1200);
  animateCount('kpi-val-1', {nb_alertes}, 1000);
  animateCount('kpi-val-2', 8, 800);
  setTimeout(() => {{
    const b0 = document.getElementById('bar-0');
    const b1 = document.getElementById('bar-1');
    const b2 = document.getElementById('bar-2');
    if (b0) b0.style.width = '75%';
    if (b1) b1.style.width = ({nb_alertes} > 0 ? '55%' : '10%');
    if (b2) b2.style.width = '100%';
  }}, 400);
}}, 300);

// ── 3. Ripple effect sur les modules et KPI ──
document.querySelectorAll('.js-ripple, .w-kpi').forEach(el => {{
  el.addEventListener('click', function(e) {{
    const rect = el.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    const ripple = document.createElement('span');
    ripple.className = el.classList.contains('w-kpi') ? 'w-kpi-ripple' : 'w-mod-ripple';
    const size = Math.max(rect.width, rect.height) * 2;
    ripple.style.cssText = `width:${{size}}px;height:${{size}}px;left:${{x - size/2}}px;top:${{y - size/2}}px;position:absolute;`;
    el.appendChild(ripple);
    ripple.addEventListener('animationend', () => ripple.remove());
  }});
}});

// ── 4. Particules canvas sur le hero ──
const canvas = document.getElementById('particle-canvas');
const hero   = document.getElementById('hero-box');
if (canvas && hero) {{
  const ctx = canvas.getContext('2d');
  function resizeCanvas() {{
    canvas.width  = hero.offsetWidth;
    canvas.height = hero.offsetHeight;
  }}
  resizeCanvas();

  const particles = Array.from({{length: 22}}, () => ({{
    x: Math.random() * canvas.width,
    y: Math.random() * canvas.height,
    r: Math.random() * 2.5 + 1,
    vy: -(Math.random() * 0.6 + 0.3),
    vx: (Math.random() - 0.5) * 0.4,
    alpha: Math.random() * 0.5 + 0.2,
  }}));

  function drawParticles() {{
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    particles.forEach(p => {{
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(52,211,153,${{p.alpha}})`;
      ctx.fill();
      p.x += p.vx;
      p.y += p.vy;
      if (p.y < 0) {{ p.y = canvas.height; p.x = Math.random() * canvas.width; }}
    }});
    requestAnimationFrame(drawParticles);
  }}
  drawParticles();
}}
</script>
</html>
""", height=960, scrolling=False)
# --- 2. ADMINISTRATION (FUSIONNÉE) ---
elif role == "Registration & Admin":
    st.markdown("""
    <div class="an-header">
        <h2>🛡️ Admin Space</h2>
        <p>Student registration · Database management · AI Diagnosis</p>
    </div>
    """, unsafe_allow_html=True)
    pwd = st.text_input("Access Code", type="password")
    
    if pwd == "admin123":
        tab_insc, tab_liste, tab_diag, tab_pred = st.tabs([
            "📝 New Registration", "📊 Student List", 
            "🔔 Monitoring Feed", "🔮 AI Diagnosis (8 variables)"
        ])
        
        # TAB 1 : INSCRIPTION
        with tab_insc:

            # CSS Inscription — partie 1
            st.markdown("""
            <style>
            .insc-header {
                background: linear-gradient(135deg,#022c22,#065F46,#10B981);
                border-radius:18px; padding:20px 28px; margin-bottom:22px;
                display:flex; align-items:center; gap:14px;
                box-shadow:0 4px 20px rgba(16,185,129,0.3);
            }
            .insc-header-icon {
                background:rgba(255,255,255,0.15); border-radius:12px;
                padding:10px 14px; font-size:1.5rem;
            }
            .insc-header-title {
                font-size:1.1rem; font-weight:800; color:#fff; letter-spacing:-0.02em;
            }
            .insc-header-sub { font-size:0.78rem; color:#6EE7B7; margin-top:2px; }
            .insc-section {
                background:#fff; border-radius:14px; padding:18px 22px;
                border:1px solid #D1FAE5; margin-bottom:16px;
                box-shadow:0 2px 10px rgba(0,0,0,0.05);
            }
            .insc-section-title {
                font-size:0.72rem; font-weight:800; text-transform:uppercase;
                letter-spacing:0.1em; color:#065F46; margin-bottom:14px;
                display:flex; align-items:center; gap:7px;
            }
            </style>
            """, unsafe_allow_html=True)

            # CSS Inscription — partie 2
            st.markdown("""
            <style>
            .insc-tip {
                background:#F0FDF4; border-left:4px solid #10B981;
                border-radius:10px; padding:12px 16px; margin-top:10px;
                font-size:0.8rem; color:#065F46; font-weight:600;
            }
            </style>
            """, unsafe_allow_html=True)

            # Header
            st.markdown("""
            <div class="insc-header">
                <div class="insc-header-icon">📝</div>
                <div>
                    <div class="insc-header-title">New Registration</div>
                    <div class="insc-header-sub">Register a new student in the database</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            with st.form("form_admin", clear_on_submit=True):
                # Section identité
                st.markdown("""
                <div class="insc-section">
                    <div class="insc-section-title">🪪 Student Identity</div>
                </div>
                """, unsafe_allow_html=True)
                col1, col2 = st.columns(2)
                with col1:
                    mat = st.text_input("Student ID (e.g. 2025XXX)")
                    nom = st.text_input("Last Name")
                    pre = st.text_input("First Name")
                with col2:
                    sex = st.selectbox("Gender", ["M", "F"])
                    age = st.number_input("Age", 5, None, 15)
                    cla = st.selectbox("Class", ["L1", "L2", "L3", "M1", "M2"])

                # Section profil
                st.markdown("""
                <div class="insc-section">
                    <div class="insc-section-title">🏠 Socio-Family Profile</div>
                </div>
                """, unsafe_allow_html=True)
                col3, col4 = st.columns(2)
                with col3:
                    dst = st.number_input("School Distance (km)", 0.0)
                    snt = st.selectbox("Health Situation", ["Low", "Medium", "High"])
                with col4:
                    sal = st.selectbox("Parents Income", ["Poor", "Middle", "Rich", "Millionaire"])
                    enf = st.number_input("Number of children in family", 1)
                    sta = st.selectbox("Parents marital status", ["Single", "Married", "Divorced", "Widowed"])

                st.markdown("""
                <div class="insc-tip">
                    💡 The ID number and name are required to complete registration.
                </div>
                """, unsafe_allow_html=True)

                if st.form_submit_button("✅ Register Student", use_container_width=True):
                    if mat and nom:
                        conn = get_connection()
                        cursor = get_cursor(conn)
                        db_execute(cursor, "INSERT INTO eleves VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                                     (mat, nom, pre, sex, age, cla, dst, snt, sal, enf, sta))
                        conn.commit()
                        conn.close()
                        st.success(f"✅ Student {nom} registered successfully!")
                    else:
                        st.error("⚠️ Please fill in at least the ID number and name.")

        # TAB 2 : LISTE
        with tab_liste:

            # CSS Liste — partie 1
            st.markdown("""
            <style>
            .liste-header {
                background:linear-gradient(135deg,#022c22,#065F46,#10B981);
                border-radius:18px; padding:20px 28px; margin-bottom:22px;
                display:flex; align-items:center; justify-content:space-between;
                box-shadow:0 4px 20px rgba(16,185,129,0.3);
            }
            .liste-header-left { display:flex; align-items:center; gap:14px; }
            .liste-header-icon {
                background:rgba(255,255,255,0.15); border-radius:12px;
                padding:10px 14px; font-size:1.5rem;
            }
            .liste-header-title {
                font-size:1.1rem; font-weight:800; color:#fff; letter-spacing:-0.02em;
            }
            .liste-header-sub { font-size:0.78rem; color:#6EE7B7; margin-top:2px; }
            .liste-badge {
                background:rgba(255,255,255,0.12); border:1.5px solid rgba(255,255,255,0.25);
                border-radius:99px; padding:6px 18px; font-size:0.82rem;
                font-weight:700; color:#fff;
            }
            </style>
            """, unsafe_allow_html=True)

            # CSS Liste — partie 2
            st.markdown("""
            <style>
            .del-zone {
                background:#FEF2F2; border:1.5px solid #FECACA;
                border-radius:14px; padding:18px 22px; margin-top:16px;
            }
            .del-zone-title {
                font-size:0.72rem; font-weight:800; text-transform:uppercase;
                letter-spacing:0.1em; color:#991B1B; margin-bottom:14px;
                display:flex; align-items:center; gap:7px;
            }
            .del-warn {
                font-size:0.78rem; color:#B91C1C; font-weight:600;
                margin-top:10px; padding:8px 12px;
                background:#FEE2E2; border-radius:8px;
            }
            </style>
            """, unsafe_allow_html=True)

            conn = get_connection()
            if conn:
                cursor = get_cursor(conn)
                db_execute(cursor, "SELECT DISTINCT classe FROM eleves ORDER BY classe")
                classes_existantes = [c['classe'] if isinstance(c, dict) else c[0] for c in cursor.fetchall()]

                filtre_cl = st.selectbox("🔍 Filter list by class:", ["All"] + classes_existantes)

                query_liste = "SELECT * FROM eleves"
                if filtre_cl != "All":
                    query_liste += f" WHERE classe = '{filtre_cl}'"

                df_liste = db_read_sql(query_liste, conn)
                nb_eleves = len(df_liste)

                # Header avec compteur dynamique
                st.markdown(f"""
                <div class="liste-header">
                    <div class="liste-header-left">
                        <div class="liste-header-icon">📊</div>
                        <div>
                            <div class="liste-header-title">Student database</div>
                            <div class="liste-header-sub">Browse · Filter · Delete</div>
                        </div>
                    </div>
                    <div class="liste-badge">👥 {nb_eleves} student(s)</div>
                </div>
                """, unsafe_allow_html=True)

                st.dataframe(df_liste, use_container_width=True)

                # Zone suppression
                st.markdown("""
                <div class="del-zone">
                    <div class="del-zone-title">🗑️ Permanent deletion zone</div>
                </div>
                """, unsafe_allow_html=True)

                col_del1, col_del2 = st.columns([3, 1])
                with col_del1:
                    liste_suppr = [f"{r['matricule']} - {r['nom']}" for idx, r in df_liste.iterrows()]
                    eleve_a_supprimer = st.selectbox("Select student to remove:", ["Choose..."] + liste_suppr)
                with col_del2:
                    st.write(" ")
                    if st.button("❌ Delete"):
                        if eleve_a_supprimer != "Choose...":
                            mat_del = eleve_a_supprimer.split(" - ")[0]
                            db_execute(cursor, "DELETE FROM eleves WHERE matricule = %s", (mat_del,))
                            conn.commit()
                            st.success(f"Student {mat_del} deleted!")
                            st.rerun()
                        else:
                            st.error("Please select a student.")

                st.markdown("""
                <div class="del-warn">⚠️ This action is irreversible. The student will be permanently removed from the database.</div>
                """, unsafe_allow_html=True)

                conn.close()



    
        # TAB 3 : DIAGNOSTIC (FLUX)
        with tab_diag:

            # CSS Flux — partie 1 : animation + header + badge
            st.markdown("""
            <style>
            @keyframes slideIn {
                from { opacity: 0; transform: translateY(12px); }
                to   { opacity: 1; transform: translateY(0); }
            }
            .flux-header {
                display: flex; align-items: center; justify-content: space-between;
                background: linear-gradient(135deg, #022c22 0%, #065F46 60%, #10B981 100%);
                border-radius: 18px; padding: 20px 28px; margin-bottom: 20px;
                box-shadow: 0 4px 24px rgba(16,185,129,0.3);
            }
            .flux-header-left { display: flex; align-items: center; gap: 14px; }
            .flux-header-icon {
                background: rgba(255,255,255,0.15); border-radius: 12px;
                padding: 10px 14px; font-size: 1.5rem;
            }
            .flux-header-title {
                font-size: 1.15rem; font-weight: 800; color: #fff; letter-spacing: -0.02em;
            }
            .flux-header-sub {
                font-size: 0.78rem; color: #6EE7B7; font-weight: 500; margin-top: 2px;
            }
            .flux-badge {
                background: rgba(255,255,255,0.12); border: 1.5px solid rgba(255,255,255,0.25);
                border-radius: 99px; padding: 6px 18px; font-size: 0.82rem;
                font-weight: 700; color: #fff;
            }
            </style>
            """, unsafe_allow_html=True)

            # CSS Flux — partie 2 : cartes + état vide
            st.markdown("""
            <style>
            .flux-card {
                display: flex; align-items: center; gap: 14px;
                background: #fff; border-radius: 14px; padding: 14px 18px;
                margin-bottom: 10px; border-left: 4px solid #10B981;
                box-shadow: 0 2px 10px rgba(0,0,0,0.06);
                animation: slideIn 0.4s ease both;
            }
            .flux-card.alerte { border-left-color: #EF4444; }
            .flux-card-icon {
                font-size: 1.3rem; width: 36px; text-align: center; flex-shrink: 0;
            }
            .flux-card-body { flex: 1; min-width: 0; }
            .flux-card-name { font-size: 0.92rem; font-weight: 800; color: #111827; }
            .flux-card-detail { font-size: 0.78rem; color: #6B7280; margin-top: 2px; }
            .flux-card-right { text-align: right; flex-shrink: 0; }
            .flux-note-ok { font-size: 1.05rem; font-weight: 900; color: #10B981; }
            .flux-note-bad { font-size: 1.05rem; font-weight: 900; color: #EF4444; }
            .flux-time { font-size: 0.7rem; color: #9CA3AF; margin-top: 3px; }
            .flux-empty {
                text-align: center; padding: 40px 20px;
                background: #F8FAFC; border-radius: 16px;
                border: 2px dashed #E5E7EB;
            }
            .flux-empty-icon { font-size: 2.5rem; margin-bottom: 10px; }
            .flux-empty-text { font-size: 0.92rem; font-weight: 600; color: #6B7280; }
            </style>
            """, unsafe_allow_html=True)

            # ── Bouton vider tout le flux ──
            if st.button("🧹 Clear feed and reset alerts", type="primary", use_container_width=True):
                from datetime import datetime
                st.session_state.last_clear = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                marquer_comme_lu()
                st.success("Feed cleared and notifications reset!")
                st.rerun()

            conn = get_connection()
            if conn:
                query = f"""
                    SELECT s.id, s.date_saisie, e.matricule, e.nom, e.prenom, e.classe, s.matiere, s.note, s.nom_enseignant 
                    FROM suivi s 
                    JOIN eleves e ON s.matricule_eleve = e.matricule 
                    WHERE s.date_saisie > '{st.session_state.last_clear}'
                    ORDER BY e.classe ASC, s.date_saisie DESC
                """
                df_notif = db_read_sql(query, conn)
                conn.close()

                if not df_notif.empty:
                    nb       = len(df_notif)
                    nb_alert = int((df_notif['note'] < 10).sum())
                    nb_ok    = nb - nb_alert

                    # ── BLOC HEADER GLOBAL ──
                    st.markdown(f"""
                    <div class="flux-header">
                        <div class="flux-header-left">
                            <div class="flux-header-icon">🔔</div>
                            <div>
                                <div class="flux-header-title">Latest entries feed</div>
                                <div class="flux-header-sub">
                                    {nb} notification(s) · 🔴 {nb_alert} alert(s) · ✅ {nb_ok} success
                                </div>
                            </div>
                        </div>
                        <div class="flux-badge">📊 {nb} entry(ies)</div>
                    </div>
                    """, unsafe_allow_html=True)

                    # ── CSS groupes par classe ──
                    st.markdown("""
                    <style>
                    .classe-group-header {
                        display: flex; align-items: center; justify-content: space-between;
                        background: linear-gradient(135deg, #064E3B, #065F46);
                        border-radius: 12px; padding: 12px 18px; margin: 18px 0 10px 0;
                    }
                    .classe-group-title {
                        font-size: 0.95rem; font-weight: 800; color: #fff;
                        display: flex; align-items: center; gap: 8px;
                    }
                    .classe-group-count {
                        background: rgba(255,255,255,0.15); border-radius: 99px;
                        padding: 3px 12px; font-size: 0.78rem; font-weight: 700; color: #6EE7B7;
                    }
                    </style>
                    """, unsafe_allow_html=True)

                    # ── GROUPEMENT PAR CLASSE ──
                    classes_Presentes = df_notif['classe'].unique()

                    for classe in classes_Presentes:
                        df_classe = df_notif[df_notif['classe'] == classe]
                        nb_classe = len(df_classe)
                        nb_alerte_classe = int((df_classe['note'] < 10).sum())

                        # Header du groupe avec bouton supprimer toute la classe
                        col_titre, col_btn = st.columns([4, 1])
                        with col_titre:
                            st.markdown(f"""
                            <div class="classe-group-header">
                                <div class="classe-group-title">🏫 Class {classe}</div>
                                <div class="classe-group-count">
                                    {nb_classe} notification(s) · 🔴 {nb_alerte_classe} alert(s)
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        with col_btn:
                            st.write("")
                            st.write("")
                            if st.button(f"🗑️ Delete all · {classe}", key=f"del_classe_{classe}", use_container_width=True):
                                ids_classe = df_classe['id'].tolist()
                                conn2 = get_connection()
                                if conn2:
                                    cursor2 = get_cursor(conn2)
                                    for sid in ids_classe:
                                        db_execute(cursor2, "DELETE FROM suivi WHERE id = %s", (int(sid),))
                                    conn2.commit()
                                    conn2.close()
                                marquer_comme_lu()
                                st.success(f"All notifications for class {classe} deleted!")
                                st.rerun()

                        # Cartes de la classe avec bouton supprimer individuel
                        for idx, row in df_classe.iterrows():
                            prof       = row['nom_enseignant'] if row['nom_enseignant'] else "Teacher"
                            note       = row['note']
                            is_alerte  = note < 10
                            card_class = "flux-card alerte" if is_alerte else "flux-card"
                            icon       = "⚠️" if is_alerte else "✅"
                            note_class = "flux-note-bad" if is_alerte else "flux-note-ok"
                            date_str   = str(row['date_saisie'])[:16] if row['date_saisie'] else ""
                            notif_id   = int(row['id'])

                            col_card, col_del = st.columns([10, 1])
                            with col_card:
                                st.markdown(f"""
                                <div class="{card_class}">
                                    <div class="flux-card-icon">{icon}</div>
                                    <div class="flux-card-body">
                                        <div class="flux-card-name">{row['nom']} {row['prenom']}</div>
                                        <div class="flux-card-detail">
                                            {row['classe']} &nbsp;·&nbsp; {row['matiere']} &nbsp;·&nbsp; {prof}
                                        </div>
                                    </div>
                                    <div class="flux-card-right">
                                        <div class="{note_class}">{note}/20</div>
                                        <div class="flux-time">{date_str}</div>
                                    </div>
                                </div>""", unsafe_allow_html=True)
                            with col_del:
                                if st.button("✕", key=f"del_notif_{notif_id}", help="Delete this notification"):
                                    conn3 = get_connection()
                                    if conn3:
                                        cursor3 = get_cursor(conn3)
                                        db_execute(cursor3, "DELETE FROM suivi WHERE id = %s", (notif_id,))
                                        conn3.commit()
                                        conn3.close()
                                    marquer_comme_lu()
                                    st.rerun()

                else:
                    # ── ÉTAT VIDE ──
                    st.markdown("""
                    <div class="flux-empty">
                        <div class="flux-empty-icon">✨</div>
                        <div class="flux-empty-text">The feed is empty.<br>All notifications have been processed.</div>
                    </div>
                    """, unsafe_allow_html=True)


        # TAB 4 : PRÉDICTION IA (LES 8 VARIABLES)
        with tab_pred:
            st.header("🔮 Individual Global Diagnosis")
            conn = get_connection()
            if conn:
                cursor = get_cursor(conn)
                db_execute(cursor, "SELECT DISTINCT classe FROM eleves ORDER BY classe")
                liste_classes = [c["classe"] if isinstance(c, dict) else c[0] for c in cursor.fetchall()]
                classe_choisie = st.selectbox("🎯 Filter by Class:", ["All"] + liste_classes)

                query = """
                    SELECT e.*, AVG(s.note) as moyenne_gen, SUM(s.absences) as total_absences, MAX(s.comportement) as dernier_comportement
                    FROM eleves e INNER JOIN suivi s ON e.matricule = s.matricule_eleve 
                """
                if classe_choisie != "All":
                    query += f" WHERE e.classe = '{classe_choisie}'"
                query += " GROUP BY e.matricule "

                df_synthese = db_read_sql(query, conn)
                conn.close()
            
                if not df_synthese.empty:
                    options = [f"{r['matricule']} - {r['nom']} {r['prenom']}" for idx, r in df_synthese.iterrows()]
                    choix = st.selectbox("Select a student for diagnosis:", options)
                    matricule_choisi = choix.split(" - ")[0].strip()
                    filtered = df_synthese[df_synthese['matricule'].astype(str).str.strip() == matricule_choisi]
                    if filtered.empty:
                        st.error("Student not found. Please refresh the page.")
                        st.stop()
                    data = filtered.iloc[0]
                
                    # --- PRÉPARATION DES 8 VARIABLES POUR L'IA ---
                    map_sante = {"Low": 0, "Medium": 1, "High": 2}
                    map_revenu = {"Poor": 0, "Middle": 1, "Rich": 2, "Millionaire": 3}
                    map_marital = {"Single": 0, "Married": 1, "Divorced": 2, "Widowed": 3}
                    map_sexe = {"F": 0, "M": 1}

                    v_moy = data['moyenne_gen']
                    v_abs = data['total_absences']
                    v_age = data['age']
                    v_dist = data['distance_ecole']
                    v_sexe = map_sexe.get(data['sexe'], 0)
                    v_sante = map_sante.get(data['situation_sante'], 0)
                    v_rev = map_revenu.get(data['salaire_parents'], 0)
                    v_mari = map_marital.get(data['statut_marital'], 0)

                    # --- CALCUL DU SCORE ---
                    if model_ia:
                        features = np.array([[v_moy, v_abs, v_age, v_dist, v_sexe, v_sante, v_rev, v_mari]])
                        proba = model_ia.predict_proba(features)[0][1]
                        score = int(proba * 100)
                    else:
                        # Fallback manuel robuste
                        score = 0
                        if v_moy < 10: score += 40
                        if v_abs > 15: score += 20
                        if v_rev == 0: score += 20 # Pauvre
                        if v_sante == 2: score += 20 # Élevé
                        score = min(score, 100)

                    # ══════════════════════════════════════════════════════
                    # AFFICHAGE PREMIUM — DIAGNOSTIC IA
                    # ══════════════════════════════════════════════════════

                    # Définition des couleurs selon le score
                    if score >= 70:
                        risk_color      = "#EF4444"
                        risk_bg         = "rgba(239,68,68,0.08)"
                        risk_border     = "#EF4444"
                        risk_gradient   = "linear-gradient(135deg, #7f1d1d 0%, #991b1b 50%, #EF4444 100%)"
                        risk_label      = "CRITICAL RISK"
                        risk_icon       = "🔴"
                        risk_desc       = "Urgent intervention required"
                        arc_color       = "#EF4444"
                        bar_color       = "#EF4444"
                    elif score >= 40:
                        risk_color      = "#F59E0B"
                        risk_bg         = "rgba(245,158,11,0.08)"
                        risk_border     = "#F59E0B"
                        risk_gradient   = "linear-gradient(135deg, #78350f 0%, #b45309 50%, #F59E0B 100%)"
                        risk_label      = "MODERATE RISK"
                        risk_icon       = "🟡"
                        risk_desc       = "Enhanced monitoring recommended"
                        arc_color       = "#F59E0B"
                        bar_color       = "#F59E0B"
                    else:
                        risk_color      = "#10B981"
                        risk_bg         = "rgba(16,185,129,0.08)"
                        risk_border     = "#10B981"
                        risk_gradient   = "linear-gradient(135deg, #022c22 0%, #065F46 50%, #10B981 100%)"
                        risk_label      = "LOW RISK"
                        risk_icon       = "🟢"
                        risk_desc       = "Stable situation — continue monitoring"
                        arc_color       = "#10B981"
                        bar_color       = "#10B981"

                    # Calcul de l'arc SVG (demi-cercle)
                    import math
                    angle   = score / 100 * 180   # 0→180 degrés
                    rad     = math.radians(angle)
                    cx, cy, r = 110, 110, 80
                    end_x   = cx + r * math.cos(math.pi - rad)
                    end_y   = cy - r * math.sin(rad)
                    large   = 1 if angle > 180 else 0

                    # Indicateurs académiques : barres de progression
                    moy_pct   = min(int(v_moy / 20 * 100), 100)
                    abs_pct   = min(int(v_abs / 30 * 100), 100)   # 30h = max ref
                    dist_pct  = min(int(v_dist / 50 * 100), 100)  # 50km = max ref

                    # Couleur barre moyenne : verte si ≥10, rouge sinon
                    moy_bar_color  = "#10B981" if v_moy >= 10 else "#EF4444"
                    abs_bar_color  = "#EF4444" if v_abs > 15 else "#10B981"
                    dist_bar_color = "#F59E0B" if v_dist > 20 else "#10B981"

                    # CSS injecté séparément pour éviter les conflits Streamlit
                    st.markdown(f"""
                    <style>
                    @keyframes fillBar {{
                        from {{ width: 0%; }}
                        to   {{ width: var(--target-w); }}
                    }}
                    @keyframes countUp {{
                        from {{ opacity: 0; transform: scale(0.7); }}
                        to   {{ opacity: 1; transform: scale(1); }}
                    }}
                    @keyframes dashAnim {{
                        from {{ stroke-dashoffset: 502; }}
                        to   {{ stroke-dashoffset: var(--dash-end); }}
                    }}
                    .diag-wrapper {{
                        display: flex;
                        gap: 20px;
                        margin-top: 16px;
                        flex-wrap: wrap;
                    }}

                    /* ─── CARTE GAUCHE : Jauge circulaire ─── */
                    .risk-gauge-card {{
                        flex: 0 0 240px;
                        background: #FFFFFF;
                        border-radius: 20px;
                        border: 1px solid {risk_border}33;
                        box-shadow: 0 4px 24px {risk_color}22, 0 1px 4px rgba(0,0,0,0.06);
                        padding: 28px 20px 20px 20px;
                        display: flex;
                        flex-direction: column;
                        align-items: center;
                        gap: 12px;
                        animation: countUp 0.6s ease both;
                    }}
                    .gauge-svg {{ width: 220px; height: 130px; }}
                    .gauge-score-text {{
                        font-family: 'DM Sans', sans-serif;
                        font-size: 2.4rem;
                        font-weight: 900;
                        color: {risk_color};
                        line-height: 1;
                        animation: countUp 0.7s ease 0.2s both;
                    }}
                    .gauge-label-pill {{
                        background: {risk_bg};
                        border: 1.5px solid {risk_border}55;
                        border-radius: 99px;
                        padding: 6px 18px;
                        font-size: 0.78rem;
                        font-weight: 800;
                        color: {risk_color};
                        letter-spacing: 0.08em;
                        text-transform: uppercase;
                    }}
                    .gauge-desc {{
                        font-size: 0.82rem;
                        color: #6B7280;
                        font-weight: 500;
                        text-align: center;
                    }}

                    /* ─── CARTE DROITE : Indicateurs ─── */
                    .indicators-card {{
                        flex: 1;
                        min-width: 280px;
                        background: #FFFFFF;
                        border-radius: 20px;
                        border: 1px solid #D1FAE5;
                        box-shadow: 0 4px 16px rgba(0,0,0,0.05);
                        padding: 24px 28px;
                        animation: countUp 0.6s ease 0.1s both;
                    }}
                    .ind-section-title {{
                        font-family: 'DM Sans', sans-serif;
                        font-size: 0.72rem;
                        font-weight: 800;
                        text-transform: uppercase;
                        letter-spacing: 0.1em;
                        color: #064E3B;
                        margin-bottom: 14px;
                        display: flex;
                        align-items: center;
                        gap: 7px;
                    }}
                    .ind-row {{
                        display: flex;
                        align-items: center;
                        margin-bottom: 13px;
                        gap: 12px;
                    }}
                    .ind-icon {{
                        font-size: 1.05rem;
                        width: 28px;
                        text-align: center;
                        flex-shrink: 0;
                    }}
                    .ind-label {{
                        font-size: 0.82rem;
                        font-weight: 600;
                        color: #374151;
                        width: 90px;
                        flex-shrink: 0;
                    }}
                    .ind-bar-wrap {{
                        flex: 1;
                        height: 8px;
                        background: #F3F4F6;
                        border-radius: 99px;
                        overflow: hidden;
                    }}
                    .ind-bar-fill {{
                        height: 100%;
                        border-radius: 99px;
                        transition: width 1.2s cubic-bezier(.4,0,.2,1);
                        animation: fillBar 1.2s cubic-bezier(.4,0,.2,1) both;
                    }}
                    .ind-value {{
                        font-size: 0.82rem;
                        font-weight: 700;
                        color: #111827;
                        width: 58px;
                        text-align: right;
                        flex-shrink: 0;
                    }}
                    .ind-divider {{
                        border: none;
                        border-top: 1px solid #F0FDF4;
                        margin: 14px 0;
                    }}

                    /* ─── CARTES Socio-Familiales (grille 2×2) ─── */
                    .socio-grid {{
                        display: grid;
                        grid-template-columns: 1fr 1fr;
                        gap: 10px;
                        margin-top: 4px;
                    }}
                    .socio-chip {{
                        background: #F8FAFC;
                        border: 1px solid #E5E7EB;
                        border-radius: 12px;
                        padding: 10px 14px;
                        display: flex;
                        align-items: flex-start;
                        gap: 9px;
                    }}
                    .socio-chip-icon {{
                        font-size: 1.1rem;
                        margin-top: 1px;
                    }}
                    .socio-chip-content {{
                        display: flex;
                        flex-direction: column;
                        gap: 2px;
                    }}
                    .socio-chip-label {{
                        font-size: 0.7rem;
                        font-weight: 700;
                        color: #9CA3AF;
                        text-transform: uppercase;
                        letter-spacing: 0.07em;
                    }}
                    .socio-chip-value {{
                        font-size: 0.85rem;
                        font-weight: 700;
                        color: #111827;
                    }}

                    /* ─── BANDEAU INFO BAS ─── */
                    .rf-info-banner {{
                        margin-top: 20px;
                        background: linear-gradient(135deg, #022c22 0%, #065F46 60%, #10B981 100%);
                        border-radius: 16px;
                        padding: 18px 24px;
                        display: flex;
                        align-items: center;
                        gap: 16px;
                        box-shadow: 0 4px 20px rgba(16,185,129,0.25);
                        animation: countUp 0.6s ease 0.3s both;
                    }}
                    .rf-info-icon {{
                        font-size: 1.8rem;
                        flex-shrink: 0;
                    }}
                    .rf-info-text {{
                        font-family: 'DM Sans', sans-serif;
                        font-size: 0.9rem;
                        font-weight: 600;
                        color: rgba(255,255,255,0.95);
                        line-height: 1.5;
                    }}
                    .rf-info-text span {{
                        color: #6EE7B7;
                        font-weight: 800;
                    }}
                    </style>
                    """, unsafe_allow_html=True)

                    # BLOC A — Header élève (carte verte)
                    st.markdown(f"""
                    <div style="background:linear-gradient(135deg,#022c22,#065F46,#10B981);
                                border-radius:18px;padding:20px 28px;margin-bottom:20px;
                                display:flex;align-items:center;gap:16px;
                                box-shadow:0 4px 20px rgba(16,185,129,0.3);">
                        <div style="background:rgba(255,255,255,0.15);border-radius:12px;
                                    padding:10px 16px;font-size:1.6rem;">🎓</div>
                        <div>
                            <div style="font-size:1.2rem;font-weight:800;color:#fff;
                                        letter-spacing:-0.02em;">
                                {data['nom']} {data['prenom']}
                            </div>
                            <div style="font-size:0.82rem;color:#6EE7B7;font-weight:600;margin-top:2px;">
                                ID: {data['matricule']} &nbsp;·&nbsp; Class: {data['classe']}
                            </div>
                        </div>
                        <div style="margin-left:auto;background:rgba(255,255,255,0.12);
                                    border-radius:10px;padding:8px 16px;text-align:center;">
                            <div style="font-size:0.68rem;color:#A7F3D0;font-weight:700;
                                        text-transform:uppercase;letter-spacing:0.08em;">Diagnosis</div>
                            <div style="font-size:0.9rem;font-weight:800;color:#fff;margin-top:2px;">
                                {risk_icon} {risk_label}
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    # BLOC B — Jauge de risque (risk-gauge-card autonome)
                    st.markdown(f"""
                    <div class="diag-wrapper">
                        <div class="risk-gauge-card">
                            <svg class="gauge-svg" viewBox="0 0 220 130">
                                <path d="M 30 110 A 80 80 0 0 1 190 110"
                                      fill="none" stroke="#F3F4F6" stroke-width="14"
                                      stroke-linecap="round"/>
                                <path d="M 30 110 A 80 80 0 {large} 1 {end_x:.1f} {end_y:.1f}"
                                      fill="none" stroke="{arc_color}" stroke-width="14"
                                      stroke-linecap="round"
                                      style="filter: drop-shadow(0 0 6px {arc_color + '88'});"
                                />
                                <circle cx="110" cy="110" r="6" fill="{arc_color}" opacity="0.9"/>
                                <text x="110" y="96" text-anchor="middle"
                                      font-family="DM Sans, sans-serif"
                                      font-size="32" font-weight="900"
                                      fill="{risk_color}">{score}</text>
                                <text x="110" y="114" text-anchor="middle"
                                      font-family="DM Sans, sans-serif"
                                      font-size="13" font-weight="700"
                                      fill="{risk_color}" opacity="0.75">%</text>
                                <text x="24" y="126" text-anchor="middle"
                                      font-family="DM Sans, sans-serif"
                                      font-size="11" fill="#9CA3AF">0</text>
                                <text x="196" y="126" text-anchor="middle"
                                      font-family="DM Sans, sans-serif"
                                      font-size="11" fill="#9CA3AF">100</text>
                            </svg>
                            <div class="gauge-label-pill">{risk_icon} {risk_label}</div>
                            <div class="gauge-desc">{risk_desc}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    # BLOC C1 — Indicateurs académiques
                    st.markdown(f"""
                    <div class="diag-wrapper">
                        <div class="indicators-card">
                            <div class="ind-section-title">📚 Academic Indicators</div>
                            <div class="ind-row">
                                <div class="ind-icon">📊</div>
                                <div class="ind-label">Moyenne</div>
                                <div class="ind-bar-wrap">
                                    <div class="ind-bar-fill"
                                         style="width:{moy_pct}%;background:{moy_bar_color};
                                                --target-w:{moy_pct}%;"></div>
                                </div>
                                <div class="ind-value" style="color:{moy_bar_color};">{v_moy:.2f} / 20</div>
                            </div>
                            <div class="ind-row">
                                <div class="ind-icon">⏱️</div>
                                <div class="ind-label">Absences</div>
                                <div class="ind-bar-wrap">
                                    <div class="ind-bar-fill"
                                         style="width:{abs_pct}%;background:{abs_bar_color};
                                                --target-w:{abs_pct}%;"></div>
                                </div>
                                <div class="ind-value" style="color:{abs_bar_color};">{v_abs} h</div>
                            </div>
                            <div class="ind-row">
                                <div class="ind-icon">📍</div>
                                <div class="ind-label">Distance</div>
                                <div class="ind-bar-wrap">
                                    <div class="ind-bar-fill"
                                         style="width:{dist_pct}%;background:{dist_bar_color};
                                                --target-w:{dist_pct}%;"></div>
                                </div>
                                <div class="ind-value" style="color:{dist_bar_color};">{v_dist} km</div>
                            </div>
                            <div class="ind-row">
                                <div class="ind-icon">🎂</div>
                                <div class="ind-label">Âge</div>
                                <div class="ind-bar-wrap">
                                    <div class="ind-bar-fill"
                                         style="width:{min(int(v_age/25*100),100)}%;
                                                background:#A78BFA;
                                                --target-w:{min(int(v_age/25*100),100)}%;"></div>
                                </div>
                                <div class="ind-value" style="color:#7C3AED;">{v_age} yrs</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    # BLOC C2 — Facteurs socio-familiaux
                    st.markdown(f"""
                    <div class="diag-wrapper">
                        <div class="indicators-card">
                            <div class="ind-section-title">🏠 Socio-Family Factors</div>
                            <div class="socio-grid">
                                <div class="socio-chip">
                                    <div class="socio-chip-icon">🏥</div>
                                    <div class="socio-chip-content">
                                        <div class="socio-chip-label">Health</div>
                                        <div class="socio-chip-value">{data['situation_sante']}</div>
                                    </div>
                                </div>
                                <div class="socio-chip">
                                    <div class="socio-chip-icon">💍</div>
                                    <div class="socio-chip-content">
                                        <div class="socio-chip-label">Statut parents</div>
                                        <div class="socio-chip-value">{data['statut_marital']}</div>
                                    </div>
                                </div>
                                <div class="socio-chip">
                                    <div class="socio-chip-icon">💰</div>
                                    <div class="socio-chip-content">
                                        <div class="socio-chip-label">Income</div>
                                        <div class="socio-chip-value">{data['salaire_parents']}</div>
                                    </div>
                                </div>
                                <div class="socio-chip">
                                    <div class="socio-chip-icon">👨‍👩‍👧</div>
                                    <div class="socio-chip-content">
                                        <div class="socio-chip-label">Family</div>
                                        <div class="socio-chip-value">{data['nb_enfants']} child(ren)</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    # BLOC D — Bannière info Random Forest
                    st.markdown("""
                    <div class="rf-info-banner">
                        <div class="rf-info-icon">🤖</div>
                        <div class="rf-info-text">
                            These <span>8 indicators</span> are cross-analyzed by the
                            <span>Random Forest</span> algorithm to calculate the dropout risk index.
                            The score reflects the probability of school dropout based on
                            the student's academic and socio-family data.
                        </div>
                    </div>
                    """, unsafe_allow_html=True)




         
          



# --- 3. ENSEIGNANTS (FIXÉ : FILTRAGE INSTANTANÉ) ---
elif role == "Teachers Section":
    st.markdown("""
    <div class="an-header">
        <h2>📝 Teachers Section</h2>
        <p>Enter results · Grades · Absences · Behavior · Academic monitoring</p>
    </div>
    """, unsafe_allow_html=True)
    pwd_ens = st.text_input("Access Code", type="password", key="pwd_ens")
    if pwd_ens != "ens123":
        if pwd_ens:
            st.error("❌ Incorrect code.")
        else:
            st.info("🔒 Please enter your access code to continue.")
        st.stop()

    # CSS Enseignants — partie 1 : header + sections
    st.markdown("""
    <style>
    .ens-header {
        background:linear-gradient(135deg,#022c22,#065F46,#10B981);
        border-radius:18px; padding:20px 28px; margin-bottom:22px;
        display:flex; align-items:center; gap:14px;
        box-shadow:0 4px 20px rgba(16,185,129,0.3);
    }
    .ens-header-icon {
        background:rgba(255,255,255,0.15); border-radius:12px;
        padding:10px 14px; font-size:1.5rem;
    }
    .ens-header-title {
        font-size:1.1rem; font-weight:800; color:#fff; letter-spacing:-0.02em;
    }
    .ens-header-sub { font-size:0.78rem; color:#6EE7B7; margin-top:2px; }
    .ens-section {
        background:#fff; border-radius:14px; padding:16px 20px;
        border:1px solid #D1FAE5; margin-bottom:14px;
        box-shadow:0 2px 8px rgba(0,0,0,0.05);
    }
    .ens-section-title {
        font-size:0.7rem; font-weight:800; text-transform:uppercase;
        letter-spacing:0.1em; color:#065F46; margin-bottom:12px;
    }
    </style>
    """, unsafe_allow_html=True)

    # CSS Enseignants — partie 2 : tip + success
    st.markdown("""
    <style>
    .ens-tip {
        background:#F0FDF4; border-left:4px solid #10B981;
        border-radius:10px; padding:10px 14px; margin-top:8px;
        font-size:0.78rem; color:#065F46; font-weight:600;
    }
    .ens-step {
        display:inline-flex; align-items:center; justify-content:center;
        width:22px; height:22px; background:#10B981; color:#fff;
        border-radius:50%; font-size:0.7rem; font-weight:800;
        margin-right:8px; flex-shrink:0;
    }
    </style>
    """, unsafe_allow_html=True)

    # Header
    st.markdown("""
    <div class="ens-header">
        <div class="ens-header-icon">📝</div>
        <div>
            <div class="ens-header-title">Enter Results</div>
            <div class="ens-header-sub">Grades · Absences · Behavior · Academic monitoring</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    conn = get_connection()
    cursor = get_cursor(conn)
    db_execute(cursor, "SELECT DISTINCT classe FROM eleves ORDER BY classe")
    classes = [c["classe"] if isinstance(c, dict) else c[0] for c in cursor.fetchall()]
    conn.close()

    # Étape 1 — Sélection classe
    st.markdown("""
    <div class="ens-section">
        <div class="ens-section-title"><span class="ens-step">1</span> Class selection</div>
    </div>
    """, unsafe_allow_html=True)
    classe_sel = st.selectbox("Class", classes if classes else ["None"], key="cls_enseignant", label_visibility="collapsed")

    eleves_filtres = []
    if classes and classe_sel != "None":
        conn = get_connection()
        cursor = get_cursor(conn)
        db_execute(cursor, "SELECT matricule, nom, prenom FROM eleves WHERE classe = %s", (classe_sel,))
        eleves_filtres = [f"{r['matricule']} | {r['nom']} {r['prenom']}" for r in cursor.fetchall()]
        conn.close()

    # Étape 2 — Formulaire de saisie
    st.markdown("""
    <div class="ens-section">
        <div class="ens-section-title"><span class="ens-step">2</span> Enter student data</div>
    </div>
    """, unsafe_allow_html=True)

    with st.form("form_note"):
        choix_eleve = st.selectbox("Student", eleves_filtres if eleves_filtres else ["None"])
        c1, c2 = st.columns(2)
        prof = c1.text_input("Teacher Name")
        matr = c2.text_input("Subject")
        n, a, c = st.columns(3)
        note = n.number_input("Grade /20", 0.0, 20.0, 10.0)
        abse = a.number_input("Absences (h)", 0)
        comp = c.selectbox("Behavior", ["Excellent", "Passive", "Disruptive", "Isolated"])

        st.markdown("""
        <div class="ens-tip">💡 Fill in the teacher name and subject before submitting.</div>
        """, unsafe_allow_html=True)

        if st.form_submit_button("🚀 Submit Data", use_container_width=True):
            if prof and matr and " | " in choix_eleve:
                conn = get_connection()
                cursor = get_cursor(conn)
                sql = "INSERT INTO suivi (matricule_eleve, note, absences, comportement, matiere, classe_concernee, nom_enseignant) VALUES (%s,%s,%s,%s,%s,%s,%s)"
                db_execute(cursor, sql, (choix_eleve.split(" | ")[0], note, abse, comp, matr, classe_sel, prof))
                conn.commit()
                conn.close()
                st.success("✅ Data saved successfully!")
            else:
                st.error("⚠️ Teacher, subject and student are required.")

# --- 4. CONSEILLER (VERSION ALIGNÉE SUR LES INDICATEURS ACADÉMIQUES) ---
elif "Counselor & Monitoring" in role:
    st.markdown("""
    <div class="an-header">
        <h2>🔍 Counselor &amp; Monitoring</h2>
        <p>At-risk student monitoring · Alerts · Interventions · Academic analysis</p>
    </div>
    """, unsafe_allow_html=True)
    pwd_cons = st.text_input("Access Code", type="password", key="pwd_cons")
    if pwd_cons != "cons123":
        if pwd_cons:
            st.error("❌ Incorrect code.")
        else:
            st.info("🔒 Please enter your access code to continue.")
        st.stop()

    # ── Badge supprimé définitivement dès l'accès à la page ──
    marquer_comme_lu()

    # CSS Conseiller — partie 1 : header + filtre
    st.markdown("""
    <style>
    .cons-header {
        background:linear-gradient(135deg,#022c22,#065F46,#10B981);
        border-radius:18px; padding:20px 28px; margin-bottom:22px;
        display:flex; align-items:center; justify-content:space-between;
        box-shadow:0 4px 20px rgba(16,185,129,0.3);
    }
    .cons-header-left { display:flex; align-items:center; gap:14px; }
    .cons-header-icon {
        background:rgba(255,255,255,0.15); border-radius:12px;
        padding:10px 14px; font-size:1.5rem;
    }
    .cons-header-title {
        font-size:1.1rem; font-weight:800; color:#fff; letter-spacing:-0.02em;
    }
    .cons-header-sub { font-size:0.78rem; color:#6EE7B7; margin-top:2px; }
    .cons-badge {
        background:rgba(239,68,68,0.25); border:1.5px solid rgba(239,68,68,0.5);
        border-radius:99px; padding:6px 18px; font-size:0.82rem;
        font-weight:700; color:#FCA5A5;
    }
    </style>
    """, unsafe_allow_html=True)

    # CSS Conseiller — partie 2 : alertes + cartes actions
    st.markdown("""
    <style>
    .cons-alert-banner {
        background:#FEF2F2; border:1.5px solid #FECACA; border-radius:14px;
        padding:14px 20px; margin-bottom:16px;
        display:flex; align-items:center; gap:12px;
    }
    .cons-alert-icon { font-size:1.4rem; flex-shrink:0; }
    .cons-alert-text { font-size:0.88rem; font-weight:700; color:#991B1B; }
    .cons-empty {
        text-align:center; padding:40px 20px; background:#F0FDF4;
        border-radius:16px; border:2px dashed #A7F3D0;
    }
    .cons-empty-icon { font-size:2.5rem; margin-bottom:10px; }
    .cons-empty-text { font-size:0.92rem; font-weight:600; color:#065F46; }
    </style>
    """, unsafe_allow_html=True)

    conn = get_connection()
    if conn:
        cursor = get_cursor(conn)
        db_execute(cursor, "SELECT DISTINCT classe FROM eleves ORDER BY classe")
        classes = [c["classe"] if isinstance(c, dict) else c[0] for c in cursor.fetchall()]
        classe_suivi = st.selectbox("🎯 Filter by class:", ["All"] + classes)

        query = """
            SELECT e.matricule, e.nom, e.prenom, e.classe,
                AVG(s.note) as moyenne_actuelle,
                SUM(s.absences) as total_absences,
                GROUP_CONCAT(s.comportement) as historique_comportement
            FROM eleves e JOIN suivi s ON e.matricule = s.matricule_eleve
        """
        if classe_suivi != "Toutes":
            query += f" WHERE e.classe = '{classe_suivi}'"
        query += " GROUP BY e.matricule HAVING moyenne_actuelle < 10"

        df_suivi = db_read_sql(query, conn)
        conn.close()

        nb = len(df_suivi)

        # Header dynamique
        st.markdown(f"""
        <div class="cons-header">
            <div class="cons-header-left">
                <div class="cons-header-icon">🔍</div>
                <div>
                    <div class="cons-header-title">Intervention & Monitoring Unit</div>
                    <div class="cons-header-sub">Detection · Action plans · Behavioral analysis</div>
                </div>
            </div>
            <div class="cons-badge">🔴 {nb} struggling student(s)</div>
        </div>
        """, unsafe_allow_html=True)

        if not df_suivi.empty:
            # Bannière alerte
            st.markdown(f"""
            <div class="cons-alert-banner">
                <div class="cons-alert-icon">⚠️</div>
                <div class="cons-alert-text">
                    {nb} student(s) identified with insufficient average (&lt; 10/20).
                    An intervention is recommended.
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Tableau d'interventions
            liste_interventions = []
            for idx, row in df_suivi.iterrows():
                compts = row['historique_comportement'].split(',')
                comp_dominant_raw = max(set(compts), key=compts.count)
                behavior_map = {"Excellent": "Excellent", "Passif": "Passive", "Perturbateur": "Disruptive", "Isolé": "Isolated", "Passive": "Passive", "Disruptive": "Disruptive", "Isolated": "Isolated"}
                comp_dominant = behavior_map.get(comp_dominant_raw, comp_dominant_raw)
                if row['total_absences'] > 15:
                    action_conseiller = "🚨 DROPOUT ALERT: Summon for chronic absenteeism."
                elif comp_dominant in ("Perturbateur", "Disruptive"):
                    action_conseiller = "⚖️ DISCIPLINE: Corrective interview following teacher reports."
                elif comp_dominant in ("Isolé", "Isolated"):
                    action_conseiller = "🤝 PSYCHOLOGICAL: Support required due to isolation risk."
                else:
                    action_conseiller = "📖 REMEDIATION: Academic support needed to improve average."
                liste_interventions.append({
                    "ID": row['matricule'],
                    "Student": f"{row['nom']} {row['prenom']}",
                    "Class": row['classe'],
                    "Average": round(row['moyenne_actuelle'], 2),
                    "Absences (h)": row['total_absences'],
                    "Profile": comp_dominant,
                    "COUNSELOR ACTION": action_conseiller
                })

            st.dataframe(pd.DataFrame(liste_interventions), use_container_width=True, hide_index=True)

        else:
            st.markdown("""
            <div class="cons-empty">
                <div class="cons-empty-icon">✅</div>
                <div class="cons-empty-text">No student has an average below 10<br>in this selection.</div>
            </div>
            """, unsafe_allow_html=True)





# --- 5. CONVERSATION EN DIRECT ---
elif role == "💬 Chat":

    # CSS Conv — partie 1 : header + bulles
    st.markdown("""
    <style>
    .conv-header {
        background:linear-gradient(135deg,#022c22,#065F46,#10B981);
        border-radius:18px; padding:20px 28px; margin-bottom:22px;
        display:flex; align-items:center; justify-content:space-between;
        box-shadow:0 4px 20px rgba(16,185,129,0.3);
    }
    .conv-header-left { display:flex; align-items:center; gap:14px; }
    .conv-header-icon {
        background:rgba(255,255,255,0.15); border-radius:12px;
        padding:10px 14px; font-size:1.5rem;
    }
    .conv-header-title {
        font-size:1.1rem; font-weight:800; color:#fff; letter-spacing:-0.02em;
    }
    .conv-header-sub { font-size:0.78rem; color:#6EE7B7; margin-top:2px; }
    .conv-badge {
        background:rgba(255,255,255,0.12); border:1.5px solid rgba(255,255,255,0.25);
        border-radius:99px; padding:6px 16px; font-size:0.8rem;
        font-weight:700; color:#fff;
    }
    </style>
    """, unsafe_allow_html=True)

    # CSS Conv — partie 2 : messages + rôles
    st.markdown("""
    <style>
    @keyframes msgIn {
        from { opacity:0; transform:translateY(8px); }
        to   { opacity:1; transform:translateY(0); }
    }
    .conv-feed {
        display:flex; flex-direction:column; gap:12px;
        padding:4px 0 16px 0;
    }
    .conv-msg {
        display:flex; gap:10px; align-items:flex-start;
        animation: msgIn 0.35s ease both;
    }
    .conv-avatar {
        width:36px; height:36px; border-radius:50%;
        display:flex; align-items:center; justify-content:center;
        font-size:1rem; flex-shrink:0; font-weight:800;
    }
    .conv-bubble {
        flex:1; background:#fff; border-radius:14px;
        padding:12px 16px; border:1px solid #E5E7EB;
        box-shadow:0 2px 8px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

    # CSS Conv — partie 3 : détails bulle + empty
    st.markdown("""
    <style>
    .conv-bubble-top {
        display:flex; align-items:center; gap:8px; margin-bottom:6px;
    }
    .conv-bubble-name {
        font-size:0.82rem; font-weight:800; color:#111827;
    }
    .conv-role-pill {
        font-size:0.65rem; font-weight:700; text-transform:uppercase;
        letter-spacing:0.07em; padding:2px 8px; border-radius:99px;
    }
    .conv-bubble-text {
        font-size:0.88rem; color:#374151; line-height:1.55;
    }
    .conv-bubble-time {
        font-size:0.68rem; color:#9CA3AF; margin-top:6px;
    }
    .conv-empty {
        text-align:center; padding:40px 20px;
        background:#F8FAFC; border-radius:16px;
        border:2px dashed #E5E7EB; margin:10px 0;
    }
    .conv-empty-icon { font-size:2.5rem; margin-bottom:10px; }
    .conv-empty-text { font-size:0.9rem; font-weight:600; color:#6B7280; }

    /* ── Petits boutons menu ⋮ (Modifier / Supprimer) ── */
    .conv-menu-btn > div > button {
        background: #fff !important;
        border: 1.5px solid #E5E7EB !important;
        border-radius: 10px !important;
        color: #374151 !important;
        font-size: 0.78rem !important;
        font-weight: 600 !important;
        padding: 5px 10px !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.07) !important;
        animation: none !important;
        background-image: none !important;
        min-height: 32px !important;
        height: 32px !important;
        line-height: 1 !important;
        letter-spacing: 0 !important;
    }
    .conv-menu-btn > div > button:hover {
        transform: none !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.12) !important;
    }
    .conv-menu-edit > div > button:hover {
        background: #F0FDF4 !important;
        border-color: #10B981 !important;
        color: #065F46 !important;
    }
    .conv-menu-del > div > button:hover {
        background: #FEF2F2 !important;
        border-color: #EF4444 !important;
        color: #B91C1C !important;
    }
    /* Bouton trois points ⋮ — ciblé par contenu */
    button[title="Options"] {
        background: transparent !important;
        border: 1px solid #E5E7EB !important;
        border-radius: 8px !important;
        color: #6B7280 !important;
        font-size: 1rem !important;
        font-weight: 900 !important;
        padding: 2px 8px !important;
        box-shadow: none !important;
        animation: none !important;
        background-image: none !important;
        min-height: 28px !important;
        height: 28px !important;
        line-height: 1 !important;
        letter-spacing: 0 !important;
    }
    button[title="Options"]:hover {
        color: #111827 !important;
        background: #F3F4F6 !important;
        border-color: #D1D5DB !important;
        transform: none !important;
        box-shadow: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Couleurs par rôle
    role_styles = {
        "Teacher":  {"bg":"#DBEAFE","color":"#1D4ED8","emoji":"👨‍🏫"},
        "Admin":       {"bg":"#D1FAE5","color":"#065F46","emoji":"🛡️"},
        "Counselor":  {"bg":"#FEF3C7","color":"#92400E","emoji":"🔍"},
    }

    conn = get_connection()
    if conn:
        cursor = get_cursor(conn)
        db_execute(cursor, "SELECT COUNT(*) FROM conversations")
        raw = cursor.fetchone()
        nb_msg = raw[0] if raw else 0
        conn.close()

    # Header
    st.markdown(f"""
    <div class="conv-header">
        <div class="conv-header-left">
            <div class="conv-header-icon">💬</div>
            <div>
                <div class="conv-header-title">General Chat</div>
                <div class="conv-header-sub">Shared space · Teachers · Admin · Counselors</div>
            </div>
        </div>
        <div class="conv-badge">💬 {nb_msg} message(s)</div>
    </div>
    """, unsafe_allow_html=True)

    # Session state pour édition / menu
    if "conv_edit_id" not in st.session_state:
        st.session_state.conv_edit_id = None
    if "conv_menu_id" not in st.session_state:
        st.session_state.conv_menu_id = None
    if "conv_auteur_session" not in st.session_state:
        st.session_state.conv_auteur_session = ""

    # Rôle automatique depuis le login
    role_conv_auto = st.session_state.get("user_role", "Teacher")

    # Formulaire d'envoi
    with st.form("form_conv", clear_on_submit=True):
        auteur_conv  = st.text_input("Your name", value=st.session_state.conv_auteur_session)
        message_conv = st.text_area("Message", height=80, placeholder="Write your message here…")
        if st.form_submit_button("📨 Send", use_container_width=True):
            if auteur_conv.strip() and message_conv.strip():
                st.session_state.conv_auteur_session = auteur_conv.strip()
                conn = get_connection()
                if conn:
                    cursor = get_cursor(conn)
                    db_execute(cursor,
                        "INSERT INTO conversations (auteur, role_auteur, message) VALUES (%s,%s,%s)",
                        (auteur_conv.strip(), role_conv_auto, message_conv.strip()))
                    conn.commit()
                    conn.close()
                st.rerun()
            else:
                st.error("⚠️ Name and message required.")

    # Lecture des messages
    conn = get_connection()
    if conn:
        df_conv = db_read_sql(
            "SELECT id, auteur, role_auteur, message, date_msg FROM conversations ORDER BY date_msg DESC LIMIT 50",
            conn)
        conn.close()

        if not df_conv.empty:
            auteur_session = st.session_state.conv_auteur_session

            for _, row in df_conv.iterrows():
                msg_id   = int(row['id'])
                st_row   = role_styles.get(row['role_auteur'], {"bg":"#F3F4F6","color":"#374151","emoji":"👤"})
                date_str = str(row['date_msg'])[:16] if row['date_msg'] else ""
                is_own   = bool(auteur_session and row['auteur'] == auteur_session)
                edited   = "[edited]" in str(row['message'])
                msg_text = str(row['message']).replace(" [edited]", "")

                # Bulle du message
                bg_col   = st_row["bg"]
                txt_col  = st_row["color"]
                emoji_s  = st_row["emoji"]
                auteur_s = row["auteur"]
                role_s   = row["role_auteur"]
                edited_tag = ('<span style="font-size:0.65rem;color:#9CA3AF;font-style:italic;">✏️ edited</span>'
                              if edited else "")

                parts = []
                parts.append('<div style="display:flex;gap:10px;align-items:flex-start;margin-bottom:4px;">')
                parts.append(f'<div style="background:{bg_col};color:{txt_col};width:36px;height:36px;'
                             f'border-radius:50%;display:flex;align-items:center;justify-content:center;'
                             f'font-size:1rem;flex-shrink:0;">{emoji_s}</div>')
                parts.append('<div style="flex:1;background:#fff;border-radius:14px;padding:10px 14px;'
                             'border:1px solid #E5E7EB;box-shadow:0 2px 8px rgba(0,0,0,0.05);">')
                parts.append('<div style="display:flex;align-items:center;gap:8px;margin-bottom:4px;">')
                parts.append(f'<span style="font-size:0.82rem;font-weight:800;color:#111827;">{auteur_s}</span>')
                parts.append(f'<span style="font-size:0.65rem;font-weight:700;text-transform:uppercase;'
                             f'padding:2px 8px;border-radius:99px;background:{bg_col};color:{txt_col};">{role_s}</span>')
                parts.append(edited_tag)
                parts.append('</div>')
                parts.append(f'<div style="font-size:0.88rem;color:#374151;line-height:1.55;">{msg_text}</div>')
                parts.append(f'<div style="font-size:0.68rem;color:#9CA3AF;margin-top:6px;">🕐 {date_str}</div>')
                parts.append('</div></div>')
                st.markdown("".join(parts), unsafe_allow_html=True)


                # Bouton ⋮ uniquement pour l'auteur
                if is_own:
                    col_sp, col_btn = st.columns([18, 1])
                    with col_btn:
                        if st.button("⋮", key=f"menu_{msg_id}", help="Options"):
                            st.session_state.conv_menu_id = msg_id if st.session_state.conv_menu_id != msg_id else None
                            st.session_state.conv_edit_id = None

                    # Menu contextuel — petits boutons style popup
                    if st.session_state.conv_menu_id == msg_id:
                        st.markdown(f"""
                        <style>
                        div[data-testid="stHorizontalBlock"]:has(button[kind="secondary"][id*="edit_{msg_id}"],
                                                                  button[kind="secondary"][id*="del_{msg_id}"]) {{
                            gap: 6px !important;
                        }}
                        button[kind="secondary"][id*="edit_{msg_id}"],
                        button[kind="secondary"][id*="del_{msg_id}"] {{
                            background: #fff !important;
                            border: 1.5px solid #E5E7EB !important;
                            border-radius: 10px !important;
                            color: #374151 !important;
                            font-size: 0.78rem !important;
                            font-weight: 600 !important;
                            padding: 6px 12px !important;
                            box-shadow: 0 2px 8px rgba(0,0,0,0.08) !important;
                            animation: none !important;
                            background-size: unset !important;
                            letter-spacing: 0 !important;
                            min-height: unset !important;
                            height: auto !important;
                        }}
                        button[kind="secondary"][id*="edit_{msg_id}"]:hover {{
                            background: #F0FDF4 !important;
                            border-color: #10B981 !important;
                            color: #065F46 !important;
                            box-shadow: 0 2px 8px rgba(16,185,129,0.2) !important;
                            transform: none !important;
                        }}
                        button[kind="secondary"][id*="del_{msg_id}"]:hover {{
                            background: #FEF2F2 !important;
                            border-color: #EF4444 !important;
                            color: #991B1B !important;
                            box-shadow: 0 2px 8px rgba(239,68,68,0.2) !important;
                            transform: none !important;
                        }}
                        </style>
                        """, unsafe_allow_html=True)
                        col_sp2, col_e, col_d, col_end = st.columns([8, 1.4, 1.4, 0.2])
                        with col_e:
                            if st.button("✏️ Edit", key=f"edit_{msg_id}", use_container_width=True):
                                st.session_state.conv_edit_id = msg_id
                                st.session_state.conv_menu_id = None
                        with col_d:
                            if st.button("🗑️ Delete", key=f"del_{msg_id}", use_container_width=True):
                                conn2 = get_connection()
                                if conn2:
                                    cur2 = get_cursor(conn2)
                                    db_execute(cur2, "DELETE FROM conversations WHERE id = %s", (msg_id,))
                                    conn2.commit()
                                    conn2.close()
                                st.session_state.conv_menu_id = None
                                st.rerun()

                # Formulaire modification inline
                if st.session_state.conv_edit_id == msg_id:
                    with st.form(f"form_edit_{msg_id}"):
                        new_text = st.text_area("✏️ Edit message", value=msg_text, height=80)
                        c1, c2 = st.columns(2)
                        if c1.form_submit_button("💾 Save", use_container_width=True):
                            if new_text.strip():
                                conn3 = get_connection()
                                if conn3:
                                    cur3 = get_cursor(conn3)
                                    db_execute(cur3,
                                        "UPDATE conversations SET message = %s WHERE id = %s",
                                        (new_text.strip() + " [edited]", msg_id))
                                    conn3.commit()
                                    conn3.close()
                                st.session_state.conv_edit_id = None
                                st.rerun()
                        if c2.form_submit_button("✖️ Cancel", use_container_width=True):
                            st.session_state.conv_edit_id = None
                            st.rerun()

        else:
            st.markdown("""
            <div class="conv-empty">
                <div class="conv-empty-icon">💬</div>
                <div class="conv-empty-text">No messages yet.<br>Be the first to write!</div>
            </div>
            """, unsafe_allow_html=True)
