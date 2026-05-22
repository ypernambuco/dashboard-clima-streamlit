# dashboard-clima-streamlit

Dashboard simples em Streamlit para visualizar dados de clima tratados no projeto `etl-clima-python-sqlite`.

A ideia é mostrar KPIs, filtros e gráficos a partir de uma base pequena, mantendo o projeto simples e fácil de entender.

## Objetivo

- criar uma visualização simples para dados de clima;
- mostrar indicadores por cidade e período;
- permitir filtros básicos;
- exibir gráficos e uma tabela com os dados filtrados;
- praticar Streamlit em um contexto de dados.

## Fonte Dos Dados

O arquivo usado pelo dashboard está em:

```text
data/clima_tratado.csv
```

Ele foi gerado a partir deste projeto:

https://github.com/ypernambuco/etl-clima-python-sqlite

A amostra é pequena de propósito. O foco aqui é visualizar os dados de forma simples, sem depender de uma base grande ou de uma integração mais complexa.

## Como Rodar

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

## O Que O Dashboard Mostra

- temperatura média no período;
- maior e menor temperatura;
- precipitação acumulada;
- quantidade de dias com chuva;
- comparação entre cidades;
- evolução diária da temperatura;
- tabela com os dados filtrados.

## Screenshot

![Dashboard de clima](assets/screenshots/dashboard.png)

O print usa uma amostra pequena de dados, suficiente para mostrar os filtros, KPIs e gráficos principais.

## Estrutura

```text
dashboard-clima-streamlit/
|-- assets/
|   |-- screenshots/
|-- data/
|   |-- clima_tratado.csv
|-- app.py
|-- README.md
|-- requirements.txt
```

## Aprendizados

Neste projeto, pratiquei:
- criação de dashboard com Streamlit;
- leitura de CSV com pandas;
- uso de filtros por cidade e período;
- criação de KPIs simples;
- exibição de gráficos e tabelas;
- organização básica de um projeto visual.

Também foi útil separar este dashboard do ETL. Assim, o projeto fica focado só na parte de visualização dos dados.

## Limitações

O projeto ainda tem algumas limitações:

- usa uma amostra pequena de dados;
- não atualiza automaticamente a base;
- lê um CSV local em vez de conectar direto ao SQLite;
- os filtros ainda são simples;
- não possui autenticação;
- não está publicado em cloud;
- não possui testes automatizados.

O objetivo foi manter o dashboard simples e fácil de explicar.

## Próximos Passos

- conectar diretamente ao SQLite do projeto de ETL;
- adicionar opção de upload de CSV;
- publicar no Streamlit Community Cloud;
- incluir mais cidades ou períodos maiores;
- adicionar uma página simples explicando a origem dos dados.
