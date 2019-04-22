from flask import g
from flask_login import current_user
from app import app, cache
from app.models import Employee, Workshop, Response
import altair as alt
from altair import expr, datum
import pandas as pd
import datetime as datetime
from config import conn

@cache.cached(timeout=60*60, key_prefix='hourly_db')
def getdb():
    return pd.read_sql_query(
    "SELECT workshop.id, workshop_name, workshop_category, workshop_instructor, \
        workshop_start, workshop_hours, class_size, e.name, e.active, e.university \
        FROM workshop \
        LEFT JOIN employee as e ON e.id = workshop.workshop_instructor",
        conn, index_col='id')

df = getdb()

def getuserdb():
    if current_user.is_authenticated:
        employee = Employee.query.filter_by(email=current_user.email).first()
        if employee is not None:
            df['this_user'] = df['workshop_instructor'] == employee.id
            return df

# ================ ================ ================
# ================ Global Section ================
#
# Visualization using the overall population (global)
# 
#
# ===================================================
# ===================================================

@app.route('/data/accum_global')
@cache.cached(timeout=86400, key_prefix='accum_g')
def accum_global():
    dat = df.copy()
    dat = dat.append({'workshop_start': datetime.datetime.now(), 'workshop_category': 'Corporate'}, ignore_index=True)
    dat = dat.append({'workshop_start': datetime.datetime.now(), 'workshop_category': 'Academy'}, ignore_index=True)
    dat['workshop_category'] = dat['workshop_category'].apply(lambda x: 'Corporate' if (x == 'Corporate') else 'Public').astype('category')
    dat = dat.loc[:,['workshop_start', 'workshop_category', 'workshop_hours', 'class_size']]\
        .set_index('workshop_start')\
        .groupby('workshop_category')\
        .resample('W').sum().reset_index()

    dat['workshop hours']=dat.groupby(['workshop_category'])['workshop_hours'].cumsum()
    dat['students']=dat.groupby(['workshop_category'])['class_size'].cumsum()
    dat = dat.melt(id_vars=['workshop_start', 'workshop_category'],value_vars=['workshop hours', 'students'])

    chart = alt.Chart(dat).mark_area().encode(
        column=alt.Column('workshop_category', title=None, sort="descending", 
                          header=alt.Header(
                              labelColor='#ffffff', 
                              titleAnchor="start")),
        x=alt.X("workshop_start", title="Date"),
        y=alt.Y("value:Q", title="Cumulative"),
        color=alt.Color("variable", 
            scale=alt.Scale(
                range=['#7dbbd2cc', '#bbc6cbe6']),
            legend=None
        ),
        tooltip=['variable', 'value:Q']
    ).properties(width=350).configure_axis(
        labelColor='#bbc6cbe6',
        titleColor='#bbc6cbe6', 
        grid=False
    )

    return chart.to_json()


@app.route('/data/accum_global_line')
@cache.cached(timeout=86400, key_prefix='accum_g_l')
def accum_global_line():
    dat = df.copy()
    dat = dat[['workshop_start', 'class_size']].sort_values(by='workshop_start')
    dat['cumsum'] = dat['class_size'].cumsum()

    brush = alt.selection(type='interval', encodings=['x'])
    # Create a selection that chooses the nearest point & selects based on x-value
    nearest = alt.selection(type='single', nearest=True, on='mouseover',
                            fields=['workshop_start'], empty='none')
    line = alt.Chart().mark_line(color='#cccccc', interpolate='basis').encode(
            x=alt.X("workshop_start:T", axis=alt.Axis(title='', grid=False),scale={'domain': brush.ref()}),
            y=alt.Y("cumsum", axis=alt.Axis(title='Total Students', grid=False))
    )
    selectors = alt.Chart(dat).mark_point().encode(
        x=alt.X("workshop_start:T"),
        opacity=alt.value(0)
    ).add_selection(
        nearest
    )
    points = line.mark_point().encode(
        opacity=alt.condition(nearest, alt.value(1), alt.value(0))
    )
    text = line.mark_text(align='left', dx=-20, dy=-5).encode(
        text=alt.condition(nearest, 'cumsum:Q', alt.value(' '))
    )
    rules = alt.Chart().mark_rule(color='gray').encode(
        x=alt.X("workshop_start:T"),
    ).transform_filter(
        nearest
    )

    upper = alt.layer(line, selectors, points, rules, text, data=dat, width=350)
    lower = alt.Chart().mark_area(color='#75b3cacc').encode(
            x=alt.X("workshop_start:T", axis=alt.Axis(title=''), scale={
                'domain':brush.ref()
            }),
            y=alt.Y("cumsum", axis=alt.Axis(title=''))
        ).properties(
        height=30,
        width=350
    ).add_selection(
        brush
    )

    chart = alt.vconcat(upper,lower, data=dat).configure_view(
        strokeWidth=0
    )
    return chart.to_json()

@app.route('/data/punchcode')
@cache.cached(timeout=86400, key_prefix='pc')
def punchcode():
    dat = df.copy()
    dat['mnth_yr'] = dat['workshop_start'].dt.to_period('M').astype(str)
    dat['workshop_category'] = dat['workshop_category'].apply(lambda x: 'Corporate' if (x == 'Corporate') else 'Public')
    dat['contrib'] = dat['workshop_hours'] * dat['class_size']

    chart = alt.Chart(dat[dat.name != 'Capstone']).mark_circle(color='#bbc6cbe6').encode(
        x=alt.X('mnth_yr:T', axis=alt.Axis(title='')),
        y='name:O',
        size=alt.Size('sum(contrib):Q', legend=None),
        column=alt.Column('workshop_category:O', title=None, sort="descending", 
            header=alt.Header(titleColor='#bbc6cbe6', labelColor='#bbc6cbe6', labelAngle=30, titleFontSize=40, titleAngle=30))
    ).properties(
        width=300, height=320
    ).configure_axis( 
        labelColor='#bbc6cbe6', titleColor='#bbc6cbe6', grid=False
    )
    return chart.to_json()

@app.route('/data/category_bars')
@cache.cached(timeout=86400, key_prefix='c_b')
def category_bars():
    chart = alt.Chart(df).mark_bar(color='#bbc6cbe6').encode(
        x=alt.X('sum(workshop_hours):Q', title='Accumulated Hours'),
        y=alt.Y('workshop_category:O', title=''),
        tooltip=['sum(workshop_hours):Q', 'workshop_category:O']
    )
    return chart.to_json()


# ================ ================ ================
# ================ Person Section ================
#
# Visualization relating to individual instructor
# 
#
# ===================================================
# ===================================================

@app.route('/data/person_contrib_area')
@cache.cached(timeout=86400, key_prefix='p_contrb')
def person_contrib_area():
    dat_ori = getuserdb()
    dat = dat_ori.loc[dat_ori.this_user == True,:].copy()
    dat['contrib'] = dat['workshop_hours'] * dat['class_size']

    brush = alt.selection(type='interval', encodings=['x'])
    upper = alt.Chart(dat).mark_area(
        clip=True,
        color='#7c98ae',
        opacity=1,
        interpolate='monotone'
        ).encode(
            x=alt.X("workshop_start:T", axis=alt.Axis(title=''), scale={'domain':brush.ref()}),
            y=alt.Y('sum(contrib)', axis=alt.Axis(title='Activities'))
        ).properties(width=450)
    lower = alt.Chart(dat).mark_rect(color='#75b3cacc').encode(
        x=alt.X("workshop_start:T", axis=alt.Axis(title='Interval Selector'), scale={'domain':brush.ref()})
    ).add_selection(
        brush
    ).properties(width=450)
    chart = alt.vconcat(upper, lower, data=dat).configure_axis(
        labelColor='#bbc6cbe6',
        titleColor='#bbc6cbe6',
        grid=False)

    return chart.to_json()

@app.route('/data/person_class_bar')
@cache.cached(timeout=86400, key_prefix='p_hours')
def person_class_bar():
    dat_ori = getuserdb()
    dat = dat_ori.loc[dat_ori.this_user == True,:].copy()
    dat['mnth_yr'] = dat['workshop_start'].dt.to_period('M').astype(str)
    dat = dat.melt(
        id_vars=['mnth_yr', 'workshop_category'],
        value_vars=['workshop_hours', 'class_size'])
    chart = alt.Chart(dat).mark_bar().encode(
        column='variable',
        x=alt.X("sum(value)"),
        y=alt.Y('mnth_yr'),
        color=alt.Color(
            'workshop_category',
            scale=alt.Scale(range=['#7dbbd2cc', '#bbc6cbe6', '#6eb0ea', '#d1d8e2', '#1a1d21', '#8f9fb3' ]),legend=None),
            tooltip=['workshop_category', 'sum(value)']
        ).configure_axis(
            grid=False
        ).properties(
            width=250
        )
        
    return chart.to_json()

@app.route('/data/person_vs_area')
@cache.cached(timeout=86400, key_prefix='p_v_a')
def person_vs_area():
    dat_ori = getuserdb()
    dat = dat_ori.loc[dat_ori.this_user == True,:].copy()
    dat = dat.append({'workshop_start': datetime.datetime.now(), 'workshop_category': 'Corporate'}, ignore_index=True)
    dat = dat.append({'workshop_start': datetime.datetime.now(), 'workshop_category': 'Academy'}, ignore_index=True)
    dat['workshop_category'] = dat['workshop_category'].apply(lambda x: 'Corporate' if (x == 'Corporate') else 'Public').astype('category')
    dat = dat.loc[:,['workshop_start', 'workshop_category', 'workshop_hours', 'class_size']]\
        .set_index('workshop_start')\
        .groupby('workshop_category')\
        .resample('W').sum().reset_index()
    dat['workshop hours']=dat.groupby(['workshop_category'])['workshop_hours'].cumsum()
    dat['students']=dat.groupby(['workshop_category'])['class_size'].cumsum()
    dat = dat.melt(id_vars=['workshop_start', 'workshop_category'],value_vars=['workshop hours', 'students'])
    
    chart = alt.Chart(dat).mark_area().encode(
        column='workshop_category',
        x=alt.X("workshop_start"),
        y=alt.Y("value:Q"),
        color=alt.Color("variable", 
            scale=alt.Scale(
                range=['#7dbbd2cc', '#bbc6cbe6']),
            legend=None
        ),
        tooltip=['variable', 'value:Q']
    ).properties(
        width=250
    ).configure_axis(
        grid=False
    )
    return chart.to_json()


@app.route('/data/instructor_breakdown')
@cache.cached(timeout=86400, key_prefix='ib')
def instructor_breakdown():
    # Getting Responses Data
    q = """ SELECT response.*, workshop_category, name
            FROM response
            INNER JOIN workshop as w 
                ON w.id = response.workshop_id
            INNER JOIN employee as e
                ON w.workshop_instructor = e.id
        """
    responses = pd.read_sql_query(
        q,
        conn,
        index_col='id'
    )
    resp_nw = responses[responses['workshop_category'] != 'Weekend'].groupby('name').agg('mean').round(2).sort_values('knowledge', ascending=False)
    resp_nw['total'] = resp_nw.iloc[:,1:].mean(axis=1).round(2)
    resp_nwm = pd.melt(resp_nw.iloc[:,1:].reset_index(), id_vars='name')

    multi = alt.selection_multi(fields=['name'], on='click')
    brush = alt.selection(type='interval')
    color = alt.condition(multi, alt.Color('name:N',  legend=None), alt.value('lightgray'))
    color2 = alt.condition(brush, alt.Color('name:N',  legend=None), alt.value('lightgray'))
    point = alt.Chart(df).mark_circle(size=60).encode(
        x=alt.X('workshop_start:T', axis=alt.Axis(title='')),
        y=alt.Y('sum(class_size)', axis=alt.Axis(title='Class Size', grid=False)),
        color=alt.Color('name:N', legend=None),
        tooltip=['workshop_name','monthdate(workshop_start)', 'name','class_size']
    ).transform_filter(
        multi
    ).transform_filter(
        brush
    ).properties(
        width=600
    ).interactive()
    bar = alt.Chart(df).mark_bar().encode(
        x=alt.X('sum(workshop_hours):Q', title='Accumulated Hours'),
        y=alt.Y('workshop_category:O', title=''),
        color=alt.Color('name:N', legend=None),
        tooltip=['sum(workshop_hours):Q', 'workshop_category:O']
    ).transform_filter(
        brush
    ).transform_filter(
        multi
    )
    box = alt.Chart(df).mark_rect().encode(
        x=alt.X('class_size:Q', bin=alt.Bin(maxbins=15)),
        y=alt.Y('workshop_hours:Q', bin=alt.Bin(maxbins=15)),
        color=color2,
        size=alt.Size('sum(workshop_hours):Q', legend=None),
        tooltip=['workshop_name:O', 'class_size:Q']
    ).transform_filter(
        multi
    ).add_selection(
        brush
    )
    picker = alt.Chart(df).mark_rect().encode(
        y=alt.Y('name:N'),
        color=color, 
    ).add_selection(
        multi
    )

    a = alt.Chart(resp_nwm).mark_square(size=40).encode(
        x=alt.X('variable:N', scale=alt.Scale(rangeStep=80), axis=alt.Axis(labelAngle=0)),
        y=alt.Y('value'),
        color=alt.Color('name', legend=None),
        tooltip=['name','value']
    ).transform_calculate(
        value=expr.round(expr.exp(datum.value))
    ).transform_filter(
        multi
    )

    b = a.mark_line(opacity=0.8, interpolate='monotone').encode(
        x=alt.X('variable')
    )
    chart = picker | (point & a+b) | (box & bar)
    #chart = alt.hconcat(picker, alt.vconcat(point, a+b) , alt.vconcat(box, bar))
    return chart.to_json()

# ================ ================ ================
# ================ Team Analytics Section ================
#
# Visualization relating to team analytics page
#
# ===================================================
# ===================================================
@app.route('/data/team_leadinst_line')
def team_leadinst_line():
    dat = df.copy()
    sixmonths = datetime.datetime.now() - datetime.timedelta(weeks=26)
    threemonths = datetime.datetime.now() - datetime.timedelta(weeks=13)
    dat = dat.loc[(dat.workshop_start >= sixmonths) &
            (dat.active == 1) & (dat.name != 'Capstone'), :]
    dat['workshop_period'] = dat.loc[:, 'workshop_start'].apply(lambda x: 'Last 3 months' if (x >= threemonths) else '3 months ago')
    dat = dat.loc[:,['name','workshop_period','workshop_hours']].groupby(['name','workshop_period']).count().reset_index()
    dat.columns = ['name', 'workshop_period', 'wh_count']
    dat['diff'] = dat.groupby('name').diff().fillna(method='bfill', limit=1)

    line = alt.Chart(data=dat, title='Lead Instructor Roles').mark_line().encode(
        x=alt.X('wh_count', axis=alt.Axis(title='Workshops in the last 6 months')),
        y=alt.Y('name', axis=alt.Axis(title=' ')),
        detail='name',
        color=alt.condition(
            alt.datum.diff > 0,
            alt.value("black"),
            alt.value("#fd7777")
        )
    )

    p1 = alt.Chart(data=dat).mark_point(filled=True, size=100).encode(
        x='wh_count',
        y='name',
        color=alt.Color('workshop_period:O', 
                        scale=alt.Scale(range=['#375d7b','black']),
                        legend=alt.Legend(orient='bottom-right', 
                                        title=None,
                                        offset=4, 
                                        zindex=0)
                    ),
        tooltip=['workshop_period:O', 'wh_count']
    )

    t1 = p1.mark_text(
        align='right',
        baseline='bottom',
        dx=-3, dy=-1,
    ).encode(
        text='wh_count',
        color=alt.condition(
            alt.datum.diff > 0,
            alt.value("black"),
            alt.value("#fd7777")
        )
    ).transform_filter(
        filter={"field":'workshop_period',
            "oneOf": ['Last 3 months']}
    )

    rule = alt.Chart(dat).mark_rule(color='#bbc6cb', strokeDash=[4]).encode(
        x='average(wh_count)',
        size=alt.value(1)
    )

    chart = line + p1 + t1 + rule
    chart = chart.configure_axis(grid=False).properties(width=580)

    return chart.to_json()

# ================ ================ ================
# ================ Non-Chart Section ================
#
#  Each factory is responsible for the data required 
# to render the chart and view for each page
#
# ===================================================
# ===================================================
@cache.cached(timeout=43200, key_prefix='gt_stats')
def factory_homepage():
    stats = {
        'students': df['class_size'].sum(),
        'workshops': df.shape[0],
        'studenthours': sum(df['workshop_hours']),
        # 'studenthours': sum(df['workshop_hours'] * df['class_size']),
        'companies': sum(df['workshop_category'] == 'Corporate'),
        'instructors': len(df['workshop_instructor'].unique()),
        'topten': df[df.name != 'Capstone'].loc[:,['name','workshop_hours', 'class_size']].groupby(
            'name').sum().sort_values(
                by='class_size', 
                ascending=False)
                .head(10)
                .rename_axis(None)
                .rename(
                    columns={'workshop_hours':'Total Hours',
                          'class_size':'Total Students'})
                .to_html(classes=['table thead-light table-striped table-bordered table-hover table-sm'])
    }
    return stats

def factory_analytics():
    dat = df.copy()
    sixmonths = datetime.datetime.now() - datetime.timedelta(weeks=26)
    threemonths = datetime.datetime.now() - datetime.timedelta(weeks=13)
    dat = dat.loc[(dat.workshop_start >= sixmonths) &
            (dat.active == 1) & (dat.name != 'Capstone'), :]
    dat['workshop_period'] = dat.loc[:, 'workshop_start'].apply(lambda x: 'Last 3 months' if (x >= threemonths) else '3 months ago')
    dat = dat.loc[:,['name','workshop_period','workshop_hours']].groupby(['name','workshop_period']).count().reset_index()
    dat.columns = ['name', 'workshop_period', 'wh_count']
    dat['diff'] = dat.groupby('name').diff().fillna(method='bfill', limit=1)
    df_sum = pd.DataFrame(dat.groupby('name').wh_count.sum())
    max_wh = df_sum.wh_count.max()
    min_wh = df_sum.wh_count.min()
    max_diff = dat['diff'].max()
    min_diff = dat['diff'].min()
    def gettimenow():
        import arrow
        return arrow.get(arrow.utcnow()).humanize()
    instructorstats = {
        'max_wh': max_wh,
        'min_wh': min_wh,
        'max_6mths': [i for i in df_sum[df_sum.wh_count == max_wh].index],
        'min_6mths': [i for i in df_sum[df_sum.wh_count == min_wh].index],
        'max_diff_n': max_diff,
        'min_diff_n': min_diff,
        'max_diff': [i for i in dat[dat['diff']==max_diff].name.unique()],
        'min_diff': [i for i in dat[dat['diff']==min_diff].name.unique()],
        'testing': ['John Doe', 'Max Brenner'],
        'updatewhen': gettimenow(),
    }
    return instructorstats


def factory_accomplishment(u):
    workshops = Workshop.query.filter_by(
        workshop_instructor=u.id).order_by(Workshop.workshop_start.desc())
    grped = dict()
    totalstud = 0
    totalhours = 0

    for gr in workshops:
        category = gr.workshop_category
        if category not in grped:
            grped[category] = {'count': 0, 'students': 0, 'hours': 0}
        grped[category]['count'] += 1
        grped[category]['students'] += gr.class_size
        grped[category]['hours'] += gr.workshop_hours
        totalhours += gr.workshop_hours
        totalstud += gr.class_size

    responses = Response.query.filter(Response.workshop_id.in_(w.id for w in workshops)).all()
    fullstar = Response.query.filter(Response.workshop_id.in_(w.id for w in workshops), Response.satisfaction_score + Response.knowledge >= 9).count()

    qualitative = Response.query.filter(
        Response.workshop_id.in_(w.id for w in workshops), Response.comments != '').join(
            Workshop, isouter=True).order_by(
                Workshop.workshop_start.desc()).paginate(
                    per_page=20, page=1, error_out=True)

    stats = {
            'joindate': u.join_date,
            'workshops': workshops.limit(5),
            'responses': responses,
            'grped': grped,
            'totalstud': totalstud,
            'totalhours': totalhours,
            'totalws': workshops.count(),
            'fullstar': fullstar,
            'responsecount': len(responses),
            'qualitative': qualitative,
            'topten': df[df.name != 'Capstone'].loc[:,['name','workshop_hours', 'class_size']].groupby(
                'name').sum().sort_values(
                    by='workshop_hours', 
                    ascending=False).head(10).rename_axis(None).to_html(classes=['table thead-light table-striped table-bordered table-hover table-sm'])

        }
    
    return stats
