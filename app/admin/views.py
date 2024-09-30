from flask import Blueprint, render_template, request
from flask_login import login_required
from ..utils import Page, resp
from ..main.utils import roles_required
from ..schema.users import Users, Roles
from ..schema.utils import db
import json

admin = Blueprint('admin', __name__,template_folder='templates')

@admin.route('/')
@login_required
def admin_home():
    page = Page("Admin Home", "Admin's Home")
    return render_template('admin_home.html', page=page)


#### privilaged tasks

@admin.route('/users')
@roles_required('ADMIN')
@login_required
def get_users():
    userList = Users.query.all()
    return render_template('users.html',data=userList)

@admin.route('/enable_user',methods=['POST'])
def enable_user():
    try:
        rData =  json.loads(request.data)
        user = Users.query.filter_by(username=rData['username']).first()
        
        if user:        
            user.enable(rData['state'])
            return resp(200,"User Updated")
        else:
            return resp(404,"User Not Found")
    
    except Exception as e:
        return resp(500,"Something Went Wrong")    
    
    


@admin.route('/get_user/<string:username>', methods=['GET','POST','DELETE'])
@roles_required('ADMIN')
@login_required
def get_user_details(username):
    try:
        if request.method == 'GET':
            roles = Roles.query.all()
            User = Users.query.filter_by(username=username).first()
            return render_template('userinfo_modal.html',user=User,roles=roles)
        elif request.method == 'POST':
            user = Users.query.filter_by(username=username).first()
            rData = json.loads(request.data)
           
            if rData:
                for role in rData:
                    user.add_role(role)
                db.session.merge(user)
                db.session.commit()
                return resp(200,"Added "+json.dumps(rData))
        elif request.method == 'DELETE':
            print("starting delete")
            user = Users.query.filter_by(username=username).first()
            rData = json.loads(request.data)
            
            if rData:              
                user.remove_role(rData["name"])
                db.session.merge(user)
                db.session.commit()
                
                return resp(200,"Deleted "+json.dumps(rData))
        
    except Exception as e:

        print(e)
        raise e
    
@admin.route('/roles', methods=['GET','POST','DELETE'])
@roles_required('ADMIN')
@login_required
def get_user_roles():
    if request.method == 'GET':
        roleList = Roles.query.all()
        return render_template('roles.html',data=roleList)
    elif request.method == 'POST':
        
        data = json.loads(request.data)
        
        if Roles.query.filter_by(name=data['role'].upper()).all():
            return resp(409,"Role already exists")
        else:
            role = Roles()
            role.name = data['role'].upper()
            role.description = data['description']
            db.session.add(role)
            db.session.commit()
            return resp(200,"Role added successfully.")
    elif request.method == 'DELETE':
        data = json.loads(request.data)

        
        role = Roles.query.filter_by(name=data['name'].upper()).first()        
        if role:
            db.session.delete(role)
            db.session.commit()
            return resp(200,"Role deleted successfully.")
        else:
            return resp(404,"Role Not Found")