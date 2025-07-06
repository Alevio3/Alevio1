import streamlit as st
import pandas as pd

def handlungsempfehlung(df, case_col, activity_col, timestamp_col):
    st.title("Handlungsempfehlungen & Insights")

    # Engpässe erkennen (Aktivitäten mit längster mittlerer Verweildauer)
    df = df.sort_values([case_col, timestamp_col])
    df['next_time'] = df.groupby(case_col)[timestamp_col].shift(-1)
    df['duration'] = (pd.to_datetime(df['next_time']) - pd.to_datetime(df[timestamp_col])).dt.total_seconds() / 60
    bottlenecks = df.groupby(activity_col)['duration'].mean().dropna().sort_values(ascending=False)

    st.subheader("Automatisch erkannte Schwachstellen")
    if not bottlenecks.empty:
        st.write("Die folgenden Aktivitäten haben die längste mittlere Verweildauer (potenzielle Engpässe):")
        st.dataframe(bottlenecks.rename("Ø Verweildauer (min)"))
        top_bottleneck = bottlenecks.index[0]
        st.warning(f"**Engpass erkannt:** Die Aktivität '{top_bottleneck}' ist ein potenzieller Flaschenhals im Prozess.")

        # Einfache Optimierungsvorschläge
        st.subheader("Vorschläge für Optimierungen")
        st.info(f"**Empfehlung:** Analysiere die Ursachen für Verzögerungen bei '{top_bottleneck}'. "
                "Mögliche Maßnahmen: Automatisierung, bessere Ressourcenzuteilung, Prozessvereinfachung.")
    else:
        st.success("Keine auffälligen Engpässe im Prozess erkannt.")

    # Weitere Insights: Fälle mit besonders langer Durchlaufzeit
    st.subheader("Fälle mit langer Durchlaufzeit")
    case_times = df.groupby(case_col)[timestamp_col].agg(['min', 'max'])
    case_times['Durchlaufzeit (min)'] = (pd.to_datetime(case_times['max']) - pd.to_datetime(case_times['min'])).dt.total_seconds() / 60
    long_cases = case_times.sort_values('Durchlaufzeit (min)', ascending=False).head(5)
    st.dataframe(long_cases[['Durchlaufzeit (min)']])
    if not long_cases.empty:
        st.info("Überprüfe die oben stehenden Fälle auf Besonderheiten oder Ausreißer.")