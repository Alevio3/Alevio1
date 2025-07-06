import streamlit as st
import pandas as pd

def kpi_dashboard(df, case_col, activity_col, timestamp_col, user_col=None):
    st.title("KPI-Dashboard")

    # Filtermöglichkeiten
    st.sidebar.header("Filter")
    min_date = pd.to_datetime(df[timestamp_col]).min()
    max_date = pd.to_datetime(df[timestamp_col]).max()
    date_range = st.sidebar.date_input("Zeitraum wählen", [min_date, max_date])
    filtered_df = df[
        (pd.to_datetime(df[timestamp_col]) >= pd.to_datetime(date_range[0])) &
        (pd.to_datetime(df[timestamp_col]) <= pd.to_datetime(date_range[1]))
    ]

    if user_col:
        users = filtered_df[user_col].unique()
        selected_users = st.sidebar.multiselect("Benutzer wählen", users, default=list(users))
        filtered_df = filtered_df[filtered_df[user_col].isin(selected_users)]

    # Durchlaufzeiten berechnen
    st.subheader("Durchlaufzeiten je Case")
    case_times = filtered_df.groupby(case_col)[timestamp_col].agg(['min', 'max'])
    case_times['Durchlaufzeit (min)'] = (pd.to_datetime(case_times['max']) - pd.to_datetime(case_times['min'])).dt.total_seconds() / 60
    st.dataframe(case_times[['Durchlaufzeit (min)']])

    st.metric("Ø Durchlaufzeit (min)", round(case_times['Durchlaufzeit (min)'].mean(), 2))
    st.metric("Median Durchlaufzeit (min)", round(case_times['Durchlaufzeit (min)'].median(), 2))

    # Häufigkeiten Aktivitäten
    st.subheader("Häufigkeit der Aktivitäten")
    activity_counts = filtered_df[activity_col].value_counts()
    st.bar_chart(activity_counts)

    # Engpässe: Aktivitäten mit längster mittlerer Verweildauer
    st.subheader("Engpässe (mittlere Verweildauer je Aktivität)")
    filtered_df = filtered_df.sort_values([case_col, timestamp_col])
    filtered_df['next_time'] = filtered_df.groupby(case_col)[timestamp_col].shift(-1)
    filtered_df['duration'] = (pd.to_datetime(filtered_df['next_time']) - pd.to_datetime(filtered_df[timestamp_col])).dt.total_seconds() / 60
    bottlenecks = filtered_df.groupby(activity_col)['duration'].mean().dropna().sort_values(ascending=False)
    st.dataframe(bottlenecks.rename("Ø Verweildauer (min)"))

    # Drilldown: Auswahl eines Cases
    st.subheader("Drilldown: Einzelner Case")
    selected_case = st.selectbox("Case auswählen", filtered_df[case_col].unique())
    st.dataframe(filtered_df[filtered_df[case_col] == selected_case])