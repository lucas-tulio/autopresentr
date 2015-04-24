from html.parser import HTMLParser

class WikiHTMLParser(HTMLParser):

  def __init__(self):

    HTMLParser.__init__(self)

    self.tables = [] # Will be a list of tuples

    # Current parsing state
    self.inside_header = False
    self.inside_span = False
    self.reading_table = False
    
    # Current section; and table being extracted
    self.current_section = ""
    self.current_table = ""

  def handle_starttag(self, tag, attrs):

    tag = tag.strip()

    if self.reading_table:
      self.current_table = self.current_table + "<" + tag + ">"

    if tag == "h1" or tag == "h2" or tag == "h3" or tag == "h4" or tag == "h5" or tag == "h6":
      self.inside_header = True
      return

    if self.inside_header and tag == "span":
      self.inside_span = True

    if tag == "table":
      self.reading_table = True
      self.current_table = "<table>"

  def handle_endtag(self, tag):

    tag = tag.strip()

    if self.reading_table:
      self.current_table = self.current_table + "</" + tag + ">"

    if tag == "h1" or tag == "h2" or tag == "h3" or tag == "h4" or tag == "h5" or tag == "h6":
      self.inside_header = False
      return
    
    if self.inside_header and tag == "span":
      self.inside_header = False

    # Finish reading table
    if tag == "table":
      self.reading_table = False
      if self.current_section.strip() != "" and self.current_table.strip() != "":
        self.tables.append((self.current_section, self.current_table))

  def handle_data(self, data):

    if self.reading_table:
      self.current_table = self.current_table + data

    clean_data = data.strip()
    if self.inside_header and self.inside_span and clean_data != "":
      self.current_section = clean_data
