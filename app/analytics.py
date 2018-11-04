from flask import g
from flask_login import current_user, login_user, logout_user, login_required
from app.models import Employee, Workshop, Response
import altair as alt
import pandas as pd
from app import app
from config import conn

df = pd.read_sql_query(
    "SELECT workshop.id, workshop_name, workshop_category, workshop_instructor, workshop_start, workshop_hours, class_size, e.name FROM workshop LEFT JOIN employee as e ON e.id = workshop.workshop_instructor", conn, index_col='id')
# convert datetime to '2018-09' month and year format
df['mnth_yr'] = df['workshop_start'].dt.to_period('M').astype(str)
df['workshop_category'] = df['workshop_category'].astype('category')

@app.before_request
def before_request():
    if current_user.is_authenticated:
        employee = Employee.query.filter_by(email=current_user.email).first()
        df['this_user'] = df['workshop_instructor'] == employee.id
        g.user_melted = pd.melt(
            df[df['this_user'] == True],
            id_vars=['mnth_yr', 'workshop_category'], 
            value_vars=['workshop_hours', 'class_size'])       

        g.df2 = df.copy()
        g.df2['workshop_category'] = pd.Categorical(g.df2['workshop_category']).codes
        g.dat = g.df2.set_index('workshop_start').resample('W').sum()
        g.accum = pd.melt(g.dat.reset_index(), 
            id_vars=['workshop_start','workshop_category'], 
            value_vars=['workshop_hours', 'class_size'])
        g.accum['workshop_category'] = g.accum['workshop_category'].apply(lambda x: 'Corporate' if (x == 1) else 'Public')
        g.accum['cumsum'] = g.accum.groupby(['variable','workshop_category']).cumsum().fillna(0)

        g.accumtotal = pd.melt(g.dat.reset_index(),
                    id_vars=['workshop_start'], 
                    value_vars=['class_size'])    
        g.accumtotal['cumsum'] = g.accumtotal.groupby(['variable']).cumsum().fillna(0)

        g.df3 = df[df['this_user'] == True].copy()
        g.df3['workshop_category'] = pd.Categorical(g.df3['workshop_category']).codes
        g.dat2 = g.df3.set_index('workshop_start').resample('W').sum()
        g.accum_personal = pd.melt(g.dat2.reset_index(), 
            id_vars=['workshop_start','workshop_category'], 
            value_vars=['workshop_hours', 'class_size'])
        g.accum_personal['workshop_category'] = g.accum_personal['workshop_category'].apply(lambda x: 'Corporate' if (x == 1) else 'Public')
        g.accum_personal['cumsum'] = g.accum_personal.groupby(['variable','workshop_category']).cumsum().fillna(0)

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

@app.route('/data/class_size_hours')
def class_size_hours():
    chart = alt.Chart(g.user_melted).mark_bar().encode(
        column='variable',
        x=alt.X("sum(value)"),
        y=alt.Y('mnth_yr'),
        color=alt.Color('workshop_category')
    ).properties(
        width=250
    )
    return chart.to_json()

@app.route('/data/accum_global')
def accum_global():
    chart = alt.Chart(g.accum).mark_area().encode(
        column='workshop_category',
        x=alt.X("workshop_start"),
        y=alt.Y("sum(cumsum):Q"),
        color=alt.Color("variable")
    ).properties(
        width=250
    )
    return chart.to_json()

@app.route('/data/accum_global_line')
def accum_global_line():
    chart = alt.Chart(g.accumtotal).mark_line(
        color='#212529'
    ).encode(
        x=alt.X("workshop_start", axis=alt.Axis(title='')),
        y=alt.Y("sum(cumsum):Q", axis=alt.Axis(title='Total Students'))
    ).properties(
        width=380
    )
    return chart.to_json()

@app.route('/data/accum_personal')
def accum_personal():
    chart = alt.Chart(g.accum_personal).mark_area().encode(
        column='workshop_category',
        x=alt.X("workshop_start"),
        y=alt.Y("sum(cumsum):Q"),
        color=alt.Color("variable")
    ).properties(
        width=250
    )
    return chart.to_json()

@app.route('/data/punchcode')
def punchcode():
    g.df2['workshop_category'] = g.df2['workshop_category'].apply(lambda x:'Corporate' if x == 1 else 'Public' )
    g.df2['contrib'] = g.df2['workshop_hours'] * g.df2['class_size']

    chart = alt.Chart(g.df2).mark_circle().encode(
        x='mnth_yr:O',
        y='name:O',
        size='sum(contrib):Q',
        column='workshop_category:O'
    ).properties(
        width=250
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
