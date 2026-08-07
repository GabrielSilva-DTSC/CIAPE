"""
CIAPE — Centralização das Informações de Apoio e Permanência Estudantil
Aplicação Streamlit do MVP (UFPB — campi I, II, III e IV).

Regra de negócio: todo dado exibido vem das bases do projeto
(`df_mvp` + `df_editais`) e da documentação do notebook `analise_censo_edu_sup.ipynb`.
Nenhum valor é digitado no código — apenas rótulos e legendas.

Execução:
    streamlit run app_ciape.py
"""

from __future__ import annotations

import re
from pathlib import Path

import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

# ===========================================================================
# 1. CONFIGURAÇÃO
# ===========================================================================
st.set_page_config(
    page_title="CIAPE — Apoio e Permanência Estudantil",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

APP_DIR = Path(__file__).resolve().parent

# Compatibilidade: a partir do Streamlit 1.45 `use_container_width` foi
# substituído por `width="stretch"`. O app aceita as duas gerações da API.
try:
    from packaging.version import Version

    _API_NOVA = Version(st.__version__.split("+")[0]) >= Version("1.45")
except Exception:
    _API_NOVA = False

LARGURA = {"width": "stretch"} if _API_NOVA else {"use_container_width": True}


# ---- Tokens de design ------------------------------------------------------
INK = "#0F172A"
MUTED = "#64748B"
LINE = "#E7E9F2"
ACCENT = "#6355F0"
ACCENT_DARK = "#5646E8"
SIDEBAR_BG = "#101828"

CORES = {
    "Alimentação": {"solid": "#F97316", "tint": "#FFF7ED", "border": "#FFEDD5", "icone": "garfo"},
    "Auxílio Aluguel": {"solid": "#22A05B", "tint": "#F0FDF4", "border": "#DCFCE7", "icone": "casa"},
    "Residência (vaga física)": {"solid": "#6366F1", "tint": "#EEF2FF", "border": "#E0E7FF", "icone": "cama"},
    "Transporte": {"solid": "#3B82F6", "tint": "#EFF6FF", "border": "#DBEAFE", "icone": "onibus"},
    "Apoio à Criança (Creche)": {"solid": "#EC4899", "tint": "#FDF2F8", "border": "#FCE7F3", "icone": "bebe"},
    "Outros": {"solid": "#64748B", "tint": "#F8FAFC", "border": "#E2E8F0", "icone": "marcador"},
}

# ---- Legendas documentadas no notebook (célula 38) -------------------------
MAPA_PUBLICO = {
    1: "Unificado",
    2: "Ingressantes",
    3: "Veteranos(as)",
    4: "Pós-graduandos(as)",
    5: "Intercambistas",
    6: "Grupos Étnicos",
}
MAPA_EIXO = {1: "Moradia", 2: "Transporte", 3: "Alimentação"}

# Silhueta simplificada da Paraíba (usada no hero e como fallback do mapa)
PB_POLIGONO = [
    (-38.62, -6.24), (-38.32, -6.30), (-38.02, -6.36), (-37.68, -6.28), (-37.30, -6.38),
    (-36.95, -6.28), (-36.60, -6.42), (-36.20, -6.28), (-35.85, -6.42), (-35.55, -6.30),
    (-35.28, -6.42), (-35.05, -6.40), (-34.98, -6.48), (-34.86, -6.72), (-34.82, -7.02),
    (-34.79, -7.28), (-34.83, -7.48), (-35.10, -7.52), (-35.40, -7.60), (-35.72, -7.58),
    (-36.05, -7.72), (-36.40, -7.68), (-36.75, -7.82), (-37.10, -7.78), (-37.45, -7.90),
    (-37.80, -7.86), (-38.10, -7.96), (-38.40, -7.80), (-38.60, -7.55), (-38.76, -7.30),
    (-38.72, -6.98), (-38.60, -6.70), (-38.66, -6.45), (-38.62, -6.24),
]

# ===========================================================================
# 2. ÍCONES
# ===========================================================================
def svg(path: str, size: int = 18, stroke: str = "currentColor", width: float = 2) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" '
        f'fill="none" stroke="{stroke}" stroke-width="{width}" stroke-linecap="round" '
        f'stroke-linejoin="round">{path}</svg>'
    )


P = {
    "casa": '<path d="M3 10.5 12 3l9 7.5"/><path d="M5 9.5V21h14V9.5"/><path d="M9.5 21v-6h5v6"/>',
    "garfo": '<path d="M4 3v6a2.5 2.5 0 0 0 5 0V3"/><path d="M6.5 9v12"/><path d="M17.5 3c-1.5 1.5-2 3.5-2 6s.5 3.5 2 3.5h1.5V3z"/><path d="M18 12.5V21"/>',
    "onibus": '<rect x="4" y="3" width="16" height="14" rx="2"/><path d="M4 10h16"/><path d="M7 17v3"/><path d="M17 17v3"/>',
    "bebe": '<circle cx="12" cy="9" r="4.5"/><path d="M9.5 8.5h.01"/><path d="M14.5 8.5h.01"/><path d="M10 11.5c1.2.9 2.8.9 4 0"/><path d="M5 21c1.5-3.5 4-5 7-5s5.5 1.5 7 5"/>',
    "cama": '<path d="M3 6v14"/><path d="M3 12h18v8"/><path d="M21 12V9a3 3 0 0 0-3-3h-7v6"/><circle cx="7" cy="9.5" r="1.6"/>',
    "info": '<circle cx="12" cy="12" r="9"/><path d="M12 11v5"/><path d="M12 8h.01"/>',
    "marcador": '<path d="M6 4h12v17l-6-4-6 4z"/>',
    "capelo": '<path d="M2 8.5 12 4l10 4.5L12 13z"/><path d="M6 10.5V16c0 1.7 2.7 3 6 3s6-1.3 6-3v-5.5"/>',
    "predio": '<path d="M4 21V5a2 2 0 0 1 2-2h6a2 2 0 0 1 2 2v16"/><path d="M14 12h4a2 2 0 0 1 2 2v7"/><path d="M2 21h20"/><path d="M8 7h2"/><path d="M8 11h2"/><path d="M8 15h2"/>',
    "pessoas": '<circle cx="9" cy="8" r="3.2"/><path d="M2.5 20c.6-3.4 3.3-5.2 6.5-5.2s5.9 1.8 6.5 5.2"/><path d="M16.5 5.2a3.2 3.2 0 0 1 0 5.9"/><path d="M18 14.9c2 .6 3.3 2.3 3.6 5.1"/>',
    "dinheiro": '<path d="M4.5 7h15a1.5 1.5 0 0 1 1.5 1.5v8a1.5 1.5 0 0 1-1.5 1.5h-15A1.5 1.5 0 0 1 3 16.5v-8A1.5 1.5 0 0 1 4.5 7z"/><circle cx="12" cy="12.5" r="2.6"/>',
    "banco": '<path d="M3 10 12 4l9 6"/><path d="M5 10v9"/><path d="M10 10v9"/><path d="M14 10v9"/><path d="M19 10v9"/><path d="M3 21h18"/>',
    "chevron": '<path d="m6 9 6 6 6-6"/>',
    "download": '<path d="M12 3v12"/><path d="m7 11 5 5 5-5"/><path d="M4 20h16"/>',
    "cadeira": '<path d="M6 20v-2"/><path d="M18 20v-2"/><path d="M4 8h16l-1 10H5z"/><path d="M7 8V5a2 2 0 0 1 2-2h6a2 2 0 0 1 2 2v3"/>',
}

# ===========================================================================
# 3. CSS
# ===========================================================================
st.markdown(
    f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="st-"], button, input, textarea, select {{
    font-family: 'Inter', -apple-system, 'Segoe UI', Roboto, sans-serif;
}}
#MainMenu, footer, header[data-testid="stHeader"] {{ visibility: hidden; height: 0; }}
.stApp {{ background: #EEF0F6; }}
.block-container {{ padding: 1.6rem 1.7rem 2.4rem 1.7rem; max-width: 1720px; }}
[data-testid="stVerticalBlock"] {{ gap: .55rem; }}
[data-testid="stHorizontalBlock"] {{ gap: 1.1rem; }}
svg {{ vertical-align: middle; }}

/* ---------------- Sidebar ---------------- */
[data-testid="stSidebar"] {{ background: {SIDEBAR_BG}; width: 268px !important; border-right: 1px solid #0B1220; }}
[data-testid="stSidebar"] > div:first-child {{ padding: 1.6rem 1.15rem 1.2rem 1.15rem; }}
.brand {{ display: flex; gap: .7rem; align-items: flex-start; margin-bottom: 1.9rem; }}
.brand-mark {{
    width: 38px; height: 38px; border-radius: 11px; flex: 0 0 38px;
    background: linear-gradient(150deg,#7C6CFF,#5544E6); display: flex;
    align-items: center; justify-content: center; box-shadow: 0 6px 16px rgba(85,68,230,.35);
}}
.brand-name {{ color: #fff; font-size: 1.42rem; font-weight: 700; line-height: 1.1; }}
.brand-sub {{ color: #94A3B8; font-size: .705rem; line-height: 1.42; margin-top: .32rem; }}
[data-testid="stSidebar"] .stButton > button {{
    width: 100%; justify-content: flex-start; gap: .7rem; background: transparent;
    color: #A9B4C7; border: none; padding: .62rem .78rem; border-radius: 11px;
    font-size: .875rem; font-weight: 500;
}}
[data-testid="stSidebar"] .stButton > button:hover {{ background: rgba(255,255,255,.06); color: #fff; }}
[data-testid="stSidebar"] .stButton > button[kind="primary"] {{
    background: {ACCENT}; color: #fff; font-weight: 600; box-shadow: 0 6px 16px rgba(99,85,240,.35);
}}
[data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {{ background: {ACCENT_DARK}; }}
[data-testid="stSidebar"] .stButton > button p {{ color: inherit; font-size: .875rem; }}
.side-card {{ background: #17203A; border: 1px solid rgba(255,255,255,.06); border-radius: 13px; padding: .95rem .9rem; margin-top: 1.6rem; }}
.side-card p {{ color: #93A0B8; font-size: .755rem; line-height: 1.55; margin: .55rem 0 0 0; }}
.side-foot {{ color: #fff; font-size: .82rem; font-weight: 600; margin: 0 0 .5rem 0; }}
.side-dl {{ display: flex; gap: .6rem; color: #93A0B8; font-size: .755rem; line-height: 1.45; margin-bottom: .5rem; }}
[data-testid="stSidebar"] [data-testid="stDownloadButton"] button {{
    background: rgba(255,255,255,.07); color: #CBD5E1; border: 1px solid rgba(255,255,255,.1);
    border-radius: 9px; font-size: .78rem;
}}
[data-testid="stSidebar"] [data-testid="stDownloadButton"] button:hover {{ background: rgba(255,255,255,.12); color: #fff; }}

/* ---------------- Painéis ---------------- */
.st-key-painel_esq, .st-key-painel_dir, .st-key-painel_full {{
    background: #fff; border-radius: 18px; padding: 1.45rem 1.5rem 1.6rem 1.5rem;
    border: 1px solid #EFF1F6; box-shadow: 0 1px 2px rgba(16,24,40,.05), 0 10px 30px rgba(16,24,40,.06);
}}
.h1 {{ font-size: 1.34rem; font-weight: 700; color: {INK}; margin: 0 0 .28rem 0; letter-spacing: -.01em; }}
.sub {{ font-size: .82rem; color: {MUTED}; margin: 0; line-height: 1.5; }}
.sec-title {{ font-size: .95rem; font-weight: 700; color: {INK}; margin: 1.6rem 0 .8rem 0; }}

/* ---------------- Hero (Sobre) ---------------- */
.hero {{ position: relative; padding: 1.2rem .4rem 1.6rem .4rem; overflow: hidden; }}
.hero-map {{ position: absolute; right: -1rem; top: 0; opacity: .5; pointer-events: none; }}
.hero h1 {{ font-size: 3.4rem; font-weight: 800; color: {INK}; margin: 0 0 .3rem 0; letter-spacing: -.035em; }}
.hero h2 {{ font-size: 1.42rem; font-weight: 600; color: #334155; margin: 0 0 .9rem 0; line-height: 1.3; max-width: 30rem; }}
.hero p {{ font-size: .875rem; color: {MUTED}; line-height: 1.65; max-width: 31rem; margin: 0; }}
.persona {{ border: 1px solid {LINE}; border-radius: 15px; padding: 1.1rem 1.15rem; height: 100%; background: #fff; }}
.persona-top {{ display: flex; gap: .85rem; align-items: center; margin-bottom: .8rem; }}
.persona-av {{ width: 46px; height: 46px; border-radius: 50%; flex: 0 0 46px; display: flex; align-items: center; justify-content: center; }}
.persona-nome {{ font-size: .98rem; font-weight: 700; color: {INK}; margin: 0; }}
.persona-tag {{ font-size: .74rem; color: {ACCENT}; font-weight: 600; margin: .1rem 0 0 0; }}
.persona p {{ font-size: .795rem; color: {MUTED}; line-height: 1.6; margin: 0; }}
.stat {{ border-left: 3px solid {ACCENT}; padding: .1rem 0 .1rem .8rem; }}
.stat b {{ display: block; font-size: 1.45rem; color: {INK}; font-weight: 700; line-height: 1.1; }}
.stat span {{ font-size: .755rem; color: {MUTED}; line-height: 1.4; display: block; margin-top: .2rem; }}

/* ---------------- Instituição / mapa / filtros ---------------- */
.st-key-inst_box {{ background: #fff; border: 1px solid {LINE}; border-radius: 13px; padding: .55rem .7rem; }}
.inst-mark {{ width: 34px; height: 34px; border-radius: 9px; background: #EEF2FF; display: flex; align-items: center; justify-content: center; }}
.inst-lab {{ font-size: .68rem; color: {MUTED}; margin: 0 0 .18rem 0; }}
.st-key-mapa_card, .st-key-filtros {{ border: 1px solid {LINE}; border-radius: 14px; background: #fff; margin-top: 1.05rem; }}
.st-key-mapa_card {{ padding: .95rem 1rem .55rem 1rem; }}
.st-key-filtros {{ padding: .85rem 1rem .95rem 1rem; }}
.map-title {{ font-size: .92rem; font-weight: 600; color: {INK}; margin: 0 0 .18rem 0; }}
.map-sub {{ font-size: .765rem; color: {MUTED}; margin: 0 0 .7rem 0; }}
.flabel {{ font-size: .72rem; color: {MUTED}; font-weight: 500; margin: 0 0 .3rem 2px; }}

/* ---------------- Lista ---------------- */
.list-head {{ display: flex; align-items: center; gap: .6rem; margin: 1.5rem 0 .85rem 0; }}
.list-head h3 {{ font-size: 1rem; font-weight: 700; color: {INK}; margin: 0; }}
.pill-count {{ background: #EEF2FF; color: {ACCENT}; font-size: .715rem; font-weight: 600; padding: .2rem .6rem; border-radius: 999px; }}
[class*="st-key-prog_"] {{ border: 1px solid {LINE}; border-radius: 14px; padding: .95rem 1.05rem; background: #fff; margin-bottom: .75rem; }}
[class*="st-key-prog_"]:hover {{ border-color: #D9DEEC; box-shadow: 0 6px 18px rgba(16,24,40,.07); }}
.pc {{ display: flex; gap: .85rem; align-items: flex-start; }}
.tile {{ width: 42px; height: 42px; border-radius: 11px; flex: 0 0 42px; display: flex; align-items: center; justify-content: center; }}
.pc-name {{ font-size: .9rem; font-weight: 600; color: {INK}; margin: 0 0 .12rem 0; line-height: 1.3; }}
.pc-scope {{ font-size: .715rem; color: #94A3B8; margin: 0 0 .32rem 0; }}
.pc-desc {{ font-size: .78rem; color: {MUTED}; margin: 0; line-height: 1.5; }}
.price-row {{ display: flex; align-items: center; justify-content: flex-end; gap: .45rem; margin-bottom: .4rem; }}
.price {{ font-size: .74rem; font-weight: 600; padding: .22rem .55rem; border-radius: 7px; background: #DCFCE7; color: #15803D; }}
.price.vaga {{ background: #EDE9FE; color: #5B21B6; }}
.period {{ font-size: .72rem; color: {MUTED}; }}
[class*="st-key-btn_"] button {{
    width: 100%; background: {ACCENT}; color: #fff; border: none; border-radius: 9px;
    padding: .38rem .7rem; font-size: .76rem; font-weight: 500; box-shadow: 0 3px 10px rgba(99,85,240,.28);
}}
[class*="st-key-btn_"] button:hover {{ background: {ACCENT_DARK}; color: #fff; }}
[class*="st-key-btn_"] button p {{ font-size: .76rem; color: #fff; }}

/* ---------------- Painel direito ---------------- */
.dp-title {{ font-size: 1.28rem; font-weight: 700; color: {INK}; margin: 0 0 .18rem 0; letter-spacing: -.01em; }}
.dp-city {{ font-size: .82rem; color: {MUTED}; margin: 0; }}
.st-key-fechar button {{ background: transparent; border: none; color: #94A3B8; }}
.st-key-fechar button:hover {{ color: {INK}; background: #F1F5F9; }}
[data-testid="stTabs"] [data-baseweb="tab-list"] {{ gap: 1.6rem; border-bottom: 1px solid {LINE}; }}
[data-testid="stTabs"] [data-baseweb="tab"] {{ padding: .55rem 0 .7rem 0; font-size: .845rem; font-weight: 500; color: {MUTED}; }}
[data-testid="stTabs"] [aria-selected="true"] {{ color: {ACCENT} !important; font-weight: 600; }}
[data-testid="stTabs"] [data-baseweb="tab-highlight"] {{ background: {ACCENT}; height: 2.5px; }}
[data-testid="stTabs"] [data-baseweb="tab-border"] {{ display: none; }}
.kpi {{ border: 1px solid {LINE}; border-radius: 13px; padding: .9rem .95rem; display: flex; gap: .75rem; align-items: center; height: 100%; }}
.kpi-ico {{ width: 40px; height: 40px; border-radius: 11px; flex: 0 0 40px; display: flex; align-items: center; justify-content: center; }}
.kpi-val {{ font-size: 1.16rem; font-weight: 700; color: {INK}; line-height: 1.15; }}
.kpi-val.sm {{ font-size: .95rem; }}
.kpi-lab {{ font-size: .705rem; color: {MUTED}; line-height: 1.35; margin-top: .16rem; }}
.acc {{ border: 1px solid {LINE}; border-radius: 14px; margin-bottom: .8rem; overflow: hidden; background: #fff; }}
.acc > summary {{ list-style: none; cursor: pointer; padding: .95rem 1.05rem; }}
.acc > summary::-webkit-details-marker {{ display: none; }}
.acc-head {{ display: flex; gap: .85rem; align-items: flex-start; }}
.acc-body {{ padding: 0 1.05rem 1.05rem 1.05rem; }}
.acc-name {{ font-size: .9rem; font-weight: 600; color: {INK}; margin: 0 0 .18rem 0; }}
.acc-desc {{ font-size: .78rem; color: {MUTED}; margin: 0; line-height: 1.5; }}
.acc-val {{ font-size: .93rem; font-weight: 700; color: {INK}; text-align: right; white-space: nowrap; }}
.acc-per {{ font-size: .715rem; color: {MUTED}; text-align: right; }}
.crit {{ border-radius: 11px; padding: .8rem .9rem; }}
.crit-t {{ font-size: .755rem; font-weight: 600; margin: 0 0 .45rem 0; }}
.crit ul {{ margin: 0; padding-left: 1.05rem; }}
.crit li {{ font-size: .755rem; color: #475569; line-height: 1.75; }}
.aviso {{ display: flex; gap: .7rem; background: #F5F3FF; border: 1px solid #E9E5FF; border-radius: 13px; padding: .85rem .95rem; margin-top: 1.5rem; }}
.aviso-t {{ font-size: .765rem; font-weight: 600; color: #4C3FD1; margin: 0; }}
.aviso-s {{ font-size: .745rem; color: #6D7CA8; margin: .1rem 0 0 0; }}

/* ---------------- Widgets ---------------- */
[data-baseweb="select"] > div {{ border-radius: 9px; border-color: {LINE}; background: #fff; min-height: 38px; font-size: .8rem; }}
.stTextInput input {{ border-radius: 9px; border: 1px solid {LINE}; font-size: .8rem; height: 38px; }}
label[data-testid="stWidgetLabel"] {{ display: none; }}
.empty {{ border: 1px dashed #D9DEEC; border-radius: 14px; padding: 2rem 1rem; text-align: center; color: {MUTED}; font-size: .82rem; }}
</style>
""",
    unsafe_allow_html=True,
)

# ===========================================================================
# 4. CAMADA DE DADOS
# ===========================================================================
RENOMEAR = {
    "ies_sigla": "Sigla da Instiuição de Ensino",
    "campus_nome": "Nome do Campus",
    "edital_numero": "Número do Edital de Auxílio",
    "ano_vigencia": "Ano de Públicação",
    "publico_alvo": "A quem se destina o edital",
    "modalidade_apoio": "Tipo de Apoio",
    "valor_mensal_brl": "Valor destinado ao beneficiário (R$)",
    "infraestrutura_disponivel": "Estrutura disponível:",
    "total_vagas_ofertadas": "Número de vagas ofertadas",
    "prazo_inscricao_dias": "Prazo de inscrição (em dias)",
    "criterios_elegibilidade": "Resumo dos Críterios de Elegibilidade",
    "ies_nome": "Nome da Instituição",
    "cod_estado": "Estado",
    "fonte_dado_site": "Edital disponível em:",
    "setor_responsavel": "Responsavel pelo edital",
}

PASTAS = [
    APP_DIR / "dados_app",
    APP_DIR,
    APP_DIR / "data",
    APP_DIR.parent / "data",
    APP_DIR.parent / "dados_app",
    Path.cwd() / "data",
    Path.cwd() / "app" / "dados_app",
]
PADROES_MVP = ["df_mvp*.csv", "data_base_CIAPE_mvp*.csv"]
PADROES_EDITAIS = ["df_editais*.csv", "fonte_dos_dados*.csv"]


def achar(padroes: list[str]) -> Path | None:
    for pasta in PASTAS:
        if not pasta.is_dir():
            continue
        for padrao in padroes:
            achados = sorted(pasta.glob(padrao))
            if achados:
                return achados[0]
    return None


def ler_csv(caminho: Path) -> pd.DataFrame:
    for enc in ("utf-8", "utf-8-sig", "latin1", "cp1252"):
        try:
            return pd.read_csv(caminho, sep=",", encoding=enc)
        except UnicodeDecodeError:
            continue
    return pd.read_csv(caminho, sep=",", encoding="latin1", engine="python")


def numerico(serie: pd.Series) -> pd.Series:
    """Converte para número aceitando formato BR ('1.234,56') e US ('1234.56')."""
    if pd.api.types.is_numeric_dtype(serie):
        return serie
    txt = serie.astype(str).str.strip().str.replace(r"[R$\s]", "", regex=True)
    br = txt.str.contains(",", na=False)
    txt = txt.where(~br, txt.str.replace(".", "", regex=False).str.replace(",", ".", regex=False))
    return pd.to_numeric(txt, errors="coerce")


def corrigir_coordenada(serie: pd.Series) -> pd.Series:
    """
    A tabela fonte veio com o separador de milhar quebrado
    (ex.: '-7.137.594' em vez de -7.137594), como registrado no notebook.
    """
    txt = serie.astype(str).str.strip()
    tem_dois_pontos = txt.str.count(r"\.") > 1
    txt = txt.where(~tem_dois_pontos, txt.str.replace(".", "", regex=False))
    valores = pd.to_numeric(txt.str.replace(",", ".", regex=False), errors="coerce")
    for _ in range(8):
        excedente = valores.abs() > 180
        if not excedente.any():
            break
        valores = valores.where(~excedente, valores / 1_000_000)
    return valores


def categorizar(tipo_apoio: str) -> str:
    """
    Traduz o termo local do edital para a categoria funcional do vocabulário
    controlado do projeto. Feito por texto, e não pela coluna `eixo_pnaes`,
    porque o notebook registra inconsistências pontuais nessa coluna.
    """
    t = str(tipo_apoio).lower().strip()
    if "restaurante universit" in t or "alimenta" in t or t == "serviço direto":
        return "Alimentação"
    if "pré-escolar" in t or "pre-escolar" in t or "creche" in t:
        return "Apoio à Criança (Creche)"
    if "residência universit" in t or "rumf" in t or "rufet" in t:
        return "Residência (vaga física)"
    if "faixa" in t or "transporte" in t:
        return "Transporte"
    if "moradia" in t or "auxílio 1" in t or "auxilio 1" in t or "aluguel" in t:
        return "Auxílio Aluguel"
    return "Outros"


def cidade_do_campus(nome: str) -> str:
    """
    Reduz o nome do campus à cidade-sede, para os rótulos do mapa.
    'Campus IV - Litoral Norte (Mamanguape e Rio Tinto)' -> 'Mamanguape'
    'Campus I - João Pessoa e Santa Rita'                -> 'João Pessoa'
    """
    texto = str(nome)
    entre_parenteses = re.search(r"\((.*?)\)", texto)
    if entre_parenteses:
        base = entre_parenteses.group(1)
    else:
        partes = texto.split(" - ", 1)
        base = partes[1] if len(partes) > 1 else partes[0]
    return re.split(r"\s+e\s+|,|/", base)[0].strip()


def romano(nome: str) -> str:
    achado = re.search(r"campus[\s\-_]*([IVXLCDM]+)", str(nome), flags=re.IGNORECASE)
    return achado.group(1).upper() if achado else ""


@st.cache_data(show_spinner="Carregando a base do CIAPE...")
def carregar() -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    caminho_mvp, caminho_ed = achar(PADROES_MVP), achar(PADROES_EDITAIS)
    if caminho_mvp is None:
        raise FileNotFoundError("df_mvp")

    df = ler_csv(caminho_mvp)
    df = df.rename(columns={k: v for k, v in RENOMEAR.items() if k in df.columns})

    editais = pd.DataFrame()
    if caminho_ed is not None:
        editais = ler_csv(caminho_ed)
        for col in ("loc_latitude", "loc_longitute"):
            if col in editais.columns:
                editais[col] = corrigir_coordenada(editais[col])
        if "campus_romano" not in editais.columns and "nome_edital" in editais.columns:
            editais["campus_romano"] = (
                editais["nome_edital"]
                .str.extract(r"campus[\s\-_]*([IVXLCDM]+)", flags=re.IGNORECASE, expand=False)
                .str.upper()
            )

    # --- tipagem ---
    for col in (
        "Valor destinado ao beneficiário (R$)",
        "Número de vagas ofertadas",
        "Prazo de inscrição (em dias)",
        "Estrutura disponível:",
    ):
        if col in df.columns:
            df[col] = numerico(df[col])

    # O ano chega ora como inteiro (2025), ora como data ('2025-01-01'). Tratar
    # inteiro via to_datetime o interpretaria como epoch e devolveria 1970.
    bruto = df["Ano de Públicação"]
    como_numero = numerico(bruto)
    anos = pd.Series(pd.NA, index=df.index, dtype="Int64")
    ja_e_ano = como_numero.between(1900, 2100)
    anos[ja_e_ano] = como_numero[ja_e_ano].astype(int)
    if (~ja_e_ano).any():
        datas = pd.to_datetime(bruto[~ja_e_ano].astype(str), errors="coerce", format="mixed")
        anos[~ja_e_ano] = datas.dt.year.astype("Int64")
    df["Ano"] = anos
    df = df[df["Ano"].notna()].copy()

    # --- coordenadas (fonte oficial = tabela de editais) ---
    for col in ("loc_latitude", "loc_longitute"):
        if col in df.columns:
            df[col] = corrigir_coordenada(df[col])

    df["campus_romano"] = df["Nome do Campus"].apply(romano)
    if not editais.empty and "campus_romano" in editais.columns:
        coords = (
            editais.dropna(subset=["loc_latitude", "loc_longitute"])
            .drop_duplicates("campus_romano")
            .set_index("campus_romano")[["loc_latitude", "loc_longitute"]]
        )
        for col in ("loc_latitude", "loc_longitute"):
            de_fonte = df["campus_romano"].map(coords[col])
            df[col] = de_fonte if col not in df.columns else df[col].fillna(de_fonte)

    # --- derivadas ---
    df["Categoria"] = df["Tipo de Apoio"].apply(categorizar)
    df["Cidade"] = df["Nome do Campus"].apply(cidade_do_campus)

    if "A quem se destina o edital" in df.columns:
        codigos = numerico(df["A quem se destina o edital"])
        df["Público-alvo"] = codigos.map(MAPA_PUBLICO).fillna(
            df["A quem se destina o edital"].astype(str)
        )
    else:
        df["Público-alvo"] = "Não informado"

    if "eixo_pnaes" in df.columns:
        df["Eixo PNAES"] = numerico(df["eixo_pnaes"]).map(MAPA_EIXO).fillna("Não classificado")
    else:
        df["Eixo PNAES"] = "Não classificado"

    ano_recente = int(df["Ano"].max())
    df["Situação"] = df["Ano"].apply(
        lambda a: "Edital vigente" if a == ano_recente else "Edital de ano anterior"
    )

    # --- dicionário de campi (só o que existe na base) ---
    campi: dict[str, dict] = {}
    for nome, bloco in df.groupby("Nome do Campus", sort=True):
        campi[nome] = {
            "nome": nome,
            "cidade": cidade_do_campus(nome),
            "romano": bloco["campus_romano"].iloc[0],
            "lat": float(bloco["loc_latitude"].dropna().iloc[0]) if bloco["loc_latitude"].notna().any() else None,
            "lon": float(bloco["loc_longitute"].dropna().iloc[0]) if bloco["loc_longitute"].notna().any() else None,
        }
    return df, editais, campi


try:
    DF, DF_EDITAIS, CAMPI = carregar()
except FileNotFoundError:
    st.error("**Base de dados não encontrada.**")
    st.markdown(
        "O app procura por `df_mvp*.csv` / `data_base_CIAPE_mvp*.csv` (e a tabela fonte "
        "`df_editais*.csv` / `fonte_dos_dados*.csv`) nas pastas:\n\n"
        + "\n".join(f"- `{p}`" for p in PASTAS)
        + "\n\nCopie os CSVs exportados no notebook para uma dessas pastas e recarregue."
    )
    st.stop()

ANOS = sorted([int(a) for a in DF["Ano"].dropna().unique()], reverse=True)
IES = sorted(DF["Nome da Instituição"].dropna().unique().tolist()) or ["—"]
CATEGORIAS = ["Todos"] + sorted(DF["Categoria"].unique().tolist())
PUBLICOS = ["Todos"] + sorted(DF["Público-alvo"].astype(str).unique().tolist())

# ===========================================================================
# 5. ESTADO
# ===========================================================================
st.session_state.setdefault("pagina", "Sobre")
st.session_state.setdefault("campus_sel", next(iter(CAMPI)))
st.session_state.setdefault("painel_aberto", True)

# ===========================================================================
# 6. HELPERS DE RENDERIZAÇÃO
# ===========================================================================
def brl(valor: float) -> str:
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def cor_de(categoria: str) -> dict:
    return CORES.get(categoria, CORES["Outros"])


def criterios_em_lista(texto: str) -> list[str]:
    bruto = str(texto or "").strip()
    if not bruto or bruto.lower() == "nan":
        return ["Critérios não informados neste edital."]
    partes = [p.strip(" ;.\n\t") for p in re.split(r"[;\n]+|\s\u2022\s", bruto) if p.strip(" ;.\n\t")]
    return [p[0].upper() + p[1:] + ";" for p in partes] or [bruto]


def rotulo_valor(linha: pd.Series) -> tuple[str, str, str]:
    """Retorna (texto do valor, periodicidade, classe css)."""
    valor = linha.get("Valor destinado ao beneficiário (R$)")
    vagas = linha.get("Número de vagas ofertadas")
    if pd.notna(valor) and valor > 0:
        return brl(float(valor)), "Mensal", "price"
    if pd.notna(vagas) and vagas > 0:
        return f"{int(vagas)} vagas", "Vaga / serviço", "price vaga"
    return "Serviço direto", "Sem repasse financeiro", "price vaga"


def kpi(icone: str, fundo: str, cor: str, valor: str, rotulo: str, pequeno: bool = False) -> str:
    return (
        f'<div class="kpi"><div class="kpi-ico" style="background:{fundo};">{svg(icone, 20, cor)}</div>'
        f'<div><div class="kpi-val{" sm" if pequeno else ""}">{valor}</div>'
        f'<div class="kpi-lab">{rotulo}</div></div></div>'
    )


def caminho_svg_pb(largura: int = 360, altura: int = 210) -> str:
    lons = [c[0] for c in PB_POLIGONO]
    lats = [c[1] for c in PB_POLIGONO]
    x0, x1, y0, y1 = min(lons), max(lons), min(lats), max(lats)
    pontos = [
        f"{(lon - x0) / (x1 - x0) * largura:.1f},{(y1 - lat) / (y1 - y0) * altura:.1f}"
        for lon, lat in PB_POLIGONO
    ]
    return "M" + "L".join(pontos) + "Z"


# ===========================================================================
# 7. SIDEBAR
# ===========================================================================
with st.sidebar:
    st.markdown(
        f'<div class="brand"><div class="brand-mark">{svg(P["capelo"], 21, "#fff", 1.9)}</div>'
        '<div><div class="brand-name">CIAPE</div>'
        '<div class="brand-sub">Central de Informações e<br>Apoio a Programas Estudantis</div>'
        "</div></div>",
        unsafe_allow_html=True,
    )

    for rotulo, icone in [
        ("Sobre", ":material/info:"),
        ("Consultar", ":material/search:"),
        ("Dashboard", ":material/bar_chart:"),
        ("Relatório", ":material/description:"),
    ]:
        if st.button(
            rotulo,
            icon=icone,
            key=f"nav_{rotulo}",
            **LARGURA,
            type="primary" if st.session_state.pagina == rotulo else "tertiary",
        ):
            st.session_state.pagina = rotulo
            st.rerun()

    st.markdown(
        f'<div class="side-card">{svg(P["marcador"], 17, "#6E7FA8")}'
        "<p>Use os filtros para encontrar os auxílios disponíveis de acordo com o que você precisa.</p></div>",
        unsafe_allow_html=True,
    )
    st.markdown("<div style='height:2.4rem'></div>", unsafe_allow_html=True)
    st.markdown('<p class="side-foot">Download de dados</p>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="side-dl">{svg(P["download"], 16, "#93A0B8")}'
        "<span>Baixar base completa em CSV</span></div>",
        unsafe_allow_html=True,
    )
    st.download_button(
        "Baixar base completa",
        data=DF.to_csv(index=False).encode("utf-8-sig"),
        file_name="ciape_base_completa.csv",
        mime="text/csv",
        **LARGURA,
        key="dl_base",
    )

PAGINA = st.session_state.pagina

# ===========================================================================
# 8. PÁGINA — SOBRE
# ===========================================================================
if PAGINA == "Sobre":
    with st.container(key="painel_full"):
        st.markdown(
            f"""
<div class="hero">
  <svg class="hero-map" width="360" height="210" viewBox="0 0 360 210" xmlns="http://www.w3.org/2000/svg">
    <path d="{caminho_svg_pb()}" fill="#E7E4FD" stroke="#C7C0F7" stroke-width="1.5"/>
  </svg>
  <h1>CIAPE</h1>
  <h2>Informação que conecta você a oportunidades.</h2>
  <p>O CIAPE reúne e organiza as informações sobre os programas de Apoio e Permanência
     Estudantil (APE) das instituições públicas de ensino superior, para que estudantes em
     situação de vulnerabilidade social possam planejar a jornada acadêmica com mais segurança.
     Este MVP cobre os editais unificados da UFPB.</p>
</div>
""",
            unsafe_allow_html=True,
        )

        if st.button("Ir para a consulta  →", key="cta_consultar", type="primary"):
            st.session_state.pagina = "Consultar"
            st.rerun()

        st.markdown('<p class="sec-title">Para quem o CIAPE é feito</p>', unsafe_allow_html=True)
        st.caption(
            "As duas personas abaixo orientam a pergunta de negócio do projeto, "
            "definida no notebook de análise."
        )

        pa, pb = st.columns(2)
        personas = [
            (
                "Jucelino",
                "Persona · estudante de outro estado",
                "#EEF2FF",
                ACCENT,
                "Não possui rede de apoio nas cidades onde a UFPB atua. É beneficiário de programas "
                "de assistência social, como o Bolsa Família, e não tem condições financeiras de se "
                "manter na cidade por conta própria.",
            ),
            (
                "Gertrudes",
                "Persona · residente na Paraíba",
                "#FDF2F8",
                "#EC4899",
                "Dependendo do campus, precisa pegar de dois a três ônibus diários e não tem condições "
                "de pagar pelas refeições na universidade nem de trazê-las de casa.",
            ),
        ]
        for coluna, (nome, tag, fundo, cor, texto) in zip((pa, pb), personas):
            with coluna:
                st.markdown(
                    f'<div class="persona"><div class="persona-top">'
                    f'<div class="persona-av" style="background:{fundo};">{svg(P["pessoas"], 22, cor)}</div>'
                    f'<div><p class="persona-nome">{nome}</p><p class="persona-tag" style="color:{cor};">{tag}</p></div>'
                    f'</div><p>{texto}</p></div>',
                    unsafe_allow_html=True,
                )

        st.markdown(
            '<p class="sec-title">A pergunta que o produto responde</p>'
            '<p class="sub">Como apoiar a tomada de decisão de pessoas leigas durante a escolha do local '
            "de estudo, de modo que consigam identificar qual campus da UFPB oferece os melhores programas "
            "de apoio e permanência para perfis como os de Jucelino e Gertrudes?</p>",
            unsafe_allow_html=True,
        )

        st.markdown('<p class="sec-title">O MVP em números</p>', unsafe_allow_html=True)
        e1, e2, e3, e4 = st.columns(4)
        estatisticas = [
            (e1, f"{DF['Nome do Campus'].nunique()}", "campi da UFPB mapeados"),
            (e2, f"{len(DF)}", "registros de modalidade de apoio"),
            (e3, f"{len(ANOS)}", f"anos de edital ({min(ANOS)}–{max(ANOS)})"),
            (e4, f"{DF['Categoria'].nunique()}", "categorias funcionais de auxílio"),
        ]
        for coluna, numero, rotulo in estatisticas:
            with coluna:
                st.markdown(
                    f'<div class="stat"><b>{numero}</b><span>{rotulo}</span></div>',
                    unsafe_allow_html=True,
                )

        st.markdown('<p class="sec-title">Escalabilidade</p>', unsafe_allow_html=True)
        st.markdown(
            '<p class="sub">O dimensionamento do projeto usou os microdados do Censo da Educação '
            "Superior (INEP, referentes a 2024): o Brasil possui 2.561 IES, das quais 317 são públicas "
            "e 261 pertencem às esferas administrativas federal e estadual. O MVP começa pela UFPB, "
            "mas a estrutura de dados (Estado–IES–Campus) foi desenhada para receber outras "
            "instituições sem reescrita.</p>",
            unsafe_allow_html=True,
        )

        st.markdown('<p class="sec-title">Fonte dos dados e responsável</p>', unsafe_allow_html=True)
        st.markdown(
            "- **Editais:** seleção unificada de apoio e permanência estudantil da PRAPE/UFPB "
            "(https://www.prape.ufpb.br/editais/).\n"
            "- **Escala:** Censo da Educação Superior — INEP.\n"
            "- **Responsável:** Everton Gabriel Silva de Almeida — everton.gabriel@academico.ufpb.br.\n"
            "- **Contexto acadêmico:** disciplina de Análise de Dados, curso de Ciência de Dados "
            "para Negócios, CCSA/UFPB."
        )
    st.stop()

# ===========================================================================
# 9. PÁGINA — DASHBOARD
# ===========================================================================
if PAGINA == "Dashboard":
    with st.container(key="painel_full"):
        st.markdown(
            '<p class="h1">Dashboard analítico</p>'
            '<p class="sub">Agrupamentos das perguntas analíticas do projeto (Q1–Q10), '
            "calculados sobre a base do MVP.</p>",
            unsafe_allow_html=True,
        )

        ano_dash = st.selectbox("Ano do edital", ["Todos"] + [str(a) for a in ANOS], key="dash_ano")
        base = DF if ano_dash == "Todos" else DF[DF["Ano"] == int(ano_dash)]

        k1, k2, k3, k4 = st.columns(4)
        vagas = int(base["Número de vagas ofertadas"].sum(skipna=True))
        valores = base.loc[base["Valor destinado ao beneficiário (R$)"] > 0, "Valor destinado ao beneficiário (R$)"]
        with k1:
            st.markdown(kpi(P["predio"], "#EEF2FF", ACCENT, str(base["Nome do Campus"].nunique()), "Campi com edital"), unsafe_allow_html=True)
        with k2:
            st.markdown(kpi(P["cadeira"], "#ECFDF5", "#0E9F6E", f"{vagas:,}".replace(",", "."), "Vagas ofertadas"), unsafe_allow_html=True)
        with k3:
            media = brl(valores.mean()) if not valores.empty else "—"
            st.markdown(kpi(P["dinheiro"], "#F0FDF4", "#16A34A", media, "Valor médio do auxílio", True), unsafe_allow_html=True)
        with k4:
            prazo = base["Prazo de inscrição (em dias)"].mean()
            st.markdown(kpi(P["info"], "#FFF7ED", "#F97316", f"{prazo:.0f} dias" if pd.notna(prazo) else "—", "Prazo médio de inscrição", True), unsafe_allow_html=True)

        st.markdown('<p class="sec-title">Q1 · Eixos PNAES por campus</p>', unsafe_allow_html=True)
        st.caption(
            "Legenda oficial da coluna `eixo_pnaes` (1 Moradia · 2 Transporte · 3 Alimentação). "
            "O notebook registra inconsistências pontuais nessa coluna — por isso os filtros da "
            "consulta usam a categoria derivada do texto do edital."
        )
        q1 = base.groupby(["Cidade", "Eixo PNAES"]).size().reset_index(name="Registros")
        st.bar_chart(q1, x="Cidade", y="Registros", color="Eixo PNAES", height=300)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<p class="sec-title">Q2 · Vagas por categoria</p>', unsafe_allow_html=True)
            q2 = base.groupby(["Cidade", "Categoria"])["Número de vagas ofertadas"].sum().reset_index()
            st.bar_chart(q2, x="Cidade", y="Número de vagas ofertadas", color="Categoria", height=300)
        with c2:
            st.markdown('<p class="sec-title">Q7 · Valor médio do auxílio por campus</p>', unsafe_allow_html=True)
            q7 = (
                base[base["Valor destinado ao beneficiário (R$)"] > 0]
                .groupby("Cidade")["Valor destinado ao beneficiário (R$)"]
                .mean()
                .reset_index()
            )
            st.bar_chart(q7, x="Cidade", y="Valor destinado ao beneficiário (R$)", height=300)

        c3, c4 = st.columns(2)
        with c3:
            st.markdown('<p class="sec-title">Q3 · Vagas em residência universitária</p>', unsafe_allow_html=True)
            q3 = (
                base[base["Categoria"] == "Residência (vaga física)"]
                .groupby("Cidade")["Número de vagas ofertadas"]
                .sum()
                .reset_index()
            )
            if q3.empty:
                st.markdown('<div class="empty">Nenhuma vaga de residência neste recorte.</div>', unsafe_allow_html=True)
            else:
                st.bar_chart(q3, x="Cidade", y="Número de vagas ofertadas", height=280)
        with c4:
            st.markdown('<p class="sec-title">Q10 · Prazo médio de inscrição</p>', unsafe_allow_html=True)
            q10 = base.groupby("Cidade")["Prazo de inscrição (em dias)"].mean().reset_index()
            st.bar_chart(q10, x="Cidade", y="Prazo de inscrição (em dias)", height=280)

        st.markdown('<p class="sec-title">Q4 e Q5 · Infraestrutura x auxílio financeiro</p>', unsafe_allow_html=True)
        infra = (
            base.assign(
                **{
                    "Tem R.U.": base["Categoria"].eq("Alimentação") & base["Valor destinado ao beneficiário (R$)"].fillna(0).eq(0),
                    "Tem residência": base["Categoria"].eq("Residência (vaga física)"),
                    "Tem auxílio financeiro": base["Valor destinado ao beneficiário (R$)"].fillna(0) > 0,
                }
            )
            .groupby("Nome do Campus")[["Tem R.U.", "Tem residência", "Tem auxílio financeiro"]]
            .any()
            .replace({True: "Sim", False: "Não"})
            .reset_index()
        )
        st.dataframe(infra, **LARGURA, hide_index=True)
    st.stop()

# ===========================================================================
# 10. PÁGINA — RELATÓRIO
# ===========================================================================
if PAGINA == "Relatório":
    with st.container(key="painel_full"):
        st.markdown(
            '<p class="h1">Relatório e rastreabilidade</p>'
            '<p class="sub">Tabelas analíticas e origem de cada edital, para auditoria da base.</p>',
            unsafe_allow_html=True,
        )

        st.markdown('<p class="sec-title">Q11 · Origem dos editais</p>', unsafe_allow_html=True)
        colunas_origem = [
            c
            for c in ["Nome do Campus", "Nome da Instituição", "Responsavel pelo edital", "Ano", "Edital disponível em:"]
            if c in DF.columns
        ]
        q11 = DF[colunas_origem].drop_duplicates().sort_values(colunas_origem[0])
        st.dataframe(
            q11,
            **LARGURA,
            hide_index=True,
            column_config={"Edital disponível em:": st.column_config.LinkColumn("Edital disponível em:")},
        )

        if not DF_EDITAIS.empty:
            st.markdown('<p class="sec-title">Tabela fonte dos editais</p>', unsafe_allow_html=True)
            st.caption("Arquivo `fonte_dos_dados` / `df_editais`: chave de rastreabilidade do projeto.")
            st.dataframe(DF_EDITAIS, **LARGURA, hide_index=True)

        st.markdown('<p class="sec-title">Q6 · Auxílios financeiros por campus</p>', unsafe_allow_html=True)
        q6 = (
            DF[DF["Valor destinado ao beneficiário (R$)"] > 0][
                ["Nome do Campus", "Tipo de Apoio", "Categoria", "Ano", "Valor destinado ao beneficiário (R$)"]
            ]
            .drop_duplicates()
            .sort_values(["Nome do Campus", "Valor destinado ao beneficiário (R$)"], ascending=[True, False])
        )
        st.dataframe(q6, **LARGURA, hide_index=True)

        st.markdown('<p class="sec-title">Q7–Q9 · Resumo estatístico do valor do auxílio</p>', unsafe_allow_html=True)
        nivel = st.selectbox(
            "Nível de agregação",
            ["Nome do Campus", "Sigla da Instiuição de Ensino", "Estado"],
            key="rel_nivel",
        )
        if nivel in DF.columns:
            resumo = (
                DF.groupby([nivel, "Ano"])["Valor destinado ao beneficiário (R$)"]
                .agg(media="mean", mediana="median", minimo="min", maximo="max", registros="count")
                .reset_index()
            )
            st.dataframe(resumo, **LARGURA, hide_index=True)
            st.download_button(
                "Baixar este resumo em CSV",
                data=resumo.to_csv(index=False).encode("utf-8-sig"),
                file_name=f"ciape_resumo_{nivel.lower().replace(' ', '_')}.csv",
                mime="text/csv",
                key="dl_resumo",
            )

        st.markdown('<p class="sec-title">Nota metodológica</p>', unsafe_allow_html=True)
        st.markdown(
            "- O identificador `ID_completo` segue a hierarquia **Estado–IES–Campus**, construída "
            "por mineração dos numerais romanos no nome do campus e casada com o código oficial "
            "da tabela fonte.\n"
            "- As colunas `loc_latitude` / `loc_longitute` chegaram com o separador de milhar "
            "quebrado e são corrigidas na carga.\n"
            "- A categoria funcional exibida na consulta vem do texto de `Tipo de Apoio` "
            "(vocabulário controlado), e não de `eixo_pnaes`, cuja legenda apresenta "
            "inconsistências pontuais.\n"
            "- `Público-alvo` está constante no MVP atual: a segmentação só ganha valor quando "
            "outras IES entrarem na base."
        )
    st.stop()

# ===========================================================================
# 11. PÁGINA — CONSULTAR
# ===========================================================================
def tooltip_campus(nome: str, ano: int) -> str:
    bloco = DF[(DF["Nome do Campus"] == nome) & (DF["Ano"] == ano)]
    itens = ""
    for categoria in bloco["Categoria"].drop_duplicates():
        cor = cor_de(categoria)
        itens += (
            f'<div style="display:flex;gap:8px;align-items:center;margin:5px 0;">'
            f'<span style="width:18px;height:18px;border-radius:5px;background:{cor["solid"]};'
            f'display:inline-flex;align-items:center;justify-content:center;">'
            f'{svg(P[cor["icone"]], 11, "#fff", 2.2)}</span>'
            f'<span style="font-size:11.5px;color:#0F172A;">{categoria}</span></div>'
        )
    if not itens:
        itens = '<div style="font-size:11.5px;color:#94A3B8;">Sem registro neste ano.</div>'
    campus = CAMPI[nome]
    return (
        f'<div style="min-width:200px;">'
        f'<div style="font-size:14px;font-weight:700;color:#0F172A;">{campus["cidade"]}</div>'
        f'<div style="font-size:11px;color:#64748B;margin-top:1px;">{nome}</div>'
        f'<div style="height:1px;background:#E7E9F2;margin:9px 0;"></div>'
        f'<div style="font-size:11px;font-weight:600;color:#334155;margin-bottom:3px;">'
        f"Principais auxílios disponíveis</div>{itens}"
        f'<div style="height:1px;background:#E7E9F2;margin:9px 0 7px 0;"></div>'
        f'<div style="font-size:10.5px;color:#94A3B8;line-height:1.4;">'
        f"Clique para ver detalhes e<br>critérios de elegibilidade.</div></div>"
    )


@st.cache_data(show_spinner=False)
def malha_paraiba() -> dict:
    try:
        import requests

        url = (
            "https://servicodados.ibge.gov.br/api/v3/malhas/estados/25"
            "?formato=application/vnd.geo+json&qualidade=intermediaria"
        )
        resposta = requests.get(url, timeout=6)
        resposta.raise_for_status()
        return resposta.json()
    except Exception:
        return {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {"nome": "Paraíba"},
                    "geometry": {"type": "Polygon", "coordinates": [[list(c) for c in PB_POLIGONO]]},
                }
            ],
        }


def construir_mapa(ano: int, selecionado: str) -> folium.Map:
    mapa = folium.Map(
        location=[-7.05, -36.4],
        zoom_start=7,
        tiles=None,
        scrollWheelZoom=False,
        attributionControl=False,
    )
    folium.GeoJson(
        malha_paraiba(),
        style_function=lambda _: {
            "fillColor": "#D7E3D3",
            "color": "#B9CBB6",
            "weight": 1.2,
            "fillOpacity": 0.95,
        },
    ).add_to(mapa)

    for nome, campus in CAMPI.items():
        if campus["lat"] is None or campus["lon"] is None:
            continue
        ativo = nome == selecionado
        tamanho = 14 if ativo else 10
        preenchimento = "#E63946" if ativo else "#FFFFFF"
        borda = "#E63946" if ativo else "#94A3B8"
        anel = "box-shadow:0 0 0 5px rgba(230,57,70,.18);" if ativo else "box-shadow:0 1px 3px rgba(0,0,0,.18);"
        html = (
            f'<div style="display:flex;align-items:center;gap:7px;'
            f'transform:translate(-{tamanho // 2}px,-{tamanho // 2}px);">'
            f'<span style="width:{tamanho}px;height:{tamanho}px;border-radius:50%;'
            f'background:{preenchimento};border:2px solid {borda};{anel}display:block;"></span>'
            f'<span style="font-size:12.5px;font-weight:{600 if ativo else 500};color:#334155;'
            f'white-space:nowrap;text-shadow:0 1px 2px #fff,0 -1px 2px #fff,1px 0 2px #fff,-1px 0 2px #fff;">'
            f'{campus["cidade"]}</span></div>'
        )
        folium.Marker(
            location=[campus["lat"], campus["lon"]],
            icon=folium.DivIcon(html=html, icon_size=(0, 0), icon_anchor=(0, 0)),
            tooltip=folium.Tooltip(tooltip_campus(nome, ano), sticky=True),
        ).add_to(mapa)

    mapa.get_root().header.add_child(
        folium.Element(
            """
<style>
  .folium-map, .leaflet-container { background:#EDF3F8 !important; font-family:'Inter',sans-serif; }
  .leaflet-top.leaflet-left { left:auto; right:12px; }
  .leaflet-control-zoom { border:none !important; box-shadow:0 2px 8px rgba(16,24,40,.12);
      border-radius:9px; overflow:hidden; }
  .leaflet-control-zoom a { background:#fff; color:#475569; border:none !important;
      width:30px; height:30px; line-height:29px; font-size:17px; }
  .leaflet-control-zoom a:first-child { border-bottom:1px solid #EEF0F6 !important; }
  .leaflet-tooltip { background:#fff; border:1px solid #E7E9F2; border-radius:12px;
      box-shadow:0 10px 30px rgba(16,24,40,.14); padding:12px 13px; opacity:1 !important; }
  .leaflet-tooltip:before { display:none; }
</style>
"""
        )
    )
    return mapa


painel = st.session_state.painel_aberto
col_esq, col_dir = st.columns([6, 4], gap="medium") if painel else (st.container(), None)

# ------------------------------------------------------------------ ESQUERDA
with col_esq:
    with st.container(key="painel_esq"):
        cab_e, cab_d = st.columns([1.35, 1], vertical_alignment="center")
        with cab_e:
            st.markdown(
                '<p class="h1">Consulte programas e auxílios</p>'
                '<p class="sub">Explore os programas de assistência estudantil disponíveis na Paraíba.</p>',
                unsafe_allow_html=True,
            )
        with cab_d:
            with st.container(key="inst_box"):
                ci, cs = st.columns([0.16, 1], vertical_alignment="center")
                with ci:
                    st.markdown(
                        f'<div class="inst-mark">{svg(P["predio"], 18, ACCENT)}</div>',
                        unsafe_allow_html=True,
                    )
                with cs:
                    st.markdown('<p class="inst-lab">Instituição de Ensino</p>', unsafe_allow_html=True)
                    ies_sel = st.selectbox("IES", IES, label_visibility="collapsed", key="f_ies")

        # --------------------------- Filtros ---------------------------
        with st.container(key="filtros"):
            f1, f2, f3, f4 = st.columns([1, 1, 1, 1.15])
            with f1:
                st.markdown('<p class="flabel">Tipo de auxílio</p>', unsafe_allow_html=True)
                f_tipo = st.selectbox("Tipo", CATEGORIAS, label_visibility="collapsed", key="f_tipo")
            with f2:
                st.markdown('<p class="flabel">Público-alvo</p>', unsafe_allow_html=True)
                f_publico = st.selectbox("Público", PUBLICOS, label_visibility="collapsed", key="f_pub")
            with f3:
                st.markdown('<p class="flabel">Ano do edital</p>', unsafe_allow_html=True)
                f_ano = st.selectbox("Ano", ANOS, label_visibility="collapsed", key="f_ano")
            with f4:
                st.markdown('<p class="flabel">&nbsp;</p>', unsafe_allow_html=True)
                f_busca = st.text_input(
                    "Busca",
                    placeholder="Buscar por palavra-chave...",
                    label_visibility="collapsed",
                    key="f_busca",
                )

        # ----------------------------- Mapa -----------------------------
        with st.container(key="mapa_card"):
            st.markdown(
                '<p class="map-title">Campi da UFPB</p>'
                '<p class="map-sub">Passe o mouse sobre os campi para ver os programas disponíveis.</p>',
                unsafe_allow_html=True,
            )
            estado_mapa = st_folium(
                construir_mapa(int(f_ano), st.session_state.campus_sel),
                height=430,
                use_container_width=True,
                returned_objects=["last_object_clicked"],
                key=f"mapa_{f_ano}",
            )

        clique = (estado_mapa or {}).get("last_object_clicked")
        if clique:
            for nome, campus in CAMPI.items():
                if campus["lat"] is None:
                    continue
                perto = abs(clique["lat"] - campus["lat"]) < 0.06 and abs(clique["lng"] - campus["lon"]) < 0.06
                if perto and (st.session_state.campus_sel != nome or not st.session_state.painel_aberto):
                    st.session_state.campus_sel = nome
                    st.session_state.painel_aberto = True
                    st.rerun()

        # ---------------------------- Lista ----------------------------
        termo = (f_busca or "").strip().lower()
        filtrado = DF[(DF["Ano"] == int(f_ano)) & (DF["Nome da Instituição"] == ies_sel)]
        if f_tipo != "Todos":
            filtrado = filtrado[filtrado["Categoria"] == f_tipo]
        if f_publico != "Todos":
            filtrado = filtrado[filtrado["Público-alvo"].astype(str) == f_publico]
        if termo:
            alvo = (
                filtrado["Tipo de Apoio"].astype(str)
                + " " + filtrado["Nome do Campus"].astype(str)
                + " " + filtrado["Categoria"].astype(str)
                + " " + filtrado["Resumo dos Críterios de Elegibilidade"].astype(str)
            )
            filtrado = filtrado[alvo.str.lower().str.contains(re.escape(termo), na=False)]

        st.markdown(
            f'<div class="list-head"><h3>Programas disponíveis na '
            f'{DF["Sigla da Instiuição de Ensino"].iloc[0]}</h3>'
            f'<span class="pill-count">{len(filtrado)} programas</span></div>',
            unsafe_allow_html=True,
        )

        if filtrado.empty:
            st.markdown(
                '<div class="empty">Nenhum programa corresponde a esses filtros. '
                "Ajuste o tipo de auxílio, o público-alvo ou limpe a busca.</div>",
                unsafe_allow_html=True,
            )
        else:
            for posicao, (indice, linha) in enumerate(filtrado.iterrows()):
                cor = cor_de(linha["Categoria"])
                valor_txt, periodicidade, classe = rotulo_valor(linha)
                vagas = linha.get("Número de vagas ofertadas")
                vagas_txt = f"{int(vagas)} vagas ofertadas" if pd.notna(vagas) else "vagas não informadas"
                with st.container(key=f"prog_{indice}_{posicao}"):
                    esq, dir_ = st.columns([6.4, 2.1], vertical_alignment="center")
                    with esq:
                        st.markdown(
                            f'<div class="pc"><div class="tile" style="background:{cor["solid"]};">'
                            f'{svg(P[cor["icone"]], 21, "#fff")}</div><div>'
                            f'<p class="pc-name">{linha["Tipo de Apoio"]}</p>'
                            f'<p class="pc-scope">{linha["Nome do Campus"]} · {linha["Público-alvo"]}</p>'
                            f'<p class="pc-desc">{linha["Categoria"]} — {vagas_txt}. '
                            f'Prazo de inscrição de {linha["Prazo de inscrição (em dias)"]:.0f} dias.</p>'
                            f"</div></div>",
                            unsafe_allow_html=True,
                        )
                    with dir_:
                        st.markdown(
                            f'<div class="price-row"><span class="{classe}">{valor_txt}</span>'
                            f'<span class="period">{periodicidade}</span></div>',
                            unsafe_allow_html=True,
                        )
                        with st.container(key=f"btn_{indice}_{posicao}"):
                            if st.button("Ver detalhes  →", key=f"ver_{indice}_{posicao}", **LARGURA):
                                st.session_state.campus_sel = linha["Nome do Campus"]
                                st.session_state.painel_aberto = True
                                st.rerun()

# -------------------------------------------------------------------- DIREITA
def acordeao(linha: pd.Series) -> str:
    cor = cor_de(linha["Categoria"])
    valor_txt, periodicidade, _ = rotulo_valor(linha)
    itens = "".join(f"<li>{c}</li>" for c in criterios_em_lista(linha["Resumo dos Críterios de Elegibilidade"]))
    vagas = linha.get("Número de vagas ofertadas")
    vagas_txt = f"{int(vagas)} vagas ofertadas" if pd.notna(vagas) else "vagas não informadas"
    return f"""
<details class="acc" open>
  <summary>
    <div class="acc-head">
      <div class="tile" style="background:{cor['solid']};">{svg(P[cor['icone']], 21, "#fff")}</div>
      <div style="flex:1;min-width:0;">
        <p class="acc-name">{linha['Tipo de Apoio']}</p>
        <p class="acc-desc">{linha['Categoria']} — {vagas_txt}.
           Edital {linha.get('Número do Edital de Auxílio', '—')}.</p>
      </div>
      <div style="flex:0 0 auto;display:flex;gap:.5rem;">
        <div><div class="acc-val">{valor_txt}</div><div class="acc-per">{periodicidade}</div></div>
        <span style="margin-top:3px;">{svg(P['chevron'], 16, "#94A3B8")}</span>
      </div>
    </div>
  </summary>
  <div class="acc-body">
    <div class="crit" style="background:{cor['tint']};border:1px solid {cor['border']};">
      <p class="crit-t" style="color:{cor['solid']};">Critérios de elegibilidade</p>
      <ul>{itens}</ul>
    </div>
  </div>
</details>
"""


if painel and col_dir is not None:
    with col_dir:
        with st.container(key="painel_dir"):
            nome_campus = st.session_state.campus_sel
            campus = CAMPI[nome_campus]
            bloco = DF[(DF["Nome do Campus"] == nome_campus) & (DF["Ano"] == int(f_ano))]

            t_esq, t_dir = st.columns([8, 1], vertical_alignment="top")
            with t_esq:
                st.markdown(
                    f'<p class="dp-title">{nome_campus}</p>'
                    f'<p class="dp-city">{campus["cidade"]} · PB — edital de {f_ano}</p>',
                    unsafe_allow_html=True,
                )
            with t_dir:
                with st.container(key="fechar"):
                    if st.button("✕", key="btn_fechar", help="Fechar painel"):
                        st.session_state.painel_aberto = False
                        st.rerun()

            aba_geral, aba_progs = st.tabs(["Visão geral", "Programas disponíveis"])

            with aba_geral:
                maiores = bloco.loc[bloco["Valor destinado ao beneficiário (R$)"] > 0, "Valor destinado ao beneficiário (R$)"]
                maior_txt = brl(maiores.max()) if not maiores.empty else "Sem repasse"
                vagas_total = int(bloco["Número de vagas ofertadas"].sum(skipna=True))
                k1, k2, k3 = st.columns(3)
                with k1:
                    st.markdown(kpi(P["banco"], "#EEF2FF", ACCENT, str(len(bloco)), "Programas<br>disponíveis"), unsafe_allow_html=True)
                with k2:
                    st.markdown(kpi(P["pessoas"], "#ECFDF5", "#0E9F6E", f"{vagas_total:,}".replace(",", "."), "Vagas ofertadas<br>no edital"), unsafe_allow_html=True)
                with k3:
                    st.markdown(kpi(P["dinheiro"], "#F0FDF4", "#16A34A", maior_txt, "Maior auxílio<br>mensal", True), unsafe_allow_html=True)

                st.markdown('<p class="sec-title">Programas disponíveis neste campus</p>', unsafe_allow_html=True)
                if bloco.empty:
                    st.markdown('<div class="empty">Sem registro de apoio para este campus no ano selecionado.</div>', unsafe_allow_html=True)
                else:
                    ordenado = bloco.sort_values("Valor destinado ao beneficiário (R$)", ascending=False)
                    st.markdown("".join(acordeao(l) for _, l in ordenado.head(3).iterrows()), unsafe_allow_html=True)
                    if len(bloco) > 3:
                        st.caption(f"+ {len(bloco) - 3} programa(s) na aba **Programas disponíveis**.")

            with aba_progs:
                st.markdown('<div style="height:.5rem"></div>', unsafe_allow_html=True)
                if bloco.empty:
                    st.markdown('<div class="empty">Sem registro de apoio para este campus no ano selecionado.</div>', unsafe_allow_html=True)
                else:
                    st.markdown(
                        "".join(
                            acordeao(l)
                            for _, l in bloco.sort_values("Valor destinado ao beneficiário (R$)", ascending=False).iterrows()
                        ),
                        unsafe_allow_html=True,
                    )
                    links = bloco["Edital disponível em:"].dropna().unique()
                    if len(links):
                        st.caption(f"📄 Edital disponível em: {links[0]}")

            st.markdown(
                f'<div class="aviso"><span style="flex:0 0 18px;">{svg(P["info"], 18, ACCENT)}</span><div>'
                '<p class="aviso-t">Os valores e critérios podem variar conforme edital vigente.</p>'
                '<p class="aviso-s">Sempre consulte o edital mais recente no site da PRAPE/UFPB.</p>'
                "</div></div>",
                unsafe_allow_html=True,
            )
