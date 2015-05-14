from app import app
from app.db import Database

from flask import render_template
from flask import Markup
from flask import request
import nltk.data

import requests

from . import wikipedia
from app.html_extractor import WikiHTMLParser

# Database access, if needed
db = Database()

# Settings
min_slide_length = 150 # Min text inside one slide, in characters (used in summary only)
detail_level = 0.5 # Presentation detail level. 0 = minimum number of slides, 1 = lots of slides

@app.route('/')
@app.route('/index')
def index():
  return render_template('index.html')

@app.route('/presentation', methods=['POST'])
def presentation():

  # Get the subject
  query = request.form['subject']
  try:
    lang = request.form['language']
  except Exception as e:
    lang = "en"

  # Summary by lang
  summary_translate = {
    'en': 'Summary',
    'pt': 'Introdução'
  }

  # Thank by lang
  thank_translate = {
      'en': 'Thank You',
      'pt': 'Obrigado',
      'es': 'Gracias',
      'it': 'Grazie',
      'fr': 'Merci',
      'de': 'Danke'
  }

  # Theme selection
  theme = "css/theme/black.css"
  if "theme:" in query:
    query_split = query.split("theme:")
    theme = query_split[1]
    if theme in ['beige', 'black', 'blood', 'league', 'moon', 'night', 'serif', 'simple', 'sky', 'solarized', 'white']:
      theme = "css/theme/" + query_split[1] + ".css"
    else:
      theme = "css/theme/black.css"
    subject = query_split[0]
  else:
    subject = query

  # Language selection
  wikipedia.set_lang(lang)

  # Check for a random subject
  is_random = False
  if subject == "":
    is_random = True
    subject = wikipedia.random()

  # Log the request
  if db.is_logging:
    db.log(request, subject, is_random)

  # Get the page, check for disambiguation
  try:
    page = wikipedia.page(subject, preload=True)
  except wikipedia.exceptions.DisambiguationError as e:

    # Make a list of links with each option
    links = "<p>"
    for option in e.options:
      links = links + "<form name='" + option + "' action='presentation' method='post'> " \
        "<input type='hidden' id='subject-input' name='subject' value='" + option + "'/> " \
        "<input type='hidden' id='language-input' name='language' value='" + lang + "'/> " \
        "</form>\n" \
        "<a href='#' onclick=\"enterPresentation('" + option + "')\">" + option + "</a><br/>\n"
    links = links + "</p>"

    return render_template("disambiguation.html",
      subject=subject,
      options=Markup(links))

  except wikipedia.exceptions.PageError as e:

    return render_template("404.html",
      message=Markup("<p>'" + subject + "' could not be found.</p>")), 404

  except requests.exceptions.ConnectionError as e:
    wikipedia.set_lang("en")
    page = wikipedia.page(subject, preload=True)

  #
  # Start building the presentation
  #

  # Parse the HTML to extract tables
  # Table extractor
  html_parser = WikiHTMLParser()
  html_parser.feed(page.html())
  html_parser.clean()

  # Use NLTK to split sentences without errors
  sent_detector = nltk.data.load("tokenizers/punkt/english.pickle")

  # Get some images
  images = [image for image in page.images if ".jpg" in image]

  #
  # Generate the title slide
  #
  if len(images) > 0:
    title_html = "<section data-state='intro'><h1 data-state='intro'>" + page.title + "</h1></section>"
  else:
    title_html = "<section><h1>" + page.title + "</h1></section>"

  #
  # Generate a summary
  #
  summary_html = "<section><h2>" + summary_translate[lang] + "</h2>"
  summary_sentences = ""
  if page.summary is not None and page.summary != "":
    summary_sentences = sent_detector.tokenize(page.summary.split('\n')[0].strip())

  # Get an image
  try:
    title_background = images[0]
  except Exception as e:
    title_background = None

  # Here we append two or more sentences in the same slide if they're too small
  usable_sentences = []
  append_next = False
  already_appended = False
  for sentence in summary_sentences:

    if already_appended:
      already_appended = False
      continue

    if append_next:
      usable_sentences[-1] = usable_sentences[-1] + " " + sentence
      append_next = False
      already_appended = True
      continue

    usable_sentences.append(sentence)
    if len(sentence) < min_slide_length:
      append_next = True

  # Generate the summary pages
  summary_page = 0
  for sentence in usable_sentences:
    if summary_page == 0:
      summary_html = summary_html + "<p>" + sentence + "</p></section>"
    else:
      summary_html = summary_html + "<section><p>" + sentence + "</p></section>"
    summary_page = summary_page + 1

  #
  # Generate sections
  #
  sections = page.sections

  # Filter out the sections we're not interested in
  ignored_sections_en = ['External links',    'References',  'See also',   'Bibliography', 'Further reading', 'Footnotes', 'Notes', 'Sources']
  ignored_sections_pt = ['Ligações externas', 'Referências', 'Ver também', 'Bibliografia', 'Leitura adicional',            'Notas', 'Fontes']
  if lang == "en":
    sections = [section for section in sections if section not in ignored_sections_en]
  elif lang == "pt":
    sections = [section for section in sections if section not in ignored_sections_pt]

  # Sections title and content
  sections_html = ""
  section_title = ""

  for section in sections:

    # Get the text in that section
    section_content = page.section(section)

    # If the section is empty, concat its title to the next section title
    if section_content is None or section_content == "":
      section_title = section + ": "
      continue
    else:
      section_title = section_title + section

    # Section title
    sections_html = sections_html + "<section><h2>" + section_title + "</h2></section>"
    section_title = ""

    # Any tables to show?
    table_html = None
    try:
      table_html = [html_parser.tables[i][1] for i, v in enumerate(html_parser.tables) if v[0] == section][0]
    except Exception as e:
      table_html = None
      pass

    # Adjust table size
    if table_html is not None and table_html != "":
      font_size = 36
      if len(table_html) > 800:
        font_size = 16
      sections_html = sections_html + "<section style='font-size: " + str(font_size) + "px;'>" + table_html + "</section>"

    # Get the section paragraphs, according to the detail_level
    section_paragraphs = section_content.split('\n')
    num_paragraphs = int(len(section_paragraphs) * detail_level)

    if (num_paragraphs == 0):
      num_paragraphs = 1

    i = 0
    every = int(len(section_paragraphs) / num_paragraphs)
    for paragraph in section_paragraphs:
      if i % every == 0 and paragraph != '':
        sections_html = sections_html + "<section><p>" + sent_detector.tokenize(paragraph.strip())[0] + "</p></section>"
      i = i + 1

  return render_template('presentation.html',
    theme=theme,
    title=Markup(title_html),
    page_title=page.title,
    title_background=title_background,
    summary=Markup(summary_html),
    sections=Markup(sections_html),
    thank=thank_translate[lang])

@app.errorhandler(404)
def page_not_found(e):
  return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
  return render_template('500.html'), 500
