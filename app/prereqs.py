from .schema.utils import db
from .schema.users import Roles, Users
from .utils import encode

def prereqs():
    # Create 'SUPERADMIN' Role if not present 
    roles = [
            ("ADMIN","Admin Role"),
            ("USER","Generic User Role"),
            ("VMWARE","VMware User Role")
        ]
    
    for r in roles:
        if not Roles.query.filter_by(name=r[0]).first():
            role = Roles()
            role.name = r[0]
            role.description = r[1]
            db.session.add(role)
            db.session.commit()
            
    #Create admin User if not present 
    if not Users.query.filter_by(username='root').first():
        roles = Roles.query.all()
        user = Users()
        user.name = 'Root'
        user.username = 'root'
        user.password = encode('H0tD0g55!')
        user.email = 'root@local'
        user.is_locked = False
        user.is_admin = True
        user.login_method = 'local'
        for role in roles:
            user.add_role(role.name)
        db.session.add(user)
        db.session.commit()
        user.enable(True)