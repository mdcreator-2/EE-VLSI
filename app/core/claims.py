from firebase_admin import auth
from app.core.rbac import Role
def set_user_role(uid: str, role: Role):
    auth.set_custom_user_claims(uid, {"role": role.value})
    return Role(role.value)

def get_user_claims(uid: str):
    user = auth.get_user(uid)
    return user.custom_claims
