from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, UserMixin
from app import login_manager
from config import Branding
from flask_security import current_user
from ..schema.users import Users
from ..schema.utils import db
from ..utils import Page

workflows = Blueprint('workflows', __name__,
                 template_folder='templates',
                 static_folder='static',
                 static_url_path='/static/workflows')

@workflows.route('/')
def workflow():
    page = Page("Workflows","Workflow's Home")
    return render_template('wf_home.html',page=page)