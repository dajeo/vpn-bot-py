from configparser import ConfigParser

config = ConfigParser()


def init(filename: str):
    try:
        config.read(filename)
    except Exception as err:
        print("Error while reading config:", err)


def get():
    return config
