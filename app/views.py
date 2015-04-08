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

  # Get the page
  subject = request.form['subject']
  page = wikipedia.page(subject)
  sections = page.sections

  # Remove sections that we're not interested into
  try:
    sections.remove('External links')
    sections.remove('References')
    sections.remove('See also')
  except Exception as e:
    pass

  # Generate 
  sections_html = ""
  for item in sections:
    sections_html = sections_html + "<section><h2>" + item + "</h2></section>"

  return render_template('presentation.html',
    title=page.title,
    summary_image=page.images[0],
    summary=page.summary.split('.')[0] + ".",
    sections=Markup(sections_html))