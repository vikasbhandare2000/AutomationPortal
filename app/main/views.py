from flask import Blueprint, render_template, redirect, url_for, flash, request,session
from flask_login import login_user, logout_user, login_required, UserMixin
from app import login_manager
from config import Branding
from flask_security import current_user
from ..schema.users import Users
from ..schema.utils import db
from ..utils import Page, decode, resp, encode
import json 

main = Blueprint('main', __name__,
                 template_folder='templates',
                 static_folder='static',
                 static_url_path='/static/admin')

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Users, user_id)

@main.route('/')
@login_required
def home():
    if current_user.has_role('ADMIN'):
        return redirect(url_for('admin.admin_home'))
    page = Page('User home','Home')
    return render_template('base.html', page=page)



@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))  # Ensure 'main.home' is in quotes

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = Users.query.filter_by(username=username).first()

        if user and password == decode(user.password):
            if not user.is_enabled:
                flash('Your Account is disabled. Please contact Administrator', 'danger')
                return render_template('login.html')
            
            login_user(user)
            session['user_id'] = user.id
            flash('Login successful!', 'success')
            return redirect(url_for('main.home'))
        else:
            flash('Invalid username or password', 'danger')

    return render_template('login.html')


@main.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()  # Clear session
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.login'))


@main.route('/register', methods=['POST'])
def register():
    rData = json.loads(request.data)
    try:
        user = Users.query.filter_by(username=rData['username']).first()
        
        if user:
            return resp('403', 'User ('+user.name+' '+user.surname+') with username '+rData['username']+' already exists.Please verify or use different Username')
        else:
            user = Users()
            user.name = rData['name']
            user.surname = rData['surname']
            user.username = rData['username']
            user.password = encode(rData['password'])
            user.email = rData['email']
            user.is_locked = False
            user.is_admin = False
            user.add_role('USER')
            db.session.add(user)
            db.session.commit()
            user.enable(False)
            
            return resp('200', 'You are registered succefully. Please ask admin to enable your userid with username '+rData['username'])
            
    except Exception as e:
        print(e)
        return resp('500', 'Something went wrong while registering User')
        
    
    
    
