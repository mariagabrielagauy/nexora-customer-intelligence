# NEXORA | Customer Intelligence

**Independent portfolio case · Product Analytics · Customer Success · AI/ML**  
**Author:** Maria Gabriela Gauy

> A fictional B2B SaaS case study exploring how product-usage and licensing signals can help teams understand adoption, identify accounts that deserve attention, and prioritize human follow-up.

[🇧🇷 Leia em português](#versão-em-português)

## The problem

In a B2B software business, a customer can remain contracted while product adoption declines. Looking only at the number of customers or total licenses can hide important signals: inactive seats, low module adoption, falling usage frequency, or a shrinking active-user base.

This prototype brings those signals together in one portfolio view.

## What the prototype does

- Monitors a fictional portfolio of **120 customer companies**.
- Summarizes customer count, licensed seats, active users and seat activation.
- Breaks down licenses across four fictional product modules.
- Explores usage frequency, active days and most-used features.
- Displays an illustrative ML-based risk score and prioritizes accounts for review.
- Suggests transparent, rule-based next steps for a human account owner.
- Supports filters and account-level exploration.

## Product and business indicators

| Dimension | Example indicators in this demo |
|---|---|
| Customer base | Number of customer companies |
| Licensing | Total seats and seats by module |
| User engagement | Active users and active-seat rate |
| Usage | Weekly sessions and active days per month |
| Feature adoption | Module adoption and most-used feature |
| Customer monitoring | Usage change, inactivity, support signals and illustrative risk band |

## How to run locally

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Community Cloud

1. Push this repository to a **public GitHub repository**.
2. Sign in to Streamlit Community Cloud with GitHub.
3. Select **Create app**, choose this repository, branch `main`, and file `app.py`.
4. Deploy. No API key or secret is required for this version.

## Technology

Python · Streamlit · Pandas · Plotly · scikit-learn

## Data, privacy and scope

All data in `data/synthetic_customers.csv` is generated for this demonstration. The company, accounts, license allocations, usage indicators and churn labels are fictional. No Eliis, IPT, university, customer or research data is included.

This is an independent portfolio project. It is **not** an Eliis product and should not be presented as work deployed at Eliis. The case is inspired by general B2B software adoption and customer-monitoring questions; the implementation and fictional data were created separately for this portfolio.

## Model limitations

The Random Forest model is trained and evaluated only in the context of simulated labels. Its risk score is illustrative, not a validated churn prediction. Thresholds are demonstration choices. Recommendations are deterministic business rules, not autonomous AI decisions. The prototype does not contact customers, change licenses or update a CRM.

A real deployment would require authorized data, temporal validation, calibration, bias and performance monitoring, security review, and human oversight.

## Project status

Portfolio prototype. The local app and data checks are included; real customer integrations, LLM assistant, production monitoring and validated predictive performance are out of scope.

---

## Versão em português

### Visão geral

O NEXORA é um estudo de caso fictício de uma empresa B2B de software. O projeto explora como indicadores de licenciamento e utilização podem ajudar a compreender a adoção do produto, identificar contas que merecem atenção e organizar prioridades de acompanhamento.

### O que a demonstração apresenta

- Carteira fictícia de 120 empresas clientes.
- Quantidade de empresas, licenças contratadas, usuários ativos e taxa de ativação.
- Distribuição de licenças entre quatro módulos fictícios.
- Frequência de utilização, dias ativos no mês e funcionalidades mais utilizadas.
- Pontuação ilustrativa de risco baseada em um modelo de machine learning.
- Recomendações transparentes para orientar a análise humana de cada conta.

### Relação com minha experiência

A escolha do problema foi inspirada em temas gerais de acompanhamento de software B2B presentes na minha experiência profissional, como indicadores de utilização, clientes, licenças e desempenho/adoção do produto. O NEXORA é uma implementação independente, com dados inteiramente sintéticos; não reproduz sistemas, dados, métricas proprietárias ou entregas da Eliis.

### Como executar

```bash
pip install -r requirements.txt
streamlit run app.py
```

### Limitações

Os dados e resultados são simulados. A pontuação de risco não representa uma previsão validada e as recomendações não são decisões automatizadas. O protótipo não se conecta a CRM nem realiza contato com clientes.
