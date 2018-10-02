import altair as alt
import pandas as pd
from app import app
#from altair import Chart, X, Y, Axis, Data, DataFormat

@app.route('/data/mediumos')
def mediumos():
    home = pd.read_csv('data/home.csv')
    # home = home[home['Medium'].notnull()]
    chart = alt.Chart(home).mark_bar().encode(
        x='Medium',
        y='count()',
        column='OSGroup',
        color='Medium'
    )
    return chart.to_json()

@app.route('/data/studentprof')
def studentprof():
    academy = pd.read_csv('data/academy.csv')
    chart = alt.Chart(academy).mark_bar().encode(
        # rangeStep allocates 20px for each bar
        alt.X('Medium:N', scale=alt.Scale(rangeStep=20), axis=alt.Axis(title='')),
        alt.Y('count():Q', axis=alt.Axis(title='Observations', grid=False)),
        column='OSGroup:N',
        color=alt.Color(
            'Are you a student or a professional?:N',
            scale=alt.Scale(range=["#EA98D2", "#659CCA"]))
    ).configure_axis(
        domainWidth=0.8
    )
    return chart.to_json()
