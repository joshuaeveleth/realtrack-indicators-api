import sqlite3
from app import app
from forms import IndicatorForm
from flask import render_template, flash, redirect, _app_ctx_stack, request, jsonify, url_for, json
import os

PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))
DATABASE = os.path.join(PROJECT_ROOT, 'db', 'indicators.sqlite')

def get_db():
    top = _app_ctx_stack.top
    db = getattr(top, '_database', None)
    if db is None:
        db = top._database = sqlite3.connect(DATABASE)
    return db

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

@app.route("/indicators", methods = ['GET','POST'])
def indicators():
    project = request.args.get('project')
    country = request.args.get('country')
    indicatorlist = []
    for indic in query_db("select * from indicators where post = ? and project = ?",[country, project]):
        indicatorlist.append(json.dumps({'post':indic[0],'project':indic[2],'goal':indic[3],'objective':indic[4],'indicator':indic[5]},encoding="utf-8"))

    return render_template('indicators.html',country=country,project=project,indicatorlist=indicatorlist)

@app.route("/")
@app.route("/index", methods = ['GET','POST'])
def index():
    form = IndicatorForm(request.form)
    countrylist = []
    for country in query_db("select distinct post from indicators order by post"):
        countrylist.append((country[0],country[0]))
    form.country.choices = countrylist

    projectlist = []
    for project in query_db("select distinct project from indicators where post = ? order by project",[countrylist[0][0]]):
        projectlist.append((project[0],project[0]))
    form.project.choices = projectlist

    if request.method == 'POST':
        return redirect(url_for('indicators', country=form.country.data, project=form.project.data))
    return render_template('index.html',title='Home',form=form)

@app.route("/updateprojects", methods = ['POST'])
def updateprojects():
    country = request.form['country']
    projectlist = []
    for project in query_db("select distinct project from indicators where post = ? order by project",[country]):
        projectlist.append(project[0])
    return jsonify({'options': projectlist})

@app.teardown_appcontext
def close_connection(exception):
    top = _app_ctx_stack.top
    db = getattr(top, '_database', None)
    if db is not None:
        db.close()
