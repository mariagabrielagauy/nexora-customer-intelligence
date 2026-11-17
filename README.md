# NEXORA | Customer Intelligence

**Independent portfolio case · Product Analytics · Customer Success · AI-assisted decision support**  
**Author:** Maria Gabriela Gauy

> A fictional B2B SaaS case exploring how product-usage and licensing signals can be transformed into an actionable view of adoption, account health and customer follow-up priorities.

## 60-second overview

Customer teams can miss early signs of declining adoption when they monitor accounts through disconnected indicators. NEXORA combines licensing, engagement, feature adoption and usage trends in one interactive portfolio view. A transparent health index helps prioritize human review, while an optional LLM assistant lets users explore the synthetic portfolio through natural-language questions.

**Live demo:** [Add your Streamlit app URL after deployment]  
**Repository:** [GitHub](https://github.com/mariagabrielagauy/nexora-customer-intelligence)

## What it demonstrates

- A portfolio dashboard with filters and executive KPIs.
- Product adoption and license activation analysis.
- Account-level exploration and prioritization.
- A transparent, explainable heuristic health index.
- Rule-based next-best-action suggestions for human review.
- Optional natural-language analysis through the OpenAI API.
- Data validation and a documented privacy/limitations approach.

## Business question

How might a B2B software team identify customers whose product adoption deserves attention, understand the usage signals behind that assessment, and organize follow-up work?

## Indicators in the fictional dataset

| Dimension | Example indicators |
|---|---|
| Customer portfolio | Account count, segment and industry |
| Licensing | Contracted seats and seats by module |
| Adoption | Active users, seat activation and module adoption |
| Engagement | Weekly sessions and active days per month |
| Usage trend | 30-day usage change and days since last login |
| Customer experience | Simulated support-ticket volume and sentiment indicator |

## Decision workflow

1. Filter the portfolio by segment and account-health category.
2. Review the overall distribution of adoption and usage.
3. Identify accounts with weaker health indicators.
4. Inspect the signals behind an individual account.
5. Use suggested actions as prompts for human investigation.
6. Ask the optional assistant to summarize patterns in the filtered synthetic data.

## Method and responsible use

The health index is a **weighted heuristic**, not a churn probability. Its components and thresholds are visible in the source code. Suggested actions are deterministic rules. The optional LLM assistant receives only a compact summary and a limited set of fictional records from the active filters; it does not contact customers or modify external systems.

All records are synthetic. The demo is not a validated production model. A real deployment would require authorized historical data, stakeholder-defined outcomes, temporal validation, model monitoring, privacy/security review and human oversight.

## Relationship to my experience

My professional experience in a B2B software environment exposed me to questions around software usage, customer indicators, product performance, user support and quality assurance. Those themes informed the **problem framing** of this independent case. The NEXORA implementation, fictional company, metrics and dataset were created separately; this project is not an Eliis product and does not reproduce proprietary systems, data or deliverables.

My previous work at IPT also involved process automation: I used AI assistance while developing code to automate the generation of descriptions for field forms. This portfolio case is a separate demonstration and should not be interpreted as a continuation of that internal tool.

## Run locally

```bash
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

## Enable the optional AI assistant

The assistant uses the OpenAI API (`gpt-4.1-mini`). The app works without an API key; only the chat feature remains disabled.

PowerShell:
```powershell
$env:OPENAI_API_KEY="your-api-key"
streamlit run app.py
```

Streamlit Community Cloud → App settings → Secrets:
```toml
OPENAI_API_KEY = "your-api-key"
```

Never commit API keys. API use may incur charges under the account's current pricing and limits.

## Technology

Python · Streamlit · Pandas · Plotly · OpenAI API

## Project status

Independent portfolio prototype. The interface and core workflow are implemented; the optional AI assistant requires a separately configured API key. No CRM integration, real customer data, autonomous actions or validated churn prediction are claimed.

---

## Versão em português

### Resumo

O NEXORA é um estudo de caso fictício de uma empresa B2B de software. A proposta é reunir indicadores de licenciamento, adoção e utilização em uma visão de carteira que ajude a identificar contas que merecem atenção e organizar prioridades de acompanhamento.

### O que a demonstração apresenta

- Dashboard de carteira com filtros e indicadores executivos.
- Análise de licenças, ativação de usuários e adoção de módulos.
- Exploração individual de contas.
- Índice heurístico e transparente de saúde da conta.
- Sugestões de próximos passos para análise humana.
- Assistente opcional de IA generativa para perguntas em linguagem natural sobre os dados fictícios.

### Relação com minha experiência

Minha experiência em um ambiente de software B2B me aproximou de temas como indicadores de utilização, acompanhamento de clientes, desempenho/adoção do produto, suporte a usuários e QA. Esses temas inspiraram a **definição do problema** do NEXORA. A implementação, a empresa fictícia, os indicadores e a base de dados foram desenvolvidos separadamente. O projeto não é um produto da Eliis e não reproduz sistemas, dados ou entregas proprietárias.

No IPT, também participei de uma iniciativa de automação de processo: utilizei assistência de IA durante o desenvolvimento de código para automatizar a geração de descrições de formulários de campo. Essa experiência é distinta do NEXORA.

### Limitações

Todos os dados são sintéticos. O índice de saúde é heurístico, não uma probabilidade de churn validada. As recomendações são regras transparentes para apoiar a análise humana. O assistente de IA é opcional e depende de uma chave de API configurada em ambiente seguro.
