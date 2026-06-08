from flask import Flask, request, jsonify
from database import databaseManager, userManager, folders as DataBaseSysFolders, ClientKeys
import newClientRondomKey
import os

class APIServer:
    def __init__(self):
        self.flask = Flask(__name__)

        self.database_manager = databaseManager()
        self.user_manager = userManager()
        self.ClientKeys = ClientKeys()

        self.DBpages()
        self.UserPages()

        self.columnNames = ["username","password","realname","email","userdata"]
    
    def DBMessages(self,respons):
        if respons == self.database_manager.success_code:
            return respons
        Messages = {
            "systemError" : [
                {"Error" : "An unexpected error occurred in the system. Please try again later"},
                500],

            "database already exists" : [
                {"Error" : "This database already exists! Please choose a different name"},
                409],

            "user password is incorrect" : [
                {"Error" : "User password is incorrect"},
                409],

            "incorrect password" : [
                {"Error" : "DB Password did not match"},
                401],

            "database not found" : [
                {"404" : "Database not found"},
                404],

            "user not found" : [
                {"404" : "User not found"},
            404],

            "key is wrong" : [
                {"Error" : "Rescue key is wrong"},
                401]
        }
        try:
            return Messages[respons]
        except KeyError:
            return Messages["systemError"] 
        
    def checkingParameters(self,parameters:list):
        for index in range(len(parameters)):
            if parameters[index] == None:
                return {"Error" : "Missing parameters"}
        
        return None
    
    def checkingClientKey(self,key):
        respons = self.ClientKeys.check_Key(key=key)
        return respons
    
    def DBpages(self):
        @self.flask.route("/new/client",methods=["POST"])
        def new_client():
            NEWclient_key = newClientRondomKey.key()
            try:
                os.mkdir(DataBaseSysFolders.DB+NEWclient_key)

                self.ClientKeys.key_save(NEWclient_key,str(request.remote_addr))

                return jsonify({
                    "info" : "New client key created",
                    "key" : NEWclient_key
                }),201
            except FileExistsError:
                return jsonify({
                    "error" : "Could not create new client"
                }),409

        @self.flask.route("/new/database",methods=["POST"])
        def new_database():
            parameters = request.get_json()
            client_ip = str(request.remote_addr)

            DB_name = parameters.get("db-name")
            DB_password = parameters.get("db-password")
            ClientKey = request.headers.get("client-key")

            checkingparameters = self.checkingParameters([DB_name,DB_password,ClientKey])

            if checkingparameters != None:
                return jsonify(checkingparameters),400
            
            if self.checkingClientKey(ClientKey) == "systemError":
                return jsonify(self.DBMessages("systemError")[0]),self.DBMessages("systemError")[1]
            
            if self.checkingClientKey(ClientKey) == False:
                return jsonify({
                    "Error" : "You entered the wrong client key"
                }),401
            
            new_db = self.database_manager.new(dbName=DB_name,dbpassword=DB_password,clientKey=ClientKey+"/",clientIP=client_ip)
            
            respons = self.DBMessages(new_db)

            if respons != self.database_manager.success_code:
                return jsonify(respons[0]),respons[1]
            
            rescuekey = self.database_manager.rescuekeyRead(dbName=DB_name,dbPassword=DB_password,clientKey=ClientKey+"/",clientIP=client_ip)

            return jsonify({
                "Info" : "Database created successfully",
                "Database Name" : DB_name,
                "Database Password" : DB_password,
                "Rescue key" : rescuekey["rescuekey"],
                "Warning" : "Don’t forget the database Rescue key and password! Also, keep your Rescue key safe!"
            }),201

        @self.flask.route("/database/delete",methods=["POST"])
        def database_delete():
            parameters = request.get_json()
            client_ip = str(request.remote_addr)

            DB_name = parameters.get("db-name")
            DB_password = parameters.get("db-password")
            ClientKey = request.headers.get("client-key")

            checkingparameters = self.checkingParameters([DB_name,DB_password,ClientKey])
            
            if checkingparameters != None:
                return jsonify(checkingparameters),400
            
            if self.checkingClientKey(ClientKey) == "systemError":
                return jsonify(self.DBMessages("systemError")[0]),self.DBMessages("systemError")[1]

            if self.checkingClientKey(ClientKey) == False:
                return jsonify({
                    "Error" : "You entered the wrong client key"
                }),401
          
            delete_db = self.database_manager.delete(dbName=DB_name,dbPassword=DB_password,clientKey=ClientKey+"/",clientIP=client_ip)
            
            respons = self.DBMessages(delete_db)

            if respons != self.database_manager.success_code:
                return jsonify(respons[0]),respons[1]

            return jsonify({
                "Info" : "The database was successfully deleted"
            }),200
    
        @self.flask.route("/database/new_password",methods=["POST"])
        def database_newpassword():
            parameters = request.get_json()
            client_ip = str(request.remote_addr)

            DB_name = parameters.get("db-name")
            DB_rescueKey = parameters.get("rescue-key")
            DB_newPassword = parameters.get("db-new-password")
            ClientKey = request.headers.get("client-key")

            checkingparameters = self.checkingParameters([DB_name,DB_rescueKey,DB_newPassword,ClientKey])

            if checkingparameters != None:
                return jsonify(checkingparameters),400
            
            if self.checkingClientKey(ClientKey) == "systemError":
                return jsonify(self.DBMessages("systemError")[0]),self.DBMessages("systemError")[1]

            if self.checkingClientKey(ClientKey) == False:
                return jsonify({
                    "Error" : "You entered the wrong client key"
                }),401
            
            passwordupgrade_db = self.database_manager.NewDBPassword(
                dbName=DB_name,
                dbRescueKey=DB_rescueKey,
                dbNewPassword=DB_newPassword,
                clientIP=client_ip,
                clientKey=ClientKey+"/"
                )
            
            respons = self.DBMessages(passwordupgrade_db)

            if respons != self.database_manager.success_code:
                return jsonify(respons[0]),respons[1]
            
            return jsonify({
                "Info" : "Password changed successfully",
                "Password" : DB_newPassword,
                "Warning" : "Don’t forget the database Rescue key and password! Also, keep your Rescue key safe!"
            }),200
        
        
        @self.flask.route("/database/view_rescuekey",methods=["POST"])
        def database_view_rescuekey():
            parameters = request.get_json()
            client_ip = str(request.remote_addr)

            DB_name = parameters.get("db-name")
            DB_password = parameters.get("db-password")
            ClientKey = request.headers.get("client-key")

            checkingparameters = self.checkingParameters([DB_name,DB_password,ClientKey])

            if checkingparameters != None:
                return jsonify(checkingparameters),400
            
            if self.checkingClientKey(ClientKey) == "systemError":
                return jsonify(self.DBMessages("systemError")[0]),self.DBMessages("systemError")[1]

            if self.checkingClientKey(ClientKey) == False:
                return jsonify({
                    "Error" : "You entered the wrong client key"
                }),401
            
            viewRescuekey_db = self.database_manager.rescuekey_get(
                dbName=DB_name,
                dbPassword=DB_password,
                clientIP=client_ip,
                clientKey=ClientKey+"/"
            )

            if isinstance(viewRescuekey_db, dict) and "key" in viewRescuekey_db:
                return jsonify({
                    "Rescue Key" : viewRescuekey_db["key"]
                }),200
            
            respons = self.DBMessages(viewRescuekey_db)

            if respons != self.database_manager.success_code:
                return jsonify(respons[0]),respons[1]
            else:
                mess = self.DBMessages("systemError")
                return jsonify(mess[0]),mess[1]
        
    def UserPages(self):
        @self.flask.route("/database/new/user", methods=["POST"])
        def database_new_user():
            parameters = request.get_json()
            client_ip = str(request.remote_addr)

            ClientKey = request.headers.get("client-key")

            DB_name = request.headers.get("db-name")
            DB_password = request.headers.get("db-password")

            user_Name = parameters.get("user-name")
            user_Password = parameters.get("user-password")
            user_Realname = parameters.get("user-realname")
            user_Email = parameters.get("user-email")
            user_Data = parameters.get("user-data")

            UserDatas = {
                "username" : user_Name,
                "password" : user_Password,
                "realname" : user_Realname,
                "email" : user_Email,
                "userdata" : user_Data
                }

            checkingparameters = self.checkingParameters([DB_name,DB_password,ClientKey, user_Name,user_Password])

            if checkingparameters != None:
                return jsonify(checkingparameters),400
            
            if self.checkingClientKey(ClientKey) == "systemError":
                return jsonify(self.DBMessages("systemError")[0]),self.DBMessages("systemError")[1]

            if self.checkingClientKey(ClientKey) == False:
                return jsonify({
                    "Error" : "You entered the wrong client key"
                }),401
            
            User_add = self.user_manager.new(
                dbName= DB_name,
                dbPassword= DB_password,
                clientKey= ClientKey+"/",
                clientIP= client_ip,
                userDatas= UserDatas
            )

            respons = self.DBMessages(User_add)

            if respons != self.database_manager.success_code:
                return jsonify(respons[0]),respons[1]
            
            return jsonify({
                "Info" : "New user created"
            }),201
        
        @self.flask.route("/user/all-data", methods=["POST"])
        def user_all_data():
            parameters = request.get_json()
            client_ip = str(request.remote_addr)

            ClientKey = request.headers.get("client-key")

            DB_name = request.headers.get("db-name")
            DB_password = request.headers.get("db-password")

            user_Name = parameters.get("user-name")

            checkingparameters = self.checkingParameters([DB_name,DB_password,ClientKey, user_Name])

            if checkingparameters != None:
                return jsonify(checkingparameters),400
            
            if self.checkingClientKey(ClientKey) == "systemError":
                return jsonify(self.DBMessages("systemError")[0]),self.DBMessages("systemError")[1]

            if self.checkingClientKey(ClientKey) == False:
                return jsonify({
                    "Error" : "You entered the wrong client key"
                }),401
            
            user_allData = self.user_manager.userData_get(
                dbName=DB_name,
                dbPassword=DB_password,
                clientKey=ClientKey+"/",
                clientIP=client_ip,
                userName=user_Name
                )
            
            if (isinstance(user_allData, list)) and (user_allData[0] == self.database_manager.success_code):
                return jsonify(user_allData[1]),200
            
            else:
                respons = self.DBMessages(user_allData)
                if (respons == None) or not (isinstance(respons, list)):
                    respons = self.DBMessages("systemError")
                    return jsonify(respons[0]),respons[1]
                
                return jsonify(respons[0]),respons[1]
        
        @self.flask.route("/user/query", methods=["POST"])
        def user_query():
            parameters = request.get_json()
            client_ip = str(request.remote_addr)

            ClientKey = request.headers.get("client-key")

            DB_name = request.headers.get("db-name")
            DB_password = request.headers.get("db-password")

            column_Name = parameters.get("column-name")
            value = parameters.get("value")

            checkingparameters = self.checkingParameters([DB_name,DB_password,ClientKey, column_Name,value])


            if checkingparameters != None:
                return jsonify(checkingparameters),400
            
            if self.checkingClientKey(ClientKey) == "systemError":
                return jsonify(self.DBMessages("systemError")[0]),self.DBMessages("systemError")[1]

            if self.checkingClientKey(ClientKey) == False:
                return jsonify({
                    "Error" : "You entered the wrong client key"
                }),401

            if not column_Name in self.columnNames:
                return jsonify({
                    "Error" : "You entered the wrong column name"
                }),400
            
            User_Query = self.user_manager.User_columnQuery(
                dbName=DB_name,
                dbPassword=DB_password,
                clientKey=ClientKey+"/",
                clientIP=client_ip,
                value=value,
                columnName=column_Name
            )

            if (isinstance(User_Query, list)) and (User_Query[0] == self.database_manager.success_code):
                return jsonify(User_Query[1]),200
            
            else:
                respons = self.DBMessages(User_Query)
                if (respons == None) or not (isinstance(respons, list)):
                    respons = self.DBMessages("systemError")
                    return jsonify(respons[0]),respons[1]
                
                return jsonify(respons[0]),respons[1]
            
        @self.flask.route("/user/update",methods=["POST"])
        def user_update():
            parameters = request.get_json()
            client_ip = str(request.remote_addr)

            ClientKey = request.headers.get("client-key")

            DB_name = request.headers.get("name")
            DB_password = request.headers.get("password")

            user_Name = parameters.get("user-name")
            column_Name = parameters.get("column-name")
            value = parameters.get("value")

            checkingparameters = self.checkingParameters([DB_name,DB_password,ClientKey, column_Name,value,user_Name])

            if checkingparameters != None:
                return jsonify(checkingparameters),400
            
            if self.checkingClientKey(ClientKey) == "systemError":
                return jsonify(self.DBMessages("systemError")[0]),self.DBMessages("systemError")[1]

            if self.checkingClientKey(ClientKey) == False:
                return jsonify({
                    "Error" : "You entered the wrong client key"
                }),401

            if not column_Name in self.columnNames:
                return jsonify({
                    "Error" : "You entered the wrong column name"
                }),400
            
            User_update = self.user_manager.User_update(
                dbName=DB_name,
                userName=user_Name,
                dbPassword=DB_password,
                clientKey=ClientKey+"/",
                clientIP=client_ip,
                columnName=column_Name,
                Data=value
                )

            respons = self.DBMessages(User_update)

            if respons != self.database_manager.success_code:
                return jsonify(respons[0]),respons[1]
            
            return jsonify({
                "Info" : "Update was done successfully"
            }),201
        
        @self.flask.route("/user/delete",methods=["POST"])
        def user_delete():
            parameters = request.get_json()
            client_ip = str(request.remote_addr)

            ClientKey = request.headers.get("client-key")

            DB_name = request.headers.get("name")
            DB_password = request.headers.get("password")

            user_Name = parameters.get("user-name")

            checkingparameters = self.checkingParameters([DB_name,DB_password,ClientKey,user_Name])

            if checkingparameters != None:
                return jsonify(checkingparameters),400
            
            if self.checkingClientKey(ClientKey) == "systemError":
                return jsonify(self.DBMessages("systemError")[0]),self.DBMessages("systemError")[1]

            if self.checkingClientKey(ClientKey) == False:
                return jsonify({
                    "Error" : "You entered the wrong client key"
                }),401
            
            User_delete = self.user_manager.User_delete(
                dbName=DB_name,
                dbPassword=DB_password,
                clientKey=ClientKey+"/",
                clientIP=client_ip,
                userName=user_Name
            )

            respons = self.DBMessages(User_delete)

            if respons != self.database_manager.success_code:
                return jsonify(respons[0]),respons[1]

            return jsonify({
                "Info" : f"User named {user_Name} has been deleted."
            }),200

