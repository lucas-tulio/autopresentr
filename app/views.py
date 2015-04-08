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

  # Settings
  detail_level = 0.2 # 0 = minimum text, 1 = full page

  # Get the page
  subject = request.form['subject']
  page = wikipedia.page(subject)
  sections = page.sections

  # Generate summary slides (from 3 to 5, if available)


  # Remove sections that we're not interested into
  try:
    sections.remove('External links')
    sections.remove('References')
    sections.remove('See also')
  except Exception as e:
    pass

  # Get an image
  summary_image = ""
  try:
    summary_image = page.images[0]
  except Expcetion as e:
    print("No images to use")

  # Generate sections
  sections_html = ""
  for section in sections:
    section_content = page.section(section)

    # Section title
    sections_html = sections_html + "<section><h2>" + section + "</h2></section>"

    # Section content
    section_sentences = section_content.strip('\n').split('. ')
    if len(section_sentences) == 1 and section_sentences[0] == '':
      continue

    i = 0
    num_sentences = int(len(section_sentences) * detail_level)
    
    if (num_sentences == 0):
      num_sentences = 1
    for sentence in section_sentences:
      if i % num_sentences == 0 and sentence != '':
        sections_html = sections_html + "<section><p>" + sentence + ".</p></section>"
      i = i + 1

  return render_template('presentation.html',
    title=page.title,
    summary_image=summary_image,
    summary=page.summary.split('.')[0] + ".",
    sections=Markup(sections_html))







