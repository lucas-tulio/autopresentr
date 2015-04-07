from app import app
import wikipedia

@app.route('/')
@app.route('/index')
def index():
  sp = wikipedia.page('São Paulo')
  return sp.summary
