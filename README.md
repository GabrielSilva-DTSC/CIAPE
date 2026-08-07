# CIAPE — Centralização das Informações de Apoio e Permanência Estudantil

**Autor:** Everton Gabriel Silva de Almeida
**Contato:** everton.gabriel@academico.ufpb.br
**Disciplina:** Análise de Dados — Ciência de Dados para Negócios
**Instituição:** Universidade Federal da Paraíba (UFPB) — Centro de Ciências Sociais Aplicadas

---

## Sobre o projeto

O **CIAPE** nasce da constatação de que parte significativa das dificuldades enfrentadas por estudantes em situação de vulnerabilidade social começa no acesso à informação — inclusive nos processos de ingresso ao ensino superior público (SiSU, FIES). Ferramentas como o "Meu SiSU" (ICMC/USP São Carlos) já ajudam vestibulandos a planejar suas escolhas com base em notas de corte, mas nenhuma centraliza as informações sobre os programas de **Apoio e Permanência Estudantil (APE)** — dado hoje fragmentado entre as esferas Federal e Estaduais.

O projeto atua sobre essa fragmentação por meio de um **MVP**: extrair, padronizar e disponibilizar de forma unificada as informações de APE, começando pela UFPB, para orientar a tomada de decisão de vestibulandos em vulnerabilidade social.

## Objetivos

### Objetivo geral
Desenvolver um Produto Mínimo Viável (MVP), baseado na UFPB e com potencial de escalabilidade nacional, para centralizar e democratizar o acesso às informações sobre políticas de APE das Instituições de Ensino Superior (IES) públicas.

### Objetivos específicos
- Mapear e catalogar os editais de seleção unificada de apoio e permanência estudantil vigentes nos campi I, II, III e IV da UFPB (2025–2026).
- Estruturar, em conjunto com Inteligência Artificial, um padrão de leitura para extração de dados complexos contidos em editais oficiais.
- Padronizar nomenclaturas, requisitos, prazos e modalidades dos diferentes auxílios (moradia, alimentação, transporte etc.).
- Estruturar uma base de dados unificada que possibilite consulta rápida e mitigue a assimetria de informação.
- Desenvolver um mecanismo de visualização simples e dinâmico para apoiar a tomada de decisão dos vestibulandos.

## Público-alvo

Estudantes e vestibulandos em situação de vulnerabilidade social em todo o Brasil, que precisam considerar a existência (ou não) de programas de APE ao escolher onde estudar — sejam eles de outro estado, sem rede de apoio local, ou residentes locais com dificuldade de deslocamento/alimentação.

## Validação de escala (Censo da Educação Superior — INEP 2024)

Antes de aprofundar o MVP, o projeto consultou os microdados do Censo da Educação Superior para dimensionar o potencial de expansão:

- **2.561** IES no Brasil.
- **317** são públicas.
- **261** pertencem às esferas administrativas Federal ou Estadual.

Essa validação está documentada em `notebooks/analise_censo_edu_sup.ipynb`.

## Estrutura do repositório

```
PROJETO-CIAPE/
├── app/
│   ├── app.py                       # Dashboard interativo (Streamlit)
│   └── dados_app/                   # Bases tratadas consumidas pelo app
│       ├── df_mvp.csv
│       └── df_editais.csv
├── data/
│   ├── data_base_CIAPE_mvp - Página1.csv     # Base curada do MVP (UFPB)
│   └── fonte_dos_dados - origem_editais.csv  # Tabela fonte / rastreabilidade dos editais
├── docs/
│   ├── apresentação projeto CIAPE.pdf
│   └── ANEXOS/
├── notebooks/
│   └── analise_censo_edu_sup.ipynb  # Leitura do Censo INEP + tratamento e análise da base do MVP
├── src/
│   └── external/
│       ├── DADOS BRUTOS - editais/           # PDFs originais dos editais UFPB (2025-2026, campi I-IV)
│       └── microdados_censo_da_educacao_superior_2024/
│           ├── Anexos/                       # Dicionário de dados e questionários do Censo
│           ├── dados/                        # Microdados brutos (CSV, INEP)
│           └── leia-me/                      # Documentação oficial do INEP
├── Uso_i.a/
│   └── outputs/                     # Registro do uso documentado de IA na extração dos editais
├── .gitignore
├── requirements.txt
└── README.md
```

## Fontes de dados

| Fonte | Descrição | Link |
|---|---|---|
| Censo da Educação Superior (INEP, 2024) | Microdados usados para dimensionar o potencial de escala do projeto | [Página oficial](https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/censo-da-educacao-superior) / [Download direto](https://download.inep.gov.br/microdados/microdados_censo_da_educacao_superior_2024.zip) |
| Editais de Apoio e Permanência Estudantil da UFPB | Editais unificados 2025 e 2026 dos campi I, II, III e IV (PRAPE) | Ver `src/external/DADOS BRUTOS - editais/` |

## Metodologia / pipeline de dados

O tratamento dos dados, documentado em `notebooks/analise_censo_edu_sup.ipynb`, segue as etapas:

1. **Leitura e diagnóstico** dos microdados do Censo (INEP) para validar a escala do problema.
2. **Leitura e limpeza** da base própria do MVP (`data_base_CIAPE_mvp`) e da tabela fonte dos editais (`fonte_dos_dados`), com verificação de tipos, nulos e duplicados.
3. **Extração assistida por IA** (Claude Code e Gemini) para leitura dos editais em PDF, com construção de um dicionário de tradução controlado entre a nomenclatura local dos auxílios e a categoria funcional padronizada (PNAES). O uso da IA está documentado na pasta `Uso_i.a/outputs`.
4. **Mineração de texto** para extrair o número do campus (numeral romano) a partir do nome, casado com o código oficial de campus da tabela fonte.
5. **Construção do identificador hierárquico** `ID_completo` (Estado-IES-Campus).
6. **Merge validado** entre a base do MVP e a tabela fonte dos editais, trazendo latitude, longitude e metadados (ano, link do edital).
7. **Definição das perguntas analíticas** do MVP, com os respectivos agrupamentos (`groupby`) por Campus, IES e Estado.

### Perguntas analíticas do MVP

O notebook estrutura o `groupby` para 11 perguntas de negócio, entre elas: eixos PNAES (moradia/transporte/alimentação) oferecidos por campus e ano; vagas por eixo e público-alvo; campi com alojamento/Restaurante Universitário e respectivas vagas no edital mais recente; valor médio/mediano do auxílio financeiro por campus, IES e estado; prazo médio de inscrição; e origem/responsável por cada edital. A lista completa está na seção "Perguntas Analíticas para Agrupamento" do notebook.

## Tecnologias e requisitos

- Python 3.11+
- pandas, numpy
- Jupyter Lab (análise exploratória)
- Streamlit (dashboard interativo)
- openpyxl (leitura do dicionário de dados em planilha)

Instale as dependências com:

```bash
pip install -r requirements.txt
```

## Como rodar o projeto

```bash
# 1. Clonar o repositório
git clone <url-do-repositorio>
cd PROJETO-CIAPE

# 2. Criar e ativar o ambiente virtual
python -m venv .venv
source .venv/bin/activate      # Linux/Mac
.venv\Scripts\activate         # Windows

# 3. Instalar as dependências
pip install -r requirements.txt

# 4. Rodar o notebook de análise
jupyter lab notebooks/analise_censo_edu_sup.ipynb

# 5. Rodar o dashboard (quando disponível)
streamlit run app/app.py
```

> **Nota:** os caminhos de leitura de dados no notebook atual estão hardcoded como absolutos locais. Ajuste-os para caminhos relativos (`../data/...`) antes de rodar em outra máquina.

## Status atual e próximos passos

- [x] Validação de escala com dados do Censo da Educação Superior (INEP).
- [x] Leitura, limpeza e tipagem da base própria do MVP e da tabela fonte dos editais.
- [x] Construção do identificador único hierárquico (`ID_completo`) e merge validado entre as bases.
- [x] Definição das 11 perguntas analíticas e implementação dos agrupamentos.
- [ ] Exibição, interpretação e visualização dos resultados das perguntas analíticas.
- [ ] Construção do **dashboard interativo em Streamlit**, com mapa (latitude/longitude por campus) como interface principal.
- [ ] Expansão da base para outras IES públicas além da UFPB.

## Limitações conhecidas

- A legenda de `eixo_pnaes` (Moradia/Transporte/Alimentação) apresenta inconsistências pontuais frente aos dados reais e deve ser validada contra os editais originais antes de uso em produção.
- `publico_alvo` está constante no MVP atual (apenas UFPB) — a segmentação por público só ganha valor real quando outras IES/editais entrarem na base.
- A identificação de Alojamento/Restaurante Universitário depende de correspondência textual em `modalidade_apoio`, o que é frágil a novas variações de nomenclatura em editais futuros.

## Uso de Inteligência Artificial

Parte da extração e estruturação de dados dos editais (em formato PDF, com nomenclaturas heterogêneas entre campi) foi realizada em conjunto com ferramentas de IA (Claude Code e Gemini), com validação humana sobre um edital-piloto antes da aplicação em escala. O registro documentado desse uso está disponível em `Uso_i.a/outputs`.

## Licença

_A definir._

## Contato

Dúvidas ou sugestões: **everton.gabriel@academico.ufpb.br**
