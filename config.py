import os

class Config:
    
    SQLALCHEMY_DATABASE_URI = 'sqlite:////opt/stp/mydatabase.db'
    
    # ## for PostgreSQL 
    # DATABASE_HOST = 'hostname'
    # DATABASE_PORT = '5432'
    # DATABASE_USERNAME = 'username'
    # DATABASE_NAME = 'dbname'
    # DATABASE_PASSWORD = 'password'

    # # Postgresql URI
    # SQLALCHEMY_DATABASE_URI = (
    #     'postgresql://' + DATABASE_USERNAME+':'+ DATABASE_PASSWORD + '@' +
    #     DATABASE_HOST + ':' + DATABASE_PORT + '/' +
    #     DATABASE_NAME
    #     # 'sqlite:///db.sqlite'

    # )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'your_secret_key'
    DEBUG = True
    SQLALCHEMY_ECHO = False  
    
    #session configirations
    SESSION_TYPE = 'sqlalchemy'
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    
    # ##Email config
    # MAIL_SERVER='localhost'
    # MAIL_PORT=25
    # MAIL_USE_TLS=True
    # MAIL_USERNAME=''
    # MAIL_PASSWORD=''
    # MAIL_DEFAULT_SENDER=('Sender Display Name','automation-bot@local')
    # MAIL_DEBUG = False

    #Request & Response data & Header
    MAX_CONTENT_LENGTH = 1024 * 1024 * 1024

class Branding():
    NAME = "Automation Portal"
    OWNER = "Vikas Bhandare"
    OWNER_SITE = "https://vikasbhandare.in"
    
    
