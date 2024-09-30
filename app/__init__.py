from flask import Flask, g, session
from flask_login import LoginManager
from .schema.utils import db
from config import Config, Branding
from .prereqs import prereqs
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
import logging
from .logger import IPAddressFilter, load_logging

login_manager = LoginManager()
logging.getLogger().addFilter(IPAddressFilter)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['SESSION_SQLALCHEMY'] = db
    
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'
    load_logging()
    db.init_app(app)
    Session(app)
    
    from .main.views import main
    from .admin.views import admin
    from .workflows.views import workflows
    from .vmware.views import vmware
    
    app.register_blueprint(main)
    app.register_blueprint(admin, url_prefix='/admin')
    app.register_blueprint(workflows,url_prefix='/workflows')
    app.register_blueprint(vmware,url_prefix='/vmware')
    

    with app.app_context():
        db.create_all()
        prereqs()
        
        
    @app.before_request
    def before_request():
        g.name = Branding.NAME
        g.owner = Branding.OWNER
        g.owner_site = Branding.OWNER_SITE
    return app
