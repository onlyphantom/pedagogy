import altair as alt
import pandas as pd
from app import app
#from altair import Chart, X, Y, Axis, Data, DataFormat

@app.route('/data/bar')
def data_bar():
    hotjar = pd.read_csv('data/home.csv')
    hotjar['Medium'] = hotjar['How did you hear about us?'].str.split('-').str[0]
    hotjar['OSGroup'] = hotjar['OS'].str.split(' ').str[0]

    chart = alt.Chart(hotjar).mark_bar().encode(
        x='Medium',
        y='count(User)',
        column='OSGroup'
    )
    return chart.to_json()
