# autopresentr
Procedural presentation generator. http://autopresentr.co

Uses the following open source projects:

- [reveal.js](https://github.com/hakimel/reveal.js)
- [Wikipedia](https://github.com/goldsmith/Wikipedia) (a [fork of mine](https://github.com/lucasdnd/Wikipedia) to be specific)
- [PyMySQL](https://github.com/PyMySQL/PyMySQL)
- [Flask](https://github.com/mitsuhiko/flask)

### Requirements

- Python 3.4
- BeautifulSoup4
- Flask
- MySQL and PyMySQL (optional)

### Setup

1. Install the requirements: `pip3 install -r requirements.tx`

1. Run the app: `python3 run.py`

##### Logging

If you need to log user access in a production environment, you can do so by following these steps:

1. Install MySQL

1. Install PyMySQL: `pip3 install pymysql`

1. Run `db/create-schema.sql` in your database

1. Open `app.conf`, set logging to True (`logging=True`) and enter your database connection info as needed.
