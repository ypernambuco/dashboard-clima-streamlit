# dashboard-clima-streamlit

Dashboard simples em Streamlit para visualizar dados de clima tratados pelo projeto `etl-clima-python-sqlite`.

O app mostra histórico recente dos últimos 7 dias, previsão futura, KPIs, gráficos e uma tabela filtrável. É um projeto de estudo para praticar visualização de dados, não um sistema profissional de meteorologia.

## Dashboard Online

https://dashboard-clima.streamlit.app/

O dashboard está publicado no Streamlit Community Cloud usando este repositório do GitHub.

## Objetivo Do Projeto

- criar uma visualização simples para dados de clima;
- mostrar indicadores por cidade e período;
- filtrar dados históricos e dados de previsão;
- praticar Streamlit em um contexto de dados;
- conectar a visualização com uma base gerada por um pipeline ETL.

## Tecnologias Utilizadas

- Python
- Streamlit
- pandas
- Altair
- CSV
- Streamlit Community Cloud

## Como Executar

Crie e ative um ambiente virtual:

```bash
python -m venv .venv
```

No Windows:

```powershell
.venv\Scripts\activate
```

Instale as dependências:

```bash
python -m pip install -r requirements.txt
```

Execute o dashboard:

```bash
streamlit run app.py
```

## Deploy

Configuração usada no Streamlit Community Cloud:

- arquivo principal: `app.py`
- branch: `main`
- Python configurado nas opções avançadas do deploy

O projeto também mantém um `runtime.txt`. A versão do Python foi ajustada no Streamlit Cloud para manter o deploy compatível com as dependências.

## Estrutura De Pastas

```text
dashboard-clima-streamlit/
|-- assets/
|   |-- screenshots/
|   |   |-- dashboard.png
|   |   |-- tabela-dados.png
|-- data/
|   |-- clima_tratado.csv
|-- app.py
|-- README.md
|-- requirements.txt
|-- runtime.txt
```

## Fonte Dos Dados

O dashboard lê o arquivo:

```text
data/clima_tratado.csv
```

Esse CSV é gerado pelo projeto:

https://github.com/ypernambuco/etl-clima-python-sqlite

A base atual contém histórico recente dos últimos 7 dias e previsão futura. A coluna `tipo_dado` separa os registros em `historico` e `previsao`.

## Screenshots

### Visão Geral

![Dashboard de clima](assets/screenshots/dashboard.png)

### Gráficos E Tabela

![Gráficos e tabela de dados filtrados](assets/screenshots/tabela-dados.png)

## O Que Aprendi

- criar um dashboard com Streamlit;
- carregar uma base CSV com pandas;
- usar filtros por cidade, período e tipo de dado;
- criar KPIs simples;
- montar gráficos com Altair;
- publicar um app no Streamlit Community Cloud;
- documentar o link de deploy e as limitações do projeto.

## Limitações

- usa uma base pequena;
- depende dos dados gerados pelo ETL;
- depende da API de clima usada pelo projeto de ETL;
- os dados históricos são limitados;
- não atualiza automaticamente sozinho sem rodar um novo pipeline;
- lê um CSV local em vez de conectar direto ao SQLite;
- não é um sistema profissional de meteorologia;
- ainda não possui testes automatizados.

## Próximos Passos

- conectar diretamente ao SQLite do projeto de ETL;
- adicionar opção de upload de CSV;
- incluir mais cidades ou períodos maiores;
- melhorar a explicação da origem dos dados dentro do próprio app.
