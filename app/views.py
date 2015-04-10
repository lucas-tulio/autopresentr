from app import app
from app.db import Database
from flask import render_template
from flask import Markup
from flask import request
from . import wikipedia

db = Database()

@app.route('/')
@app.route('/index')
def index():
  return render_template('index.html')

@app.route('/presentation', methods=['POST'])
def presentation():

  # Settings
  detail_level = 0.5 # 0 = minimum text, 1 = full page

  # Get the subject
  subject = request.form['subject']
  if subject == '':
    subject = wikipedia.random()

  # Log the request
  db.log(request, subject)

  # Get the page, check for disambiguation
  try:
    page = wikipedia.page(subject)
  except wikipedia.exceptions.DisambiguationError as e:

    # Make a list of links with each option
    links = "<p>"
    for option in e.options:
      links = links + "<form name='" + option + "' action='presentation' method='post'> " \
        "<input type='hidden' id='subject-input' name='subject' value='" + option + "'/> " \
        "</form>\n" \
        "<a href='#' onclick=\"enterPresentation('" + option + "')\">" + option + "</a><br/>\n"
    links = links + "</p>"

    return render_template("disambiguation.html",
      subject=subject,
      options=Markup(links))

  # All good, get sections
  sections = page.sections

  # Remove sections that we're not interested into
  try: sections.remove('External links')
  except Exception as e: pass
  try: sections.remove('References')
  except Exception as e: pass
  try: sections.remove('See also')
  except Exception as e: pass
  try: sections.remove('Bibliography')
  except Exception as e: pass
  try: sections.remove('Further reading')
  except Exception as e: pass
  try: sections.remove('Footnotes')
  except Exception as e: pass

  # Get an image
  summary_image = ""
  try:
    summary_image = page.images[0]
  except Exception as e:
    pass

  # Generate sections
  sections_html = ""
  for section in sections:
    section_content = page.section(section)

    # Section title
    sections_html = sections_html + "<section><h2>" + section + "</h2></section>"

    # Section content
    if section_content is None:
      continue

    section_sentences = section_content.split('\n')
    if len(section_sentences) == 1 and section_sentences[0] == '':
      continue

    num_sentences = int(len(section_sentences) * detail_level)

    if (num_sentences == 0):
      num_sentences = 1

    i = 0
    every = int(len(section_sentences) / num_sentences)
    for sentence in section_sentences:
      if i % every == 0 and sentence != '':
        sections_html = sections_html + "<section><p>" + sentence.split('. ')[0] + ".</p></section>"
      i = i + 1

  return render_template('presentation.html',
    title=page.title,
    summary_image=summary_image,
    summary=page.summary.split('.')[0] + ".",
    sections=Markup(sections_html))

@app.errorhandler(404)
def page_not_found(e):
  return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
  return render_template('500.html'), 500
