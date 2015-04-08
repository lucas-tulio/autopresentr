from app import app
from flask import render_template
from . import wikipedia
from flask import Markup

@app.route('/')
@app.route('/index')
def index():

  page = wikipedia.page('São Paulo')
  sections = page.sections

  sections_html = "<ul>"
  for item in sections:
    print(item)
    sections_html = sections_html + "<li>" + item + "</li>"
  sections_html = sections_html + "</ul>"

  return render_template('index.html',
    title=page.title,
    summary=page.summary.split('.')[0],
    sections=Markup(sections_html))
