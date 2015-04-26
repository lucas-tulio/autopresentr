# Conditional pymysql import
with open("app.conf", "r") as f:
  logging = f.readline().split("=")[1].rstrip("\n")
  if logging == "True":
    import pymysql

# Database access class
class Database:

  def __init__(self):

    self.cur = None
    self.conn = None
    self.is_logging = False

    # Read parameters
    with open("app.conf", "r") as f:
      self.logging = f.readline().split("=")[1].rstrip("\n")
      self.is_logging = logging == "True"
      self.db_host = f.readline().split("=")[1].rstrip("\n")
      self.db_port = f.readline().split("=")[1].rstrip("\n")
      self.db_user = f.readline().split("=")[1].rstrip("\n")
      self.db_password = f.readline().split("=")[1].rstrip("\n")
      self.db_schema = f.readline().split("=")[1].rstrip("\n")

  def __del__(self):
    self._disconnect()

  def _connect(self):
    self.conn = pymysql.connect(host=self.db_host, port=int(self.db_port), user=self.db_user, passwd=self.db_password, db=self.db_schema, charset='utf8')
    self.cur = self.conn.cursor()

  def _disconnect(self):
    if self.cur != None:
      self.cur.close()
    if self.conn != None:
      self.conn.close()

  #
  # Log
  #
  def log(self, request, subject, is_random):

    self._connect()
    try:
      self.cur.execute("""INSERT INTO logs (user_ip, user_agent, subject, is_random) VALUES (%s, %s, %s, %s)""", (str(request.remote_addr), str(request.user_agent), str(subject), is_random))
      self.conn.commit()
      self._disconnect()
      return True
    except Exception as e:
      print("Error inserting log")
      print(e)

    self._disconnect()
    return False
