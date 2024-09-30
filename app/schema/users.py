from .utils import db
from sqlalchemy import Column, Integer, String, Boolean, DateTime, LargeBinary, Table
from flask_security import UserMixin, RoleMixin
import datetime

# Many-to-many relationship table between users and roles
roles_users = Table(
    'roles_users', 
    db.metadata,  # Add this line
    db.Column('user_id', db.Integer(), db.ForeignKey('users.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('roles.id'))
)



class Roles(db.Model, RoleMixin):
    __tablename__ = 'roles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String, unique=True)
    description = db.Column(db.String)

    def __str__(self):
        return self.name
    
# # Create the session model with extend_existing=True
# class SessionModel(db.Model):
#     __tablename__ = 'sessions'
#     __table_args__ = {'extend_existing': True}  # Prevent table redefinition error
#     id = db.Column(db.String(255), primary_key=True)  # Session ID
#     data = db.Column(db.LargeBinary)  # Session data
#     expiry = db.Column(db.DateTime)  # Session expiry
    
class Users(db.Model, UserMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    surname = Column(String)
    username = Column(String, unique=True)
    password = Column(String)
    email = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    is_admin = Column(Boolean, default=False)
    team = Column(String)
    
    failed_login_attempts = Column(Integer, default=0)
    is_locked = Column(Boolean, default=False)
    is_enabled = Column(Boolean, default=False)
    last_active = Column(DateTime, nullable=True)
    contact = Column(String)
    image = Column(LargeBinary)
    roles = db.relationship('Roles', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'), cascade='delete')
    token1 = Column(String, nullable=True)
    token1_expiry = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def enable(self, enabled):
        if Users.query.filter_by(username=self.username).first():
            self.is_enabled = enabled
            db.session.merge(self)
            db.session.commit()
        else:
            raise Exception

    def add_role(self, role_name):
        """Adding role to user"""
        try:
            role = Roles.query.filter_by(name=role_name).first()
            self.roles.append(role)
            return True
        except Exception as e:
            print(e)
            raise

    def remove_role(self, role_name):
        """Remove role from user"""
        try:
            role = Roles.query.filter_by(name=role_name).first()
            self.roles.remove(role)
            return True
        except Exception as e:
            print(e)
            raise

