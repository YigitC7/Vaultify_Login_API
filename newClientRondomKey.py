from random import randint
from database import ClientKeys

def key():
    randomSTR = ""
    key = ""

    charset = [[65, 90],[97, 122],[48, 57]]

    while True:
        key = ""
        
        for i in range(3):
            if i > 0:
                key = key + "_"

            for i in range(8):
                randomCharset = randint(0,2)
                x = chr(randint(charset[randomCharset][0],charset[randomCharset][1]))
                randomSTR = randomSTR + x

            key = key + randomSTR
        """
        databases = ClientKeys().check_Key(key)

        if not (databases == True):
        """
        return key
        