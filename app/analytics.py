import altair as alt
import pandas as pd
from app import app
from config import conn
#from altair import Chart, X, Y, Axis, Data, DataFormat

df = pd.read_sql_query("SELECT * FROM workshop", conn, index_col='id')
# convert datetime to '2018-09' month and year format
df['mnth_yr'] = df['workshop_start'].dt.to_period('M').astype(str)
# TODO: change to compare to current user instead of hardcoded to Samuel
df['this_user'] = df['workshop_instructor'] == 1

@app.route('/data/class_size_vs')
def class_size_vs():
    chart = alt.Chart(df).mark_area(
        opacity=0.75,
        interpolate='step'
    ).encode(
        alt.X("class_size:Q", bin=alt.Bin(maxbins=12)),
        alt.Y('count()', stack=None),
        alt.Color(
            'this_user',
            scale=alt.Scale(range=['#000000', '#62092f'])
        )
    )
    return chart.to_json()

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
