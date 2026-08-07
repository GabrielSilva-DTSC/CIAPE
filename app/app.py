"""
CIAPE — Painel de Apoio e Permanência Estudantil (UFPB)
Dashboard de mapa: ajuda vestibulandos a identificar qual campus da UFPB
oferece o melhor suporte de APE (moradia, alimentação, transporte, creche)
para o seu perfil de necessidade.

Rodar com: streamlit run app.py
"""

import pandas as pd
import pydeck as pdk
import streamlit as st

DATA_DIR = "dados_app"

# ---------------------------------------------------------------------------
# Coordenadas de referência dos campi (fallback caso não venham na base)
# ---------------------------------------------------------------------------
CAMPI_COORDS = {
    "Campus I - João Pessoa e Santa Rita": (-7.137594, -34.846927),
    "Campus II - Areia": (-6.969892, -35.715877),
    "Campus III - Bananeiras": (-6.751521, -35.648475),
    "Campus IV - Litoral Norte (Mamanguape e Rio Tinto)": (-6.806485, -35.075725),
}

CATEGORIA_MAP = {
    "🔎 Ver tudo": None,
    "🏠 Auxílio Aluguel (moradia fora do campus)": "Auxílio Aluguel",
    "🛏️ Residência universitária (vaga física)": "Residência (vaga física)",
    "🍽️ Alimentação (RU / auxílio alimentação)": "Alimentação",
    "🚌 Transporte": "Transporte",
    "👶 Apoio à criança (creche/pré-escolar)": "Apoio à Criança (Creche)",
}


def categorizar(tipo_apoio: str) -> str:
    """
    Reclassifica cada linha de 'Tipo de Apoio' em uma categoria funcional,
    usando o vocabulário controlado definido em Sobre_os_Dados_CIAPE.xlsx
    (aba 'vocabulario_controlado').

    Feito via texto (e não via coluna 'eixo_pnaes') porque a base atual tem
    algumas inconsistências pontuais nessa coluna (ex.: linhas de Restaurante
    Universitário marcadas como eixo 'Transporte' em vez de 'Alimentação').
    Isso já era um ponto de atenção registrado no notebook original.
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
    if "moradia" in t or "auxílio 1" in t or "auxilio 1" in t:
        return "Auxílio Aluguel"
    return "Outros"


@st.cache_data
def carregar_dados() -> pd.DataFrame:
    df = pd.read_csv(f"{DATA_DIR}/df_mvp.csv")

    # Corrige separador de milhar quebrado em lat/long (ex.: -7137594 -> -7.137594)
    df["loc_latitude"] = df["loc_latitude"] / 1_000_000
    df["loc_longitute"] = df["loc_longitute"] / 1_000_000

    # Preenche/valida coordenadas com o dicionário de referência
    for campus, (lat, lon) in CAMPI_COORDS.items():
        mask = df["Nome do Campus"] == campus
        df.loc[mask & df["loc_latitude"].isna(), "loc_latitude"] = lat
        df.loc[mask & df["loc_longitute"].isna(), "loc_longitute"] = lon

    df["Ano"] = pd.to_datetime(df["Ano de Públicação"]).dt.year
    df["Categoria"] = df["Tipo de Apoio"].apply(categorizar)
    df["Cidade"] = df["Nome do Campus"].str.split(" - ").str[-1]

    return df


def montar_resumo_por_campus(df_filtrado: pd.DataFrame, todos_campi: list) -> pd.DataFrame:
    """Garante que os 4 campi apareçam no resumo, mesmo sem nenhuma linha no filtro atual."""
    if df_filtrado.empty:
        resumo = pd.DataFrame({"Nome do Campus": todos_campi})
        resumo["Nº de opções"] = 0
        resumo["Vagas totais"] = 0
        resumo["Valor médio (R$)"] = 0.0
        resumo["Prazo médio (dias)"] = pd.NA
    else:
        resumo = (
            df_filtrado.groupby("Nome do Campus")
            .agg(
                **{
                    "Nº de opções": ("Tipo de Apoio", "count"),
                    "Vagas totais": ("Número de vagas ofertadas", "sum"),
                    "Valor médio (R$)": ("Valor destinado ao beneficiário (R$)", "mean"),
                    "Prazo médio (dias)": ("Prazo de inscrição (em dias)", "mean"),
                }
            )
            .reindex(todos_campi, fill_value=0)
            .reset_index()
        )
    lat_lon = pd.DataFrame(
        [{"Nome do Campus": c, "lat": v[0], "lon": v[1]} for c, v in CAMPI_COORDS.items()]
    )
    resumo = resumo.merge(lat_lon, on="Nome do Campus", how="left")
    resumo["Cidade"] = resumo["Nome do Campus"].str.split(" - ").str[-1]
    return resumo


# ---------------------------------------------------------------------------
# Página
# ---------------------------------------------------------------------------
st.set_page_config(page_title="CIAPE — Apoio Estudantil UFPB", page_icon="🎓", layout="wide")

df = carregar_dados()
todos_campi = list(CAMPI_COORDS.keys())

st.title("🎓 CIAPE — Onde estudar na UFPB pensando na sua permanência")
st.caption(
    "Ferramenta de apoio à decisão para vestibulandos em situação de vulnerabilidade social: "
    "veja qual campus da UFPB oferece o melhor suporte de Apoio e Permanência Estudantil (APE) "
    "para o seu perfil — moradia, alimentação, transporte ou apoio à criança."
)

# ------------------------------- Sidebar -----------------------------------
st.sidebar.header("🔎 Filtros")

anos_disponiveis = sorted(df["Ano"].unique(), reverse=True)
ano_sel = st.sidebar.selectbox("Ano do edital", anos_disponiveis, index=0)

categoria_label = st.sidebar.radio("Qual apoio você está buscando?", list(CATEGORIA_MAP.keys()), index=0)
categoria_sel = CATEGORIA_MAP[categoria_label]

st.sidebar.markdown("---")
st.sidebar.caption(
    "**Exemplos de perfil (do projeto original):**\n\n"
    "👤 *Jucelino* — vem de outro estado, sem rede de apoio local → busque **🏠 Auxílio Aluguel** "
    "ou **🛏️ Residência universitária**.\n\n"
    "👤 *Gertrudes* — mora na Paraíba, mas não tem como pagar as refeições nem o deslocamento → "
    "busque **🍽️ Alimentação** ou **🚌 Transporte**."
)

# ------------------------------- Filtro -------------------------------------
df_filtrado = df[df["Ano"] == ano_sel].copy()
if categoria_sel is not None:
    df_filtrado = df_filtrado[df_filtrado["Categoria"] == categoria_sel]

resumo = montar_resumo_por_campus(df_filtrado, todos_campi)

# ------------------------------- KPIs ---------------------------------------
col1, col2, col3, col4 = st.columns(4)
col1.metric("Opções de apoio encontradas", int(resumo["Nº de opções"].sum()))
col2.metric("Vagas ofertadas (total)", int(resumo["Vagas totais"].sum()))
valor_medio_geral = df_filtrado["Valor destinado ao beneficiário (R$)"].mean()
col3.metric(
    "Valor médio do auxílio (R$)",
    f"{valor_medio_geral:,.0f}".replace(",", ".") if pd.notna(valor_medio_geral) else "—",
)
prazo_medio_geral = df_filtrado["Prazo de inscrição (em dias)"].mean()
col4.metric(
    "Prazo médio de inscrição (dias)",
    f"{prazo_medio_geral:,.0f}" if pd.notna(prazo_medio_geral) else "—",
)

# ------------------------------- Mapa ---------------------------------------
st.subheader(f"📍 Campi da UFPB — {categoria_label} · Edital {ano_sel}")

max_vagas = max(resumo["Vagas totais"].max(), 1)
resumo["raio"] = 1200 + (resumo["Vagas totais"] / max_vagas) * 6000
resumo["cor"] = resumo["Nº de opções"].apply(lambda n: [230, 57, 70, 200] if n > 0 else [150, 150, 150, 120])

camada = pdk.Layer(
    "ScatterplotLayer",
    data=resumo,
    get_position="[lon, lat]",
    get_radius="raio",
    get_fill_color="cor",
    pickable=True,
    stroked=True,
    get_line_color=[255, 255, 255],
    line_width_min_pixels=2,
)

visao = pdk.ViewState(latitude=-7.0, longitude=-35.4, zoom=7.4, pitch=0)

tooltip = {
    "html": (
        "<b>{Nome do Campus}</b><br/>"
        "Opções de apoio: {Nº de opções}<br/>"
        "Vagas totais: {Vagas totais}<br/>"
        "Valor médio: R$ {Valor médio (R$)}"
    ),
    "style": {"backgroundColor": "#1f2937", "color": "white"},
}

st.pydeck_chart(pdk.Deck(layers=[camada], initial_view_state=visao, tooltip=tooltip))
st.caption("🔴 Vermelho = há opções de apoio para o filtro selecionado · ⚪ Cinza = nenhuma opção encontrada nesse filtro.")

# ------------------------------- Ranking -------------------------------------
st.subheader("🏆 Ranking dos campi para esse filtro")
ranking = resumo.sort_values(["Vagas totais", "Valor médio (R$)"], ascending=False)[
    ["Nome do Campus", "Cidade", "Nº de opções", "Vagas totais", "Valor médio (R$)", "Prazo médio (dias)"]
].reset_index(drop=True)
ranking.index = ranking.index + 1
st.dataframe(
    ranking.style.format({"Valor médio (R$)": "{:,.0f}", "Prazo médio (dias)": "{:,.0f}"}),
    use_container_width=True,
)

# ------------------------------- Detalhe por campus ---------------------------
st.subheader("📋 Detalhamento por campus")
for campus in todos_campi:
    dados_campus = df_filtrado[df_filtrado["Nome do Campus"] == campus]
    with st.expander(f"{campus} — {len(dados_campus)} opção(ões) encontrada(s)"):
        if dados_campus.empty:
            st.info("Nenhuma opção de apoio encontrada para esse filtro neste campus/ano.")
        else:
            tabela = dados_campus[
                [
                    "Tipo de Apoio",
                    "Valor destinado ao beneficiário (R$)",
                    "Número de vagas ofertadas",
                    "Prazo de inscrição (em dias)",
                    "Resumo dos Críterios de Elegibilidade",
                ]
            ].sort_values("Valor destinado ao beneficiário (R$)", ascending=False)
            st.dataframe(tabela, use_container_width=True, hide_index=True)

            link = dados_campus["Edital disponível em:"].iloc[0]
            st.caption(f"📄 Edital disponível em: {link}")

# ------------------------------- Rodapé ---------------------------------------
st.markdown("---")
with st.expander("ℹ️ Sobre os dados e metodologia"):
    st.markdown(
        """
- **Fonte:** editais unificados de Apoio e Permanência Estudantil (PRAPE/UFPB), campi I, II, III e IV, 2025–2026.
- **Categorização:** a coluna `Categoria` usada nos filtros é derivada do texto de `Tipo de Apoio`,
  seguindo o vocabulário controlado do projeto (`Sobre_os_Dados_CIAPE.xlsx`), e não diretamente da coluna
  `eixo_pnaes` — que apresenta algumas inconsistências pontuais já registradas no notebook original.
- **Escopo do MVP:** dados exclusivos da UFPB. A estrutura foi desenhada para escalar a outras IES públicas.
- Projeto **CIAPE** — Everton Gabriel Silva de Almeida (everton.gabriel@academico.ufpb.br).
        """
    )
