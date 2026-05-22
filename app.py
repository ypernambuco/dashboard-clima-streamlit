from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st


DATA_FILE = Path("data/clima_tratado.csv")


@st.cache_data
def load_data() -> pd.DataFrame:
    dataframe = pd.read_csv(DATA_FILE)
    dataframe["data"] = pd.to_datetime(dataframe["data"])
    return dataframe


def format_number(value: float, suffix: str = "") -> str:
    return f"{value:,.1f}{suffix}".replace(",", "X").replace(".", ",").replace("X", ".")


def filter_data(dataframe: pd.DataFrame, selected_cities: list[str], date_range: tuple) -> pd.DataFrame:
    start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])

    filtered = dataframe[
        (dataframe["cidade"].isin(selected_cities))
        & (dataframe["data"] >= start_date)
        & (dataframe["data"] <= end_date)
    ]
    return filtered.copy()


def build_temperature_chart(dataframe: pd.DataFrame) -> alt.Chart:
    return (
        alt.Chart(dataframe)
        .mark_line(point=True)
        .encode(
            x=alt.X("data:T", title="Data"),
            y=alt.Y("temperatura_media_c:Q", title="Temperatura média (°C)"),
            color=alt.Color("cidade:N", title="Cidade"),
            tooltip=[
                alt.Tooltip("cidade:N", title="Cidade"),
                alt.Tooltip("data:T", title="Data"),
                alt.Tooltip("temperatura_media_c:Q", title="Temperatura média", format=".1f"),
            ],
        )
        .properties(height=360)
    )


def build_rain_chart(dataframe: pd.DataFrame) -> alt.Chart:
    rain_by_city = (
        dataframe.groupby("cidade", as_index=False)["precipitacao_mm"]
        .sum()
        .sort_values("precipitacao_mm", ascending=False)
    )

    return (
        alt.Chart(rain_by_city)
        .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
        .encode(
            x=alt.X("cidade:N", title="Cidade", sort="-y"),
            y=alt.Y("precipitacao_mm:Q", title="Precipitação acumulada (mm)"),
            color=alt.Color("cidade:N", legend=None),
            tooltip=[
                alt.Tooltip("cidade:N", title="Cidade"),
                alt.Tooltip("precipitacao_mm:Q", title="Precipitação", format=".1f"),
            ],
        )
        .properties(height=320)
    )


def build_city_temperature_chart(dataframe: pd.DataFrame) -> alt.Chart:
    temp_by_city = (
        dataframe.groupby("cidade", as_index=False)["temperatura_media_c"]
        .mean()
        .sort_values("temperatura_media_c", ascending=False)
    )

    return (
        alt.Chart(temp_by_city)
        .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
        .encode(
            x=alt.X("cidade:N", title="Cidade", sort="-y"),
            y=alt.Y("temperatura_media_c:Q", title="Temperatura média (°C)"),
            color=alt.Color("cidade:N", legend=None),
            tooltip=[
                alt.Tooltip("cidade:N", title="Cidade"),
                alt.Tooltip("temperatura_media_c:Q", title="Temperatura média", format=".1f"),
            ],
        )
        .properties(height=320)
    )


def main() -> None:
    st.set_page_config(
        page_title="Dashboard de Clima",
        page_icon="☀️",
        layout="wide",
    )

    dataframe = load_data()

    st.title("Dashboard de Clima")
    st.caption("Visualização simples dos dados tratados pelo projeto etl-clima-python-sqlite.")

    cities = sorted(dataframe["cidade"].unique())
    min_date = dataframe["data"].min().date()
    max_date = dataframe["data"].max().date()

    with st.sidebar:
        st.header("Filtros")
        selected_cities = st.multiselect(
            "Cidades",
            options=cities,
            default=cities,
        )
        date_range = st.date_input(
            "Período",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
        )
        only_rainy_days = st.checkbox("Mostrar apenas dias com chuva")

    if len(date_range) != 2 or not selected_cities:
        st.warning("Selecione pelo menos uma cidade e um período válido.")
        return

    filtered = filter_data(dataframe, selected_cities, date_range)
    if only_rainy_days:
        filtered = filtered[filtered["precipitacao_mm"] > 0]

    if filtered.empty:
        st.info("Nenhum dado encontrado para os filtros selecionados.")
        return

    average_temp = filtered["temperatura_media_c"].mean()
    max_temp = filtered["temperatura_maxima_c"].max()
    min_temp = filtered["temperatura_minima_c"].min()
    total_rain = filtered["precipitacao_mm"].sum()
    rainy_days = int((filtered["precipitacao_mm"] > 0).sum())

    kpi_columns = st.columns(5)
    kpi_columns[0].metric("Temperatura média", format_number(average_temp, " °C"))
    kpi_columns[1].metric("Maior temperatura", format_number(max_temp, " °C"))
    kpi_columns[2].metric("Menor temperatura", format_number(min_temp, " °C"))
    kpi_columns[3].metric("Chuva acumulada", format_number(total_rain, " mm"))
    kpi_columns[4].metric("Dias com chuva", rainy_days)

    st.divider()

    st.subheader("Temperatura média por dia")
    st.altair_chart(build_temperature_chart(filtered), use_container_width=True)

    left_column, right_column = st.columns(2)
    with left_column:
        st.subheader("Precipitação por cidade")
        st.altair_chart(build_rain_chart(filtered), use_container_width=True)

    with right_column:
        st.subheader("Temperatura média por cidade")
        st.altair_chart(build_city_temperature_chart(filtered), use_container_width=True)

    st.subheader("Dados filtrados")
    st.dataframe(
        filtered.sort_values(["data", "cidade"]),
        use_container_width=True,
        hide_index=True,
    )


if __name__ == "__main__":
    main()
