from flask_login import current_user
from flask import jsonify
from functools import wraps

def roles_required(*roles):
    def wrapper(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if current_user.is_authenticated:
                authorised = True
                if roles and not current_user.is_locked:
                    for role in roles:
                        if isinstance(role, (list, tuple)):
                            authorised = False
                            for auth_role in role:
                                if current_user.has_role(auth_role):
                                    authorised = True
                                    break
                        else:
                            if not current_user.has_role(role):
                                authorised = False
                else:
                    authorised = False            
            else:
                message = {'message': "Unauthorised access"}
                resp = jsonify(message)
                resp.status_code = 401
                return resp

            if not authorised:
                message = {'message': "Unauthorised access"}
                resp = jsonify(message)
                resp.status_code = 401
                return resp

            return f(*args, **kwargs)
        return decorated
    return wrapper