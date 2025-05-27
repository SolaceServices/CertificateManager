import datetime;
import os

class Logger:
  def __init__(self, logName: str):
    if not os.path.exists("logs"):
        os.mkdir("logs")
    
    self.logfile = "logs/" + logName + ".txt"
    self.log("Starting " +  logName)
    
  def log(self, logtxt: str):
    ct = datetime.datetime.now()

    with open(self.logfile, 'a') as f:
        f.write(str(ct))       
        f.write(": " + logtxt + '\n')

  def addSeperator(self):
    with open(self.logfile, 'a') as f:
        f.write("---------------------------------------------------------------" + '\n')
