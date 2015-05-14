from html.parser import HTMLParser
import re

class WikiHTMLParser(HTMLParser):

  def __init__(self):

    HTMLParser.__init__(self)

    self.tables = [] # Will be a list of tuples: (section, table_html)
    self.images = [] # Will be a list of tuples: (section, image_url)

    # Current parsing state
    self.inside_header = False
    self.inside_span = False
    self.reading_table = False
    self.reading_image = False
    
    # Current section; and table being extracted
    self.current_section = ""
    self.current_table = ""

  def handle_starttag(self, tag, attrs):

    tag = tag.strip()

    # Table!
    if self.reading_table:
      
      # Keep the colspan
      colspan_html = ""
      for attr in attrs:
        # attr[0] is the attribute name, attr[1] is the attribute value
        if attr[0] == "colspan":
          colspan_html = "colspan='" + attr[1] + "' "

      self.current_table = self.current_table + "<" + tag
      if colspan_html != "":
        self.current_table = self.current_table + " " + colspan_html
      self.current_table = self.current_table + " >"

    # Image!
    elif self.reading_image:

      # Get the image src
      src = ""
      for attr in attrs:
        # attr[0] is the attribute name, attr[1] is the attribute value
        if attr[0] == "src":
          src = attr[1]

      if self.current_section.strip() != "" and src.strip() != "":
        self.images.append((self.current_section, src))

    # Navigating through the html
    if tag in ["h1", "h2", "h3", "h4", "h5", "h6"]:
      self.inside_header = True
      return

    # We need to get the text inside <span>s
    if self.inside_header and tag == "span":
      self.inside_span = True

    # Found a table!
    if tag == "table":
      self.reading_table = True
      self.current_table = "<table>"
    
    # Found an image!
    elif tag == "img":
      self.reading_image = True
      self.current_image = "<img "

  def handle_endtag(self, tag):

    tag = tag.strip()

    if self.reading_table:
      self.current_table = self.current_table + "</" + tag + ">"

    if tag in ["h1", "h2", "h3", "h4", "h5", "h6"]:
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

  def clean(self):

    # Cleans up tags written like "< a>" and "< span />"
    # I hate having to do this
    new_tuples = []
    for table_tuple in self.tables:
      h = table_tuple[1]
      h = h.replace("< ", "<") \
           .replace(" <", "<") \
           .replace(" >", ">") \
           .replace("> ", ">") \
           .replace(" />", "/>") \
           .replace("/> ", "/>") \
           .replace(" /> ", "/>") \
           .replace(" / > ", "/>") \
           .replace("<a>", " ") \
           .replace("</a>", " ") \
           .replace("<img>", " ") \
           .replace("</img>", " ")

      # Remove reference square brackets
      h = re.sub("\[.*?\]", "", h).strip()
      
      new_table_tuple = (table_tuple[0], h)
      new_tuples.append(new_table_tuple)
    
    self.tables = new_tuples

    # Cleans up the images list: we only want the jpegs
    new_image_tuples = []
    print(self.images)
    for image_tuple in self.images:
      img = image_tuple[1]
      if ".svg" not in img:
        new_image_tuples.append(img)
    self.images = new_image_tuples
