import logging
import os
from time import localtime

class Log:
    def __init__(self, dir="Logs"):
        Time = localtime()
        Date = f"{Time.tm_year}-{Time.tm_mon}"

        self.dir = os.path.join(dir, Date)

        os.makedirs(self.dir, exist_ok=True)

    def logWrite(self, message):
        Time = localtime()

        Date = f"{Time.tm_year}-{Time.tm_mon}-{Time.tm_mday}"
        Hour = f"{Time.tm_hour}:{Time.tm_min}:{Time.tm_sec}"
        
        fileName = f"Log[{Date}].txt"

        path = os.path.join(self.dir, fileName)

        with open(path, "a", encoding="utf-8") as file:
            file.write(f"[>{Hour}<] "+message + "\n")

    def info(self, message, ip=None):
        if ip != None:
            message = message + f" (IP {ip})"

        logging.info(message)
        self.logWrite(message)

    def error(self, message, ip=None):
        if ip != None:
            message = message + f" (IP {ip})"

        logging.error(message)
        self.logWrite(message)