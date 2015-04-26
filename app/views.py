from app import app
from app.db import Database

from flask import render_template
from flask import Markup
from flask import request
import nltk.data

from . import wikipedia
from app.html_extractor import WikiHTMLParser

# Database access, if needed
db = Database()

# Table extractor
html_parser = WikiHTMLParser()

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
  subject = request.form['subject']
  if subject == '':
    subject = wikipedia.random()

  # Log the request
  if db.is_logging:
    db.log(request, subject)

  # Get the page, check for disambiguation
  try:
    page = wikipedia.page(subject, preload=True)
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

  except wikipedia.exceptions.PageError as e:

    return render_template("404.html",
      message=Markup("<p>'" + subject + "' could not be found.</p>")), 404

  #
  # Start building the presentation
  #

  # Parse the HTML to extract tables
  html_parser.feed(page.html())
  html_parser.clean()

  # Use NLTK to split sentences without errors
  sent_detector = nltk.data.load("tokenizers/punkt/english.pickle")

  # Get some images
  images = [image for image in page.images if ".jpg" in image]

  #
  # Generate a summary
  #
  summary_html = "<section><h2>Summary</h2>"
  summary_sentences = sent_detector.tokenize(page.summary.split('\n')[0].strip())

  # Get an image
  try:
    summary_image = images[0]
  except Exception as e:
    summary_image = None

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
      summary_html = summary_html + "<p>" + sentence + "</p>"
      if summary_image is not None:
        summary_html = summary_html + "<img style='position: relative; max-width: 50%; max-height: 30%;' src='" + summary_image + "' />"
      summary_html = summary_html + "</section>"
    else:
      summary_html = summary_html + "<section><p>" + sentence + "</p></section>"
    summary_page = summary_page + 1

  #
  # Generate sections
  #
  sections = page.sections

  # Filter out the sections we're not interested in
  ignored_sections = ['External links', 'References', 'See also', 'Bibliography', 'Further reading', 'Footnotes', 'Notes']
  sections = [section for section in sections if section not in ignored_sections]

  # Sections title and content
  sections_html = ""
  section_title = ""

  for section in sections:

    # Get the text in that section
    section_content = page.section(section)

    # If the section is empty, concat its title to the next section title
    if section_content == "":
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
    title=page.title,
    summary_image=summary_image,
    summary=Markup(summary_html),
    sections=Markup(sections_html))

@app.errorhandler(404)
def page_not_found(e):
  return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
  return render_template('500.html'), 500
