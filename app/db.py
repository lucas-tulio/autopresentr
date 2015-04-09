import pymysql

class Database:

  def __init__(self):

    self.cur = None
    self.conn = None

    # Read parameters
    f = open("db.conf", "r")
    self.db_host = f.readline().split("=")[1].rstrip("\n")
    self.db_port = f.readline().split("=")[1].rstrip("\n")
    self.db_user = f.readline().split("=")[1].rstrip("\n")
    self.db_password = f.readline().split("=")[1].rstrip("\n")
    self.db_schema = f.readline().split("=")[1].rstrip("\n")
    f.close()

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
  def log(self, request, subject):

    self._connect()
    try:
      self.cur.execute("""INSERT INTO logs (user_ip, user_agent, subject) VALUES (%s, %s, %s)""", (str(request.remote_addr), str(request.user_agent), str(subject)))
      self.conn.commit()
      self._disconnect()
      return True
    except Exception as e:
      print("Error inserting log")
      print(e)

    self._disconnect()
    return False
