import api
from os import mkdir
import logManager
from database import ClientKeys

log = logManager.Log()

Clientkeys = ClientKeys().createDB()

try:
    mkdir("DataBases")
    log.info("[Info] <System Event> : DataBases folder created")
except FileExistsError:
    pass

server = api.APIServer()
server.flask.run(debug=True,port=3001)
