from random import randint

def randomRK():
    key = ""
    charset = [[65, 90],[97, 122],[48, 57]]
    for i in range(40):
        randomCharset = randint(0,2)
        x = chr(randint(charset[randomCharset][0],charset[randomCharset][1]))
        key = key + x

    return key
