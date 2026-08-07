# Protocolo Metodológico para Extração e Padronização de Dados de
# Assistência Estudantil em Editais de Instituições de Ensino Superior
# Públicas do Brasil

### Projeto CIAPE — versão nacional generalizada (substitui e amplia o escopo do documento anterior, restrito à UFPB/PRAPE)

---

## Resumo

Instituições de Ensino Superior (IES) públicas brasileiras — universidades federais, institutos
federais, universidades estaduais e municipais — publicam periodicamente editais de seleção
para auxílios de assistência estudantil. Cada rede opera sob marco legal próprio, com
nomenclatura, formato de documento e estrutura administrativa distintos. Este protocolo
generaliza o método desenvolvido e testado sobre editais PRAPE/COAPE da UFPB (4 campi,
múltiplos ciclos anuais) em um procedimento de análise documental estruturada,
institution-agnostic, replicável e auditável, aplicável a qualquer IES pública do país,
independentemente do marco legal ou da nomenclatura local.

---

## 1. Introdução e Escopo

A rede de ensino superior público brasileiro é heterogênea:

| Esfera administrativa | Marco legal típico | Exemplo de nomenclatura observada |
|---|---|---|
| Federal — Universidades | Lei nº 14.914/2024 (PNAES), resoluções internas de CONSUNI | PRAPE, PROAE, COSEAS |
| Federal — Institutos Federais | Mesma lei do PNAES, mas gestão via CAE/NAE | Auxílio Permanência, Bolsa Alimentação |
| Estadual | Legislação estadual e resoluções de CONSU/CONSEPE próprias — **não há marco nacional equivalente ao PNAES** | Bolsa Trabalho, Bolsa Moradia, Programa Moradia Estudantil |
| Municipal | Legislação municipal própria, quando existente | variável, sem padrão consolidado |

Essa diversidade significa que **um protocolo de extração não pode assumir uma nomenclatura fixa
herdada da legislação federal**. Ele precisa operar sobre o **tipo funcional do benefício**
(o que ele custeia, e não como a instituição o rotula), preservando ao mesmo tempo o nome e o
marco legal originais para fins de rastreabilidade.

Este documento define esse protocolo.

---

## 2. Objetivos

**Objetivo geral:** estabelecer um procedimento sistemático e reprodutível para converter o
texto não estruturado de editais de assistência estudantil em dados estruturados, comparáveis e
auditáveis, aplicável a qualquer IES pública brasileira.

**Objetivos específicos:**
1. Padronizar uma taxonomia funcional de benefícios, desacoplada do marco legal de origem.
2. Garantir validação cruzada obrigatória entre o dado extraído e o total declarado no documento-fonte.
3. Garantir rastreabilidade plena de cada registro até o PDF de origem.
4. Preservar séries históricas por unidade institucional, sem sobreposição ou perda de edições anteriores.
5. Permitir a incorporação de novas instituições sem retrabalho do schema já existente.

---

## 3. Delineamento Metodológico

**3.1 Abordagem.** Análise documental estruturada (*structured document analysis*), próxima à
tradição de análise de conteúdo categorial (esquema de codificação fechado, aplicado de forma
sistemática a um corpus de documentos oficiais), combinada com validação aritmética
(*arithmetic cross-validation*) contra os totais declarados no próprio documento.

**3.2 Unidade de análise.** Cada linha de dado representa **1 modalidade de auxílio, ofertada
por 1 unidade institucional (campus/polo/unidade), em 1 processo seletivo (edital) específico**.
Essa é a menor unidade que preserva granularidade suficiente para reconstrução de qualquer
agregado (por eixo, por unidade, por edital, por ano) sem reprocessar o documento-fonte.

**3.3 Corpus.** Documentos oficiais em PDF publicados pelos setores responsáveis (pró-reitorias,
coordenações de assistência estudantil, CAEs, NAEs, fundações de amparo ao estudante).

**3.4 Instrumento de coleta.** Schema de dados padronizado e institution-agnostic (Anexo A),
preenchido a partir da leitura integral do documento — nunca de resumos ou notícias
secundárias sobre o edital.

**3.5 Critério de reprodutibilidade.** Toda decisão de codificação (agregar/desagregar,
mapear para qual categoria, como tratar retificações) segue regras objetivas e documentadas
(Seções 6 e 7), de forma que analistas diferentes cheguem ao mesmo resultado a partir do mesmo
documento-fonte — pré-requisito básico de um protocolo científico replicável.

---

## 4. Etapa 0 (pré-requisito) — Identificação do marco institucional local

Antes de extrair qualquer edital de uma instituição **ainda não presente na base**, executar:

1. Identificar a esfera administrativa (federal / estadual / municipal) e o marco legal que
   rege a assistência estudantil ali (PNAES/Lei 14.914/2024, ou legislação/resolução própria).
2. Mapear a hierarquia institucional local (campus, polo, unidade, pólo avançado) para o campo
   genérico `unidade_institucional`.
3. Construir um dicionário de tradução: termo local do auxílio → categoria funcional
   padronizada (Seção 6). Sem esse dicionário prévio, a extração tende a criar categorias
   ad hoc incompatíveis com o restante da base.
4. Validar o dicionário com um edital-piloto antes de escalar para o histórico completo da
   instituição (ver Seção 10).

Só depois desta etapa a instituição está pronta para o protocolo de extração propriamente dito
(Seção 5).

---

## 5. Protocolo de Extração (passo a passo)

| # | Etapa | Regra objetiva |
|---|---|---|
| 1 | Leitura estrutural do documento | Localizar as seções equivalentes a: objeto/público-alvo, cronograma, **quadro de vagas**, critérios de elegibilidade, valores, regras de acumulação, metodologia de avaliação socioeconômica |
| 2 | Localização do quadro de vagas | Extrair a tabela/bloco que declara nº de vagas por auxílio; anotar à parte o "Total de vagas" declarado — essa é a âncora de validação da etapa 8 |
| 3 | Mapeamento taxonômico | Classificar cada modalidade observada em uma categoria da taxonomia funcional (Seção 6); nunca criar categoria nova sem registrar a extensão (Seção 6.1) |
| 4 | Granularidade | 1 linha por combinação unidade + edital + modalidade (nunca agregar faixas/variantes distintas numa só linha) |
| 5 | Agregação vs. desagregação de subgrupos | Regra objetiva (Seção 7): se valor/nome difere entre subgrupos → linhas separadas; se é idêntico → linha única, detalhamento em texto |
| 6 | Valores monetários | `valor_recorrente_brl` = valor mensal ou periódico recorrente; benefícios em espécie (acesso a refeição, uso de infraestrutura) = texto `"Serviço Direto"`; parcelas únicas registradas separadamente, nunca somadas ao valor recorrente |
| 7 | Critérios de elegibilidade | Registrar apenas os critérios **adicionais e específicos daquela modalidade**; critérios gerais (válidos para todo o edital) ficam documentados uma única vez na metodologia, não repetidos linha a linha |
| 8 | Validação cruzada obrigatória | Somar as vagas das linhas lançadas para aquela unidade+edital e conferir contra o total declarado no documento (etapa 2). Divergência bloqueia o lançamento até ser resolvida |
| 9 | Checagem de duplicidade / retificação | Ver protocolo de versionamento (Seção 8) antes de inserir |
| 10 | Numeração sequencial e fonte | ID contínuo (nunca reiniciar); campo de fonte no formato `"PDF [Órgão/Setor] [Nº]/[Ano] ([status de retificação, se houver])"` |
| 11 | Atualização de agregados | Tabelas-resumo recalculadas por fórmula (nunca valor fixo digitado), com intervalo de referência sempre expandido para cobrir os novos registros |
| 12 | Documentação da variação inter-edital | Para toda nova edição de uma unidade já presente na base: registrar explicitamente vagas/valores antes→depois e qualquer modalidade que apareceu/desapareceu, sinalizando incerteza quando aplicável |

---

## 6. Taxonomia Funcional (Vocabulário Controlado, Extensível)

A taxonomia é **funcional** (o que o benefício custeia), não legal (como a instituição o
nomeia). Isso é o que permite comparar uma "Bolsa Moradia" estadual com o "Auxílio Moradia"
federal como o mesmo tipo de dado.

| Categoria funcional (`categoria_beneficio`) | Cobre tipicamente | Exemplos de nomes observados em diferentes redes |
|---|---|---|
| Alimentação | Acesso a refeições ou auxílio financeiro equivalente | Restaurante Universitário, Auxílio Alimentação, Bolsa Alimentação |
| Moradia | Auxílio financeiro para custeio de moradia | Auxílio Moradia, Bolsa Moradia |
| Moradia — Infraestrutura | Vaga física em alojamento/residência mantida pela instituição | Residência Universitária, Casa do Estudante, Moradia Estudantil |
| Transporte | Custeio de deslocamento residência–instituição | Auxílio Transporte, Bolsa Transporte, Passe Estudantil |
| Creche/Educação Infantil | Apoio a estudantes com filhos pequenos | Auxílio Pré-escolar, Bolsa Creche |
| Apoio Pedagógico/Acadêmico | Materiais, equipamentos, conectividade para estudo | Auxílio Inclusão Digital, Bolsa Material Didático |
| Apoio Financeiro Geral/Emergencial | Auxílio de manutenção geral, sem finalidade específica | Bolsa Permanência, Auxílio Emergencial |
| Saúde/Psicossocial | Apoio a saúde física ou mental do estudante | Auxílio Saúde, Bolsa Atenção Psicossocial |
| Outros (a especificar) | Categoria de extensão — usada quando nenhuma das acima se aplica | — |

### 6.1 Regra de extensão da taxonomia

Se um auxílio observado não se encaixa em nenhuma categoria existente, ele **pode** gerar uma
nova categoria — mas isso é uma decisão registrada, não silenciosa: documentar no log de
metodologia (a) o nome original do auxílio, (b) a instituição/edital de origem, (c) a
justificativa para não se encaixar nas categorias existentes, (d) a data da extensão. Isso
evita proliferação descontrolada de categorias equivalentes com nomes diferentes.

---

## 7. Regra de Decisão: Agregar ou Desagregar Subgrupos

Aplicável sempre que um auxílio for oferecido em variantes (por gênero, unidade física, faixa
de renda, faixa de distância etc.):

> **Se o valor monetário OU o nome/rótulo institucional da modalidade difere entre as
> variantes → uma linha por variante.**
> **Se o valor é idêntico independentemente da variante → uma linha única**, somando as vagas
> das variantes, com o detalhamento (ex. "15 vagas masculinas + 10 femininas") registrado em
> texto no campo de critérios — nunca em linhas separadas artificiais.

Esse teste é objetivo e reprodutível: qualquer analista aplicando a mesma regra ao mesmo
documento chega à mesma estrutura de linhas.

---

## 8. Protocolo de Versionamento: Retificações e Séries Temporais

1. **Antes de inserir**, verificar se a combinação `unidade_institucional + número do edital`
   já existe na base.
2. Se existir uma versão de retificação **anterior do mesmo número de edital**, a nova versão
   **substitui integralmente** as linhas da anterior — retificações são a versão autoritativa
   mais recente do mesmo processo seletivo, não um registro adicional.
3. Se for um **número de edital novo** (nova edição/ciclo da mesma unidade), **nunca sobrescrever
   ou remover** as linhas do edital anterior — cada edital é um ponto distinto de uma série
   temporal, e a preservação dessa série é o valor central do projeto.
4. Editais retificados que alteram apenas texto (sem mudança em vagas/valores) ainda devem
   atualizar o campo de fonte para refletir a versão vigente, mesmo sem alteração numérica.

---

## 9. Validação e Controle de Qualidade

| Tipo de validação | Descrição | Ação se falhar |
|---|---|---|
| **Interna (aritmética)** | Soma das vagas lançadas = total declarado no edital | Bloquear lançamento; reler o quadro de vagas |
| **Temporal (plausibilidade)** | Variação de vagas/valores entre edições da mesma unidade dentro de faixa plausível | Sinalizar como observação, não bloquear — mudanças reais de política (ex. expansão orçamentária) são esperadas, mas devem ser explicitamente registradas (Seção 5, etapa 12) |
| **Estrutural (schema)** | Todo campo obrigatório do instrumento (Anexo A) preenchido | Bloquear lançamento até completude |
| **Rastreabilidade** | Campo de fonte aponta exatamente para o documento e status de retificação | Obrigatório em 100% dos registros |
| **Auditoria por amostragem** | Recomenda-se reconferência periódica de uma amostra de registros já lançados contra o PDF original, especialmente ao incorporar uma nova instituição | Ajustar dicionário de tradução (Seção 4) se erros sistemáticos forem encontrados |

---

## 10. Protocolo de Adaptação Institucional (Onboarding de Nova IES)

| Etapa | Ação |
|---|---|
| A | Executar a Etapa 0 (Seção 4): identificar marco legal, esfera administrativa e hierarquia institucional |
| B | Construir o dicionário local de tradução (termo institucional → categoria funcional, Seção 6) |
| C | Selecionar 1 edital-piloto e aplicar o protocolo completo (Seção 5) manualmente |
| D | Validar o piloto: a soma bate com o total declarado? A taxonomia cobriu todos os auxílios sem forçar categorias? |
| E | Somente após validação do piloto, escalar para o histórico completo da instituição |
| F | Registrar qualquer extensão de taxonomia feita durante o onboarding (Seção 6.1) |

---

## 11. Limitações e Ameaças à Validade

- **Erros no próprio documento-fonte.** Editais podem conter inconsistências internas (ex. soma
  do quadro de vagas não bate com o total declarado por erro de digitação da própria
  instituição). O protocolo detecta a divergência (Seção 9), mas não resolve autoritativamente
  qual número está certo — isso exige contato com a instituição emissora quando relevante.
- **Retificações fora de ordem.** Documentos podem ser recebidos fora da ordem cronológica de
  publicação; o protocolo assume que a data/numeração de retificação declarada no próprio
  documento é a fonte de verdade sobre precedência.
- **Manutenção contínua do dicionário.** A nomenclatura institucional evolui; o dicionário de
  tradução (Seção 6) é um artefato vivo, não uma tabela estática — requer revisão periódica.
- **Ausência ≠ descontinuação.** A ausência de uma modalidade em uma nova edição pode refletir
  descontinuação real da política **ou** lacuna de extração de uma edição anterior. O protocolo
  exige sinalização explícita da incerteza (Seção 5, etapa 12) em vez de inferência silenciosa.
- **Extração humana/assistida por IA.** O processo descrito é semi-automatizado (leitura e
  codificação assistidas por modelo de linguagem, com regras determinísticas); recomenda-se
  amostragem de auditoria (Seção 9) como controle de qualidade contínuo, especialmente ao
  escalar para múltiplas instituições simultaneamente.

---

## 12. Aplicabilidade e Escalabilidade Nacional

Como a taxonomia (Seção 6) é funcional e não depende do marco legal de origem, o mesmo schema
cobre simultaneamente:
- Universidades federais e institutos federais (PNAES, Lei nº 14.914/2024);
- Universidades estaduais e municipais, sob suas legislações próprias;
- Diferentes formatos de documento e estrutura administrativa, desde que o protocolo de
  onboarding (Seção 10) seja seguido antes da extração em escala.

Isso viabiliza usos de pesquisa que exigem comparabilidade nacional: séries históricas de
oferta de vagas por tipo de benefício, estudos comparativos entre redes federal/estadual, e
acompanhamento de política pública de permanência estudantil ao longo do tempo — sem exigir
que cada nova instituição incorporada redefina o schema do zero.

---

## 13. Dados Abertos e Considerações Éticas

Os documentos-fonte (editais) são atos administrativos públicos, e o schema captura **dados de
política institucional agregados** (vagas, valores, critérios, cronogramas) — não dados
pessoais ou identificáveis de estudantes individuais. Não há, portanto, tratamento de dados
sensíveis no escopo deste protocolo. Caso um projeto derivado incorpore dados individuais de
beneficiários (fora do escopo aqui descrito), esse tratamento passaria a exigir salvaguardas
próprias sob a Lei Geral de Proteção de Dados (Lei nº 13.709/2018), o que não se aplica aos
dados de vagas/editais tratados por este protocolo.

---

## 14. Checklist Operacional Resumido

- [ ] Marco legal e hierarquia institucional identificados (Seção 4)
- [ ] Dicionário de tradução local construído e validado em piloto (Seções 4 e 10)
- [ ] Quadro de vagas localizado e total declarado anotado (Seção 5, etapa 2)
- [ ] Cada modalidade mapeada para categoria funcional, sem forçar categorias existentes (Seção 6)
- [ ] Regra de agregação/desagregação aplicada objetivamente (Seção 7)
- [ ] Soma de vagas lançadas = total declarado (Seção 9)
- [ ] Duplicidade/retificação verificada antes da inserção (Seção 8)
- [ ] Fonte rastreável registrada em 100% das linhas
- [ ] Agregados recalculados por fórmula, intervalo expandido
- [ ] Variação inter-edital documentada explicitamente

---

## Anexo A — Schema de Dados Padronizado (institution-agnostic)

| Campo | Tipo | Descrição | Exemplo |
|---|---|---|---|
| `registro_id` | inteiro sequencial | Identificador único e contínuo do registro | 59 |
| `ies_nome` | texto | Nome da instituição | Universidade Federal da Paraíba |
| `esfera_administrativa` | categórico | Federal / Estadual / Municipal | Federal |
| `unidade_institucional` | texto | Campus/polo/unidade | Campus III – Bananeiras |
| `edital_numero` | texto | Número/ano/status de retificação | 10/2026 (Retificado 1) |
| `ano_vigencia` | inteiro | Ano do ciclo seletivo | 2026 |
| `programa_institucional` | texto | Nome do programa que rege o benefício | PNAES |
| `base_legal` | texto | Norma que fundamenta o programa | Lei nº 14.914/2024 |
| `fonte_dado` | texto | Documento de origem, com status de retificação | PDF Edital PRAPE 10/2026 (Retificado 1) |
| `categoria_beneficio` | categórico (Seção 6) | Categoria funcional do auxílio | Moradia |
| `modalidade_apoio` | texto | Modalidade específica dentro da categoria | Vaga Física - Infraestrutura (Residência Universitária) |
| `valor_recorrente_brl` | número ou "Serviço Direto" | Valor mensal/periódico recorrente | 500 |
| `valor_parcela_unica_brl` | número (opcional) | Valor de parcela única, se houver | 500 |
| `infraestrutura_disponivel` | Sim/Não | Se o benefício envolve uso de infraestrutura física | Sim |
| `total_vagas_ofertadas` | inteiro | Vagas daquela linha | 8 |
| `prazo_inscricao_dias` | inteiro | Duração do período de inscrição (contagem inclusiva) | 19 |
| `criterios_elegibilidade` | texto | Critérios adicionais específicos da modalidade | Núcleo familiar fora do perímetro urbano... |

---

## Anexo B — Log de Extensão da Taxonomia (modelo)

| Data | Categoria nova proposta | Instituição/edital de origem | Justificativa | Decisão |
|---|---|---|---|---|
| _(preencher a cada extensão)_ | | | | |

---

## Referências

- BRASIL. **Lei nº 14.914, de 2024.** Institui a Política Nacional de Assistência Estudantil
  (PNAES).
- Resoluções internas de CONSUNI/CONSU/CONSEPE de cada instituição (marco legal local,
  variável por rede — a serem mapeadas individualmente no protocolo de onboarding, Seção 10).
- Tradição metodológica de análise de conteúdo categorial aplicada a documentos oficiais
  (esquema de codificação fechado e sistemático).
