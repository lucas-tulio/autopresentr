#!flask/bin/python
from app import app
from app import db
import sys

# Check if logging is enabled
print("")
with open("app.conf") as conf:
  logging = conf.readline().split("=")[1].rstrip("\n")
  if logging == "True":
    print("Logging is enabled, trying database connection...")
    try:
      db = db.Database()
      db._connect()
      print("Database connection ok. App started.\n")
    except Exception as e:
      print(e)
      sys.exit()
  else:
    print("Logging is DISABLED by default.\nTo enable it, edit 'app.conf', set 'logging' to 'True' and enter your database connection information as needed.\n")

# app.run(debug=True, host='0.0.0.0', port=8000)
app.run()
