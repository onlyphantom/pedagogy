from flask import g
from flask_login import current_user
from app import app
from app.models import Workshop, Response
import pandas as pd
from config import conn

def ongoing_workshop():
    workshops = Workshop.query.filter_by(
        workshop_instructor=g.employee.id).order_by(Workshop.workshop_start.desc())
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

    # for qualitative reviews
    qualitative = Response.query.filter(
        Response.workshop_id.in_(w.id for w in workshops), Response.comments != '').join(
            Workshop, isouter=True).order_by(
                Workshop.workshop_start.desc()).paginate(
                    per_page=20, page=1, error_out=True)

    stats = {
        'employee': g.employee,
        'workshops': workshops.limit(5),
        'responses': responses,
        'grped': grped,
        'totalstud': totalstud,
        'totalhours': totalhours,
        'totalws': workshops.count(),
        'fullstar': fullstar,
        'responsecount': len(responses),
        'qualitative': qualitative,
        # change here:
        'topten': g.df2.loc[:,['name','workshop_hours', 'class_size']].groupby(
            'name').sum().sort_values(
                by='workshop_hours', 
                ascending=False).head(10).rename_axis(None).to_html(classes=['table thead-light table-striped table-bordered table-hover table-sm'])

    }
    return stats