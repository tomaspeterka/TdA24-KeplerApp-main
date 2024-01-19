import datetime

def init():
    with open("log", "w") as f:
        f.write(str(datetime.datetime.now()) + "<br>")

def log(text):
    with open("log", "a") as f:
        f.write(text + "<br>")

def get():
    with open("log", "r") as f:
        return f.read()