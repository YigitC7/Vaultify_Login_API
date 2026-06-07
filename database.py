import sqlite3
from os import listdir, remove
import timeDate
import cryptologyAlgorithm
import rescueKeyCreate
import logManager

class folders:
    Script = "sqliteScript/"
    DB = "DataBases/"


class databaseTools:
    def sqlScriptRead(file_name):
        with open(folders.Script+file_name, "r", encoding="utf-8") as file:
            return file.read()
        
    def checkingDB(dbName, clientKey, ReturnMessages="database already exists"):
        LogPrint = logManager.Log()
        
        try:
            databases = listdir(folders.DB+clientKey)

            if (dbName+".db" in databases):
                return [True,ReturnMessages]
            else:
                return [False,ReturnMessages]
        except Exception as err:
            LogPrint.error(f"[Error] !From database.checkingDB <System Error> : {err}")
            return "systemError"
        
    def rescuekeyReader(dbName,clientKey):
        connect = sqlite3.connect(folders.DB+clientKey+dbName+".db")
        cursor = connect.cursor()

        cursor.execute(databaseManager().sqliteScript["db-rescuekey-select"])
        data = cursor.fetchall()

        rescueKeyAlogrithm = cryptologyAlgorithm.UltraEncrypt(dbName)
        rescueKey = rescueKeyAlogrithm.decrypt(data[0][0])

        connect.close()
        return rescueKey
    
    def passwordCheck(dbName,dbPassword,clientKey,clientIP):
        print(folders.DB+clientKey+dbName+".db")
        LogPrint = logManager.Log()

        try:
            connect = sqlite3.connect(folders.DB+clientKey+dbName+".db",timeout=14)
            cursor = connect.cursor()

            cursor.execute(databaseManager().sqliteScript["db-password-select"])
            data = cursor.fetchall()
            
            cryptPassword = data[0][0]

            DB_PasswordAlogrithm = cryptologyAlgorithm.UltraEncrypt(dbPassword)
            DBRealPassword = DB_PasswordAlogrithm.decrypt(cryptPassword)

            connect.close()

        except Exception as err:
            LogPrint.error(f"[Error] !From database.passwordCheck <Database Read Error> : {err}",clientIP)
            return "systemError"
        
        connect.close()
        
        if dbPassword == DBRealPassword:
            return True
        else:
            return False
        
    def UserDatabaseConnect(dbName,clientKey,clientIP,timeout=15):
        LogPrint = logManager.Log()

        try:
            return sqlite3.connect(folders.DB+clientKey+dbName+".db",timeout=timeout)
        except Exception as err:
            LogPrint.error(f"[Error] !From database.UserDatabaseConnect <Database connect error> : {err}",ip=clientIP)
            return "systemError"
        
    def UserEncryptPassword(password):
        DB_PasswordAlogrithm = cryptologyAlgorithm.UltraEncrypt(password)
        return DB_PasswordAlogrithm.encrypt(password)
    
    def userDecryptPassword(password):
        DB_PasswordAlogrithm = cryptologyAlgorithm.UltraEncrypt(password)
        realPassword = DB_PasswordAlogrithm.decrypt(password)

        if realPassword == password:
            return realPassword

class databaseManager:
    def __init__(self):
        self.sqliteScript = {
            "new-db-info" : databaseTools.sqlScriptRead("DB/new-db-info.sql"),
            "new-db-users" : databaseTools.sqlScriptRead("DB/new-db-users.sql"),
            "new-db-info-write" : databaseTools.sqlScriptRead("DB/new-db-info-write.sql"),
            "db-password-select" : databaseTools.sqlScriptRead("DB/db-password-select.sql"),
            "db-rescuekey-select" : databaseTools.sqlScriptRead("DB/db-rescuekey-select.sql"),
            "db-new-password" : databaseTools.sqlScriptRead("DB/db-new-password.sql"),

            "new-user" : databaseTools.sqlScriptRead("User/new-user.sql"),
            "user-datas-select" : databaseTools.sqlScriptRead("User/user-datas-select.sql"),
            "user-delete" : databaseTools.sqlScriptRead("User/user-delete.sql"),

            "new-ClientKeys-DB" : databaseTools.sqlScriptRead("ClientKey/new-client-key-db.sql"),
            "Client-save" : databaseTools.sqlScriptRead("ClientKey/client-save.sql"),
            "check-key" : databaseTools.sqlScriptRead("ClientKey/check-key.sql")
        }
        
        self.LogPrint = logManager.Log()
        self.success_code = "ok"
    
    def new(self,dbName,dbpassword,clientKey,clientIP):        
        DB_PasswordAlogrithm = cryptologyAlgorithm.UltraEncrypt(dbpassword)
        DB_Sec_Password = DB_PasswordAlogrithm.encrypt(dbpassword)

        rescueKey = rescueKeyCreate.randomRK()
        rescueKeyAlogrithm = cryptologyAlgorithm.UltraEncrypt(dbName)
        DB_Sec_rescueKey = rescueKeyAlogrithm.encrypt(rescueKey)

        checkingDB = databaseTools.checkingDB(dbName=dbName,clientKey=clientKey)
        
        if checkingDB == "systemError":
            return checkingDB

        if checkingDB[0] == True:
            return checkingDB[1]

        try:
            connect = sqlite3.connect(folders.DB+clientKey+dbName+".db")
            cursor = connect.cursor()

            cursor.execute(self.sqliteScript["new-db-info"])
            cursor.execute(self.sqliteScript["new-db-users"])
            cursor.execute(self.sqliteScript["new-db-info-write"], (DB_Sec_Password, timeDate.date(), DB_Sec_rescueKey, dbName))

            connect.commit()
            connect.close()

        except Exception as err:
            self.LogPrint.error(f"[Error] !From database.new <DB Process Error> : {err}",clientIP)
            return "systemError"

        self.LogPrint.info(f"[Info] <Database Created> : {dbName}",clientIP)
        return self.success_code
    
    def delete(self,dbName,dbPassword,clientKey,clientIP):
        checkingDB = databaseTools.checkingDB(dbName=dbName,clientKey=clientKey)

        if checkingDB == "systemError":
            return checkingDB

        if checkingDB[0] == False:
            return checkingDB[1]

        passwordIsTrue = databaseTools.passwordCheck(dbName=dbName,dbPassword=dbPassword,clientKey=clientKey,clientIP=clientIP)

        if passwordIsTrue == "systemError":
            return passwordIsTrue

        if passwordIsTrue == True:
            remove(folders.DB+clientKey+dbName+".db")
            self.LogPrint.info(f"[Info] <Database Deleted> : {dbName}",clientIP)
            return self.success_code
        else:
            self.LogPrint.info(f"[Info] <Database Deletion Attempt> : Incorrect password {dbPassword}",clientIP)
            return "incorrect password"
    
    def rescuekeyRead(self,dbName,dbPassword,clientKey,clientIP):
        error_Message = "key not found"

        checkingDB = databaseTools.checkingDB(dbName=dbName,clientKey=clientKey)

        if checkingDB == "systemError":
            return checkingDB

        if checkingDB[0] == False:
            return checkingDB[1]

        passwordIsTrue = databaseTools.passwordCheck(dbName=dbName,dbPassword=dbPassword,clientKey=clientKey,clientIP=clientIP)

        if passwordIsTrue == "systemError":
            return passwordIsTrue

        if passwordIsTrue == True:
            return {"rescuekey" : databaseTools.rescuekeyReader(dbName,clientKey)}
        else:
            self.LogPrint.info(f"[Info] <rescue key Could Not Be Read> : Incorrect password {dbPassword}",clientIP)
            return error_Message

    def NewDBPassword(self,dbName,dbRescueKey,dbNewPassword,clientKey,clientIP):
        def upgrade():
            DB_PasswordAlogrithm = cryptologyAlgorithm.UltraEncrypt(dbNewPassword[::3]*3)
            DB_Sec_Password = DB_PasswordAlogrithm.encrypt(dbNewPassword)

            try:
                connect = sqlite3.connect(folders.DB+clientKey+dbName+".db")
                cursor = connect.cursor()

                cursor.execute(self.sqliteScript["db-new-password"],(DB_Sec_Password, dbName))
                connect.commit()
                connect.close()
            except Exception as err:
                self.LogPrint.info(f"[Error] !From database.NewDBPassword <Database Error> : {err}",clientIP)
                return "systemError"

            return None

        checkingDB = databaseTools.checkingDB(dbName=dbName,clientKey=clientKey)

        if checkingDB == "systemError":
            return checkingDB

        if checkingDB[0] == False:
            return checkingDB[1]
        
        realKey = databaseTools.rescuekeyReader(dbName,clientKey)

        if realKey != dbRescueKey:
            self.LogPrint.error("[Error] <Client Error> : The client tried to change their password but entered the wrong key",clientIP)
            return "key is wrong"
        
        upgrade = upgrade()

        if upgrade != None:
            return upgrade

        self.LogPrint.info("[Info] <Client Event> : The client changed their password",clientIP)

        return self.success_code
    
    def rescuekey_get(self,dbName,dbPassword,clientKey,clientIP):
        checkingDB = databaseTools.checkingDB(dbName=dbName,clientKey=clientKey)

        if checkingDB == "systemError":
            return checkingDB

        if checkingDB[0] == False:
            return checkingDB[1]
        
        passwordIsTrue = databaseTools.passwordCheck(dbName=dbName,dbPassword=dbPassword,clientKey=clientKey,clientIP=clientIP)

        rescuekey = databaseTools.rescuekeyReader(dbName=dbName,clientKey=clientKey)

        if passwordIsTrue == "systemError":
            return passwordIsTrue
        
        if passwordIsTrue == True:
            self.LogPrint.info("[Info] <Client Event> : Client viewed rescuekey",ip=clientIP)
            return {"key" : rescuekey}
        else:
            return "incorrect password"
        

class userManager(databaseManager):
    def new(self,dbName,dbPassword,clientKey,clientIP,userDatas):
        checkingDB = databaseTools.checkingDB(dbName=dbName,clientKey=clientKey)

        if checkingDB == "systemError":
            return checkingDB

        if checkingDB[0] == False:
            return checkingDB[1]

        passwordIsTrue = databaseTools.passwordCheck(dbName=dbName,dbPassword=dbPassword,clientKey=clientKey,clientIP=clientIP)

        if passwordIsTrue == "systemError":
            return passwordIsTrue

        if passwordIsTrue == True:
            try:
                connect = databaseTools.UserDatabaseConnect(dbName=dbName,clientKey=clientKey,clientIP=clientIP)
                cursor = connect.cursor()

                if connect == "systemError":
                    return connect

                cursor.execute(self.sqliteScript["new-user"],(
                    userDatas["username"],
                    databaseTools.UserEncryptPassword(userDatas["password"]),
                    userDatas["realname"],
                    userDatas["email"],
                    userDatas["userdata"]
                ))
                connect.commit()
                connect.close()
            except Exception as err:
                self.LogPrint.error(f"[Error] !From database.userManager.new <Database Write Error> : {err}")
                return "systemError"

            return self.success_code
        else:
            self.LogPrint.error("[Error] <Client Error> : An incorrect username was entered",ip=clientIP)
            return "incorrect password"
    
    def userData_get(self,dbName,dbPassword,clientKey,clientIP,userName):
        checkingDB = databaseTools.checkingDB(dbName=dbName,clientKey=clientKey)

        if checkingDB == "systemError":
            return checkingDB

        if checkingDB[0] == False:
            return checkingDB[1]

        passwordIsTrue = databaseTools.passwordCheck(dbName=dbName,dbPassword=dbPassword,clientKey=clientKey,clientIP=clientIP)

        if passwordIsTrue == "systemError":
            return passwordIsTrue

        if passwordIsTrue == True:           
            try:
                connect = databaseTools.UserDatabaseConnect(dbName=dbName,clientKey=clientKey,clientIP=clientIP)
                cursor = connect.cursor()

                if connect == "systemError":
                    return connect

                cursor.execute(self.sqliteScript["user-datas-select"],(userName,))
                datas = cursor.fetchone()
                
                DATAS_AND_RESPONS = [self.success_code,{
                    "User Name" : userName,
                    "User Password" : datas[1]+" (User passwords cannot be viewed)",
                    "RealName" : datas[2],
                    "Email" : datas[3],
                    "User Data" : datas[4]
                }]
                connect.close()

                return DATAS_AND_RESPONS
            except Exception as err:
                self.LogPrint.error(f"[Error] !From database.userManager.userData_get <Database Read Error> : {err}")
                return "systemError"
        else:
            return "incorrect password"
        
    def User_columnQuery(self,dbName,dbPassword,clientKey,clientIP,columnName,value):
        checkingDB = databaseTools.checkingDB(dbName=dbName,clientKey=clientKey)

        if checkingDB == "systemError":
            return checkingDB

        if checkingDB[0] == False:
            return checkingDB[1]

        passwordIsTrue = databaseTools.passwordCheck(dbName=dbName,dbPassword=dbPassword,clientKey=clientKey,clientIP=clientIP)

        if passwordIsTrue == "systemError":
            return passwordIsTrue

        if passwordIsTrue == True:
            try:
                connect = databaseTools.UserDatabaseConnect(dbName=dbName,clientKey=clientKey,clientIP=clientIP)
                cursor = connect.cursor()

                if connect == "systemError":
                    return connect
                
                cursor.execute(f"SELECT EXISTS(SELECT 1 FROM users WHERE {columnName} = ?)",(value,))
                exists = cursor.fetchone()[0]
                exists = bool(exists)

                connect.close()
            except Exception as err:
                self.LogPrint.error(f"[Error] !From database.userManager.User_columnQuery <Database Select Error> : {err}")
                return "systemError"
            
            return [self.success_code,{
                "Exists" : exists
            }]
        else:
            return "incorrect password"
    
    def User_update(self,dbName,dbPassword,clientKey,clientIP,userName,columnName,Data):
        checkingDB = databaseTools.checkingDB(dbName=dbName,clientKey=clientKey)

        if checkingDB == "systemError":
            return checkingDB

        if checkingDB[0] == False:
            return checkingDB[1]

        passwordIsTrue = databaseTools.passwordCheck(dbName=dbName,dbPassword=dbPassword,clientKey=clientKey,clientIP=clientIP)

        if passwordIsTrue == "systemError":
            return passwordIsTrue

        if passwordIsTrue == True:            
            try:
                connect = databaseTools.UserDatabaseConnect(dbName=dbName,clientKey=clientKey,clientIP=clientIP)
                cursor = connect.cursor()

                if connect == "systemError":
                    return connect
                
                if columnName == "password":
                    passw = databaseTools.UserEncryptPassword(Data)
                    cursor.execute(f"UPDATE users SET {columnName} = ? WHERE username = ?",(passw, userName))
                else:
                    cursor.execute(f"UPDATE users SET {columnName} = ? WHERE username = ?",(Data, userName))
                connect.commit()

                connect.close()
            except Exception as err:
                self.LogPrint.error(f"[Error] !From database.userManager.User_update <Database Update Error> : {err}")
                return "systemError"
            
            return self.success_code
        else:
            return "incorrect password"
        
    def User_delete(self,dbName,dbPassword,clientKey,clientIP,userName):
        checkingDB = databaseTools.checkingDB(dbName=dbName,clientKey=clientKey)

        if checkingDB == "systemError":
            return checkingDB

        if checkingDB[0] == False:
            return checkingDB[1]

        passwordIsTrue = databaseTools.passwordCheck(dbName=dbName,dbPassword=dbPassword,clientKey=clientKey,clientIP=clientIP)

        if passwordIsTrue == "systemError":
            return passwordIsTrue
        
        isUser = self.User_columnQuery(
            dbName=dbName,
            dbPassword=dbPassword,
            clientKey=clientKey,
            clientIP=clientIP,
            columnName="username",
            value=userName
        )

        if isUser[1]["Exists"] == False:
            return "user not found"
        elif isUser == "systemError":
            return isUser

        if passwordIsTrue == True:
            try:
                connect = databaseTools.UserDatabaseConnect(dbName=dbName,clientKey=clientKey,clientIP=clientIP)
                cursor = connect.cursor()

                cursor.execute(self.sqliteScript["user-delete"],(userName,))
                connect.commit()

                connect.close()

                return self.success_code
            except Exception as err:
                self.LogPrint.error(f"[Error] !From database.userManager.User_delete <Database Delete Error> : {err}")
                return "systemError"
        else:
            return "incorrect password"


class ClientKeys(databaseManager):
    def __init__(self):
        self.DB_name = "ClientKeys.db"

        self.LogPrint = logManager.Log()

        try:
            connect = sqlite3.connect(self.DB_name)
            cursor = connect.cursor()

            cursor.execute(self.sqliteScript["New-ClientKey-DB"])

            connect.commit()
            connect.close()
        except Exception as err:
            self.LogPrint.error(f"[Error] !From database.ClientKeys.__init__ <Database Create Error> : {err}")

    def key_save(self,key,ip):
        try:
            connect = sqlite3.connect(self.DB_name)
            cursor = connect.cursor()

            cursor.execute(self.sqliteScript["Client-save"],(key,ip))

            connect.commit()
            connect.close()

            return self.success_code
        except Exception as err:
            self.LogPrint.error(f"[Error] !From database.ClientKeys.key_save <Database Insert Error> : {err}")
            return "systemError"

    def check_Key(self,key):
        try:
            connect = sqlite3.connect(self.DB_name)
            cursor = connect.cursor()

            cursor.execute(self.sqliteScript["check-key"],(key,))
            exists = cursor.fetchall()[0]
            exists = bool(exists)

            connect.close()

            return exists
        except Exception as err:
            self.LogPrint.error(f"[Error] !From database.ClientKeys.check_Key <Database SELECT Error> : {err}")
            return "systemError"
