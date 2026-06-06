from time import localtime

def date():
    T = localtime()
    X = f"{T.tm_year}-{T.tm_mon}-{T.tm_mday}_{T.tm_hour}:{T.tm_min}:{T.tm_sec}"
    return X
