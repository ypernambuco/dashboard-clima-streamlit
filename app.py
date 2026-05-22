from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st


DATA_FILE = Path("data/clima_tratado.csv")
DATA_TYPE_LABELS = {
    "historico": "Histórico",
    "previsao": "Previsão",
}
DATA_TYPE_ORDER = ["historico", "previsao"]
PERIOD_ORDER = ["Histórico", "Previsão"]
PERIOD_COLOR_SCALE = alt.Scale(
    domain=PERIOD_ORDER,
    range=["#6b7280", "#14b8a6"],
)
TEMPERATURE_PERIOD_COLOR_SCALE = alt.Scale(
    domain=PERIOD_ORDER,
    range=["#fbbf24", "#f97316"],
)
PERIOD_DASH_SCALE = alt.Scale(
    domain=PERIOD_ORDER,
    range=[[0], [7, 5]],
)
WEEKDAY_ABBR = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
X_AXIS_LABEL_EXPR = (
    "{'Mon':'Seg','Tue':'Ter','Wed':'Qua','Thu':'Qui','Fri':'Sex',"
    "'Sat':'Sáb','Sun':'Dom'}[timeFormat(datum.value, '%a')] + ' ' + "
    "timeFormat(datum.value, '%d/%m')"
)


@st.cache_data
def load_data() -> pd.DataFrame:
    dataframe = pd.read_csv(DATA_FILE)
    dataframe["data"] = pd.to_datetime(dataframe["data"])
    if "tipo_dado" not in dataframe.columns:
        dataframe["tipo_dado"] = "previsao"
    dataframe["periodo"] = dataframe["tipo_dado"].map(DATA_TYPE_LABELS).fillna(
        dataframe["tipo_dado"].str.capitalize()
    )
    dataframe["data_rotulo"] = dataframe["data"].map(format_date_label)
    return dataframe


def format_date_label(value: pd.Timestamp) -> str:
    return f"{WEEKDAY_ABBR[value.weekday()]} {value:%d/%m}"


def format_number(value: float, suffix: str = "") -> str:
    return f"{value:,.1f}{suffix}".replace(",", "X").replace(".", ",").replace("X", ".")


def order_data_types(data_types: list[str]) -> list[str]:
    ordered = [data_type for data_type in DATA_TYPE_ORDER if data_type in data_types]
    ordered.extend(data_type for data_type in sorted(data_types) if data_type not in ordered)
    return ordered


def format_data_type(data_type: str) -> str:
    return DATA_TYPE_LABELS.get(data_type, data_type.capitalize())


def get_date_tick_step(dataframe: pd.DataFrame) -> int:
    date_count = dataframe["data"].dt.normalize().nunique()
    return max(1, round(date_count / 6))


def filter_data(
    dataframe: pd.DataFrame,
    selected_cities: list[str],
    selected_data_types: list[str],
    date_range: tuple,
) -> pd.DataFrame:
    start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])

    filtered = dataframe[
        (dataframe["cidade"].isin(selected_cities))
        & (dataframe["tipo_dado"].isin(selected_data_types))
        & (dataframe["data"] >= start_date)
        & (dataframe["data"] <= end_date)
    ]
    return filtered.copy()


def build_temperature_chart(dataframe: pd.DataFrame) -> alt.Chart:
    tick_step = get_date_tick_step(dataframe)
    base = alt.Chart(dataframe).encode(
        x=alt.X(
            "data:T",
            title=None,
            axis=alt.Axis(
                labelExpr=X_AXIS_LABEL_EXPR,
                tickCount=alt.TimeIntervalStep("day", tick_step),
                labelAngle=0,
                labelPadding=10,
                labelOverlap="parity",
                labelBound=True,
                grid=False,
                ticks=False,
            ),
        ),
        y=alt.Y("temperatura_media_c:Q", title="Temperatura média (°C)"),
    )

    line = base.mark_line(strokeWidth=2.6).encode(
        color=alt.Color("cidade:N", title="Cidade"),
        strokeDash=alt.StrokeDash(
            "periodo:N",
            sort=PERIOD_ORDER,
            scale=PERIOD_DASH_SCALE,
            legend=alt.Legend(title="Período", symbolStrokeColor="#94a3b8"),
        ),
        tooltip=[
            alt.Tooltip("cidade:N", title="Cidade"),
            alt.Tooltip("periodo:N", title="Período"),
            alt.Tooltip("data_rotulo:N", title="Data"),
            alt.Tooltip("temperatura_media_c:Q", title="Temperatura média", format=".1f"),
        ],
    )

    points = line.mark_circle(size=42, opacity=0.75)
    chart = line + points

    forecast = dataframe[dataframe["tipo_dado"] == "previsao"]
    if not forecast.empty:
        forecast_start = forecast["data"].min()
        forecast_end = dataframe["data"].max()
        forecast_band_data = pd.DataFrame(
            {"inicio": [forecast_start], "fim": [forecast_end + pd.Timedelta(days=1)]}
        )
        forecast_band = (
            alt.Chart(forecast_band_data)
            .mark_rect(color="#14b8a6", opacity=0.08)
            .encode(x=alt.X("inicio:T"), x2=alt.X2("fim:T"), tooltip=alt.value(None))
        )
        forecast_rule = (
            alt.Chart(pd.DataFrame({"data": [forecast_start]}))
            .mark_rule(color="#94a3b8", strokeDash=[4, 4], opacity=0.65)
            .encode(x=alt.X("data:T"), tooltip=alt.value(None))
        )
        chart = forecast_band + chart + forecast_rule + build_period_labels(dataframe)

    return (
        chart.properties(height=360)
        .configure_view(strokeWidth=0)
        .configure_axis(
            labelColor="#475569",
            titleColor="#334155",
            gridColor="#e5e7eb",
            domain=False,
        )
        .configure_legend(
            labelColor="#334155",
            titleColor="#334155",
            orient="bottom",
            direction="horizontal",
        )
    )


def build_period_labels(dataframe: pd.DataFrame) -> alt.Chart:
    label_rows = []
    for data_type in DATA_TYPE_ORDER:
        period_data = dataframe[dataframe["tipo_dado"] == data_type]
        if period_data.empty:
            continue

        start_date = period_data["data"].min()
        end_date = period_data["data"].max()
        middle_date = start_date + (end_date - start_date) / 2
        label_rows.append(
            {
                "data": middle_date,
                "periodo": format_data_type(data_type),
            }
        )

    return (
        alt.Chart(pd.DataFrame(label_rows))
        .mark_text(
            baseline="top",
            fontSize=12,
            fontWeight=600,
            color="#475569",
        )
        .encode(
            x=alt.X("data:T"),
            y=alt.value(8),
            text=alt.Text("periodo:N"),
            tooltip=alt.value(None),
        )
    )


def build_rain_chart(dataframe: pd.DataFrame) -> alt.Chart:
    rain_by_city = (
        dataframe.groupby(["cidade", "periodo"], as_index=False)["precipitacao_mm"]
        .sum()
        .sort_values("precipitacao_mm", ascending=False)
    )

    return (
        alt.Chart(rain_by_city)
        .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
        .encode(
            x=alt.X("cidade:N", title="Cidade", sort="-y"),
            xOffset=alt.XOffset("periodo:N", sort=PERIOD_ORDER),
            y=alt.Y("precipitacao_mm:Q", title="Precipitação acumulada (mm)"),
            color=alt.Color(
                "periodo:N",
                title="Período",
                sort=PERIOD_ORDER,
                scale=PERIOD_COLOR_SCALE,
            ),
            tooltip=[
                alt.Tooltip("cidade:N", title="Cidade"),
                alt.Tooltip("periodo:N", title="Período"),
                alt.Tooltip("precipitacao_mm:Q", title="Precipitação", format=".1f"),
            ],
        )
        .properties(height=320)
    )


def build_city_temperature_chart(dataframe: pd.DataFrame) -> alt.Chart:
    temp_by_city = (
        dataframe.groupby(["cidade", "periodo"], as_index=False)["temperatura_media_c"]
        .mean()
        .sort_values("temperatura_media_c", ascending=False)
    )

    return (
        alt.Chart(temp_by_city)
        .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
        .encode(
            x=alt.X("cidade:N", title="Cidade", sort="-y"),
            xOffset=alt.XOffset("periodo:N", sort=PERIOD_ORDER),
            y=alt.Y("temperatura_media_c:Q", title="Temperatura média (°C)"),
            color=alt.Color(
                "periodo:N",
                title="Período",
                sort=PERIOD_ORDER,
                scale=TEMPERATURE_PERIOD_COLOR_SCALE,
            ),
            tooltip=[
                alt.Tooltip("cidade:N", title="Cidade"),
                alt.Tooltip("periodo:N", title="Período"),
                alt.Tooltip("temperatura_media_c:Q", title="Temperatura média", format=".1f"),
            ],
        )
        .properties(height=320)
    )


def main() -> None:
    st.set_page_config(
        page_title="Dashboard de Clima",
        layout="wide",
    )

    dataframe = load_data()

    st.title("Dashboard de Clima")
    st.caption("Visualização simples dos dados tratados pelo projeto etl-clima-python-sqlite.")

    cities = sorted(dataframe["cidade"].unique())
    data_types = order_data_types(dataframe["tipo_dado"].unique().tolist())
    min_date = dataframe["data"].min().date()
    max_date = dataframe["data"].max().date()

    with st.sidebar:
        st.header("Filtros")
        selected_cities = st.multiselect(
            "Cidades",
            options=cities,
            default=cities,
        )
        selected_data_types = st.multiselect(
            "Tipo de dado",
            options=data_types,
            default=data_types,
            format_func=format_data_type,
        )
        date_range = st.date_input(
            "Período",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
        )
        only_rainy_days = st.checkbox("Mostrar apenas dias com chuva")

    if len(date_range) != 2 or not selected_cities or not selected_data_types:
        st.warning("Selecione pelo menos uma cidade, um tipo de dado e um período válido.")
        return

    filtered = filter_data(dataframe, selected_cities, selected_data_types, date_range)
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

    first_kpi_row = st.columns(3)
    first_kpi_row[0].metric("Temperatura média", format_number(average_temp, " °C"))
    first_kpi_row[1].metric("Maior temperatura", format_number(max_temp, " °C"))
    first_kpi_row[2].metric("Menor temperatura", format_number(min_temp, " °C"))

    second_kpi_row = st.columns(2)
    second_kpi_row[0].metric("Chuva acumulada", format_number(total_rain, " mm"))
    second_kpi_row[1].metric("Dias com chuva", rainy_days)

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
