from flask import Flask
from os import path
from .functions import model_load


from .views import views
from .auth import auth

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'gizli'
    
    if functions.model ==None:
        print("yüklenmemiş")
    else:
        print("Modeller yüklendi.")

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    return app