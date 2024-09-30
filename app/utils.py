from flask import current_app, jsonify
import cryptocode

class Page():
    def __init__(self,title,header) -> None:
        self.title = title
        self.header = header


def encode(text):
    return cryptocode.encrypt(text,current_app.config["SECRET_KEY"])

def decode(hash):
    return cryptocode.decrypt(hash,current_app.config["SECRET_KEY"])


def resp(status_code, message):    
    resp = jsonify({'message': message})
    resp.status_code = status_code
    return resp