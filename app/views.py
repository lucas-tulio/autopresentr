from app import app
from flask import render_template
from flask import Markup
from flask import request
from . import wikipedia

@app.route('/')
@app.route('/index')
def index():
  return render_template('index.html')

@app.route('/presentation', methods=['POST'])
def presentation():

  subject = request.form['subject']
  print(subject)

  page = wikipedia.page(subject)
  sections = page.sections

  sections_html = "<ul>"
  for item in sections:
    print(item)
    sections_html = sections_html + "<li>" + item + "</li>"
  sections_html = sections_html + "</ul>"

  return render_template('presentation.html',
    title=page.title,
    summary=page.summary.split('.')[0],
    sections=Markup(sections_html))