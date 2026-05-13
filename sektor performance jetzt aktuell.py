

#---Sektor Performance---
st.title("Weltweite Sektor Performance")

# Slider für Zeiteinstellung
zeit_map = {"1 Woche": 7, "1 Monat": 30, "6 Monate": 180, "1 Jahr": 365,"5 Jahr":1825}
auswahl = st.select_slider("Zeitraum wählen", options=list(zeit_map.keys()), value="1 Monat")

df_perf = get_sector_performance(zeit_map[auswahl])

# Heatmap (Treemap) erstellen
if not df_perf.empty:
    fig = px.treemap(
        df_perf,
        path=["Sektor"], 
        values="Weight", 
        color="Performance %",
        color_continuous_scale="RdYlGn", 
        color_continuous_midpoint=0,
        # Wir übergeben die Performance-Daten als custom_data für den Hover/Text
        custom_data=["Performance %", "Ticker"],
        title="Sektor Performance Übersicht" # Titel muss ein String sein, keine Liste!
    )

    # Hier definieren wir, was auf der Kachel stehen soll
    # %{label} ist der Name des Sektors, %{customdata[0]} ist die Performance
    fig.update_traces(
        texttemplate="<b>%{label}</b><br>%{customdata[0]:.2f}%",
        textposition="middle center",
        textfont_size=16
    )
    #Layout Einstellungen
    fig.update_layout(margin=dict(t=50, l=10, r=10, b=10), height=500)
    #Chart zeigen
    st.plotly_chart(fig, use_container_width=True)




    #COPY Sektor performance
    