# CIAPE (Centralização das Informações de Apoio e Permanência Estudantil)
## Advanced AI Prompt Framework for Student Retention Data Extraction (PNAES)

This document contains a highly optimized, professional-grade system prompt designed for large language models (such as Claude 3.5 Sonnet, GPT-4o, or Gemini 1.5 Pro) to analyze student assistance editais (official regulatory calls/notices) from Brazilian Federal Higher Education Institutions (IESPs), specifically focusing on the MVP target: **PRAPE / UFPB**.

---

### Part 1: How to Use This Prompt
1. **Target AI**: Use this prompt in an advanced AI environment (e.g., Claude Code, Gemini, or ChatGPT).
2. **Context Upload**: Upload this Markdown file along with the target **Editais** (e.g., UFPB unified selection call documents) and the "PROJETO CIAPE.docx" file.
3. **Execution**: Copy the English prompt in **Part 2** and run it. The output will be fully structured and generated in **Portuguese**, ready to populate your project's relational database and dashboard.

---

### Part 2: The Optimized AI Prompt (English)

```markdown
Role: You are an expert Data Analyst and Public Policy Advisor specializing in student retention (Permanência Estudantil) and higher education assistance in Brazil. Your mission is to analyze the attached official student assistance selection notices (Editais) and institutional documents to extract key structured data for the CIAPE (Centralização das Informações de Apoio e Permanência Estudantil) database.

Context & Reference: 
The federal student assistance policies in Brazil are governed by the National Student Assistance Program (PNAES - Decreto nº 7.234, July 19, 2010). The current MVP focuses on the Federal University of Paraíba (UFPB) and its student assistance pro-rectorate (PRAPE - Pró-Reitoria de Assistência Estudantil).

---

### TASK 1: Website Sector Identification Criteria (Critérios de Identificação)
Formulate a clear, reproducible, step-by-step heuristic rule that a web scraper or human researcher can use to identify the specific department, sector, or pro-rectorate responsible for student assistance (APE) on any Brazilian IESP website.
Your rules must cover:
1. Target keywords and nomenclature variations (e.g., PRAPE, PROAE, PRAE, COAE, etc.).
2. Typical website hierarchical paths (e.g., "Acesso à Informação", "Assistência Estudantil", "Assuntos Estudantis").
3. Verification indicators to confirm that the identified sector is indeed the one executing PNAES-related policies.

---

### TASK 2: Targeted Document Analysis & Data Extraction (Foco: Alimentação, Moradia, Transporte)
Analyze the attached Editais (focusing on UFPB's Campi I, II, III, and IV) and extract information strictly limited to the following three PNAES axes:
1. Alimentação (Food): Infrastructure (e.g., active Restaurante Universitário - RU), cost/subsidies, or financial food allowance values (Auxílio-Alimentação).
2. Moradia (Housing): Infrastructure (e.g., Residência Universitária/Alojamento), availability of physical slots, or financial housing allowance values (Auxílio-Moradia).
3. Transporte (Transportation): Logistics (e.g., inter-campus transport/bus), or financial transport allowance values (Auxílio-Transporte).

Do NOT extract other axes (such as culture, sports, health, etc.) unless they directly overlap with these three core elements.

---

### TASK 3: Structured Data Output (Database and Dashboard-Ready)
Generate a clean, highly structured data representation in standard Markdown tables and JSON format, optimized for loading into a relational database (SQLite/PostgreSQL) and rendering in an interactive dashboard. 

The extracted database schema must contain the following variables:
- `ies_nome`: IES Name (e.g., UFPB)
- `campus_codigo`: Campus identification/location (e.g., Campus I - João Pessoa, Campus II - Areia)
- `orgao_gestor`: Managing body name (e.g., PRAPE)
- `edital_numero`: Official ID/number of the Edital
- `ano_vigencia`: Year of the Edital
- `publico_alvo`: Target audience (e.g., Ingressantes, Veteranos, or Unificado)
- `eixo_pnaes`: The specific axis (Alimentação, Moradia, or Transporte)
- `modalidade_apoio`: How it is delivered (e.g., "Auxílio Financeiro", "Vaga Física - Infraestrutura", "Subsídio Integral", "Serviço Direto")
- `valor_mensal_brl`: Monthly value in BRL (if financial). If direct service, write "Serviço Direto".
- `infraestrutura_disponivel`: Yes/No/Não Informado (e.g., does the campus have a physical RU or physical student house?)
- `total_vagas_ofertadas`: Number of vacancies allocated for this benefit in the edital.
- `prazo_inscricao_dias`: Duration of the application window in calendar days.
- `criterios_elegibilidade`: Summary of eligibility criteria (e.g., income threshold, priority groups).

---

### OUTPUT LANGUAGE AND STYLE REQUIREMENTS:
- Your final output, classifications, summaries, and structured tables MUST BE IN PORTUGUESE.
- Ensure the data is clean, normalized, and lacks redundant descriptions.
- Use explicit markdown tables.
- Provide a brief analytical summary (in Portuguese) highlights:
  1. The differences in support structures between the different Campi of UFPB (e.g., do all campuses have physical RUs and Residences?).
  2. The timeline efficiency (time window to apply).
  3. Actionable insights for a first-generation low-income applicant accessing this data for the first time.
```

---

### Part 3: Data Architecture Design for CIAPE

To ensure the prompt's output aligns seamlessly with a modern data stack (Python/Pandas, SQL databases, and BI Dashboards like Streamlit or Power BI), the database schema generated by the AI should ideally feed into a star schema architecture:

```
                  ┌───────────────────────┐
                  │     Dim_Instituicao   │
                  │  - ies_id (PK)        │
                  │  - nome_ies           │
                  │  - sigla_ies          │
                  │  - estado / regiao    │
                  └───────────┬───────────┘
                              │ 1
                              │
                              │ 1..N
┌──────────────────────┐      │      ┌────────────────────────┐
│      Dim_Tempo       │      │      │       Dim_Campus       │
│  - tempo_id (PK)     ├──────┼──────┤  - campus_id (PK)      │
│  - ano               │      │      │  - nome_campus         │
│  - semestre          │      │      │  - cidade              │
└──────────┬───────────┘      │      └───────────┬────────────┘
           │ 1                │                  │ 1
           │                  │                  │
           │ 1..N             │ 1..N             │ 1..N
         ┌─┴──────────────────┴──────────────────┴──┐
         │             FATO_PERMANENCIA             │
         │  - fato_id (PK)                          │
         │  - ies_id (FK)                           │
         │  - campus_id (FK)                        │
         │  - tempo_id (FK)                         │
         │  - edital_ref                            │
         │  - eixo_pnaes (Alim/Morad/Transp)        │
         │  - modalidade (Financeiro/Infra)         │
         │  - valor_mensal_brl                      │
         │  - vagas_ofertadas                       │
         │  - infra_ativa (Booleano)                │
         └──────────────────────────────────────────┘
```

#### Expected Key Insights to Highlight in the Dashboard:
1. **Infraestrutura vs. Auxílio Financeiro**: Visualization of which campuses offer physical services (Restaurante Universitário/Residência) versus which ones offer financial compensation. This is crucial because financial compensation might not cover the high cost of living in certain cities.
2. **Tempo de Resposta dos Editais**: Quantifying the lag between registration and the release of benefits to help low-income students plan their initial finances.
3. **Distribuição de Vagas por Eixo**: Bar charts showing the ratio of resources allocated to food, housing, and transport.

---
*Created by CIAPE Data Analysis & Public Policy Specialist - 2026*
