from passlib.hash import pbkdf2_sha256
from db import one, execute
def register_user(name,email,password,role):
    if len(password)<10: raise ValueError("Password must contain at least 10 characters.")
    if role not in ("customer","seller","rider"): raise ValueError("Invalid role.")
    if one("SELECT id FROM users WHERE lower(email)=lower(%s)",(email,)): raise ValueError("Email already exists.")
    status="active" if role=="customer" else "pending"
    u=execute("INSERT INTO users(name,email,password_hash,role,status) VALUES(%s,%s,%s,%s,%s) RETURNING id",(name,email.lower(),pbkdf2_sha256.hash(password),role,status),True)
    if role=="seller": execute("INSERT INTO sellers(user_id,store_name) VALUES(%s,%s)",(u["id"],name))
    if role=="rider": execute("INSERT INTO riders(user_id) VALUES(%s)",(u["id"],))
    return u["id"]
def login(email,password):
    u=one("SELECT id,name,email,password_hash,role,status FROM users WHERE lower(email)=lower(%s)",(email.lower(),))
    if not u or u["status"]!="active" or not pbkdf2_sha256.verify(password,u["password_hash"]): return None
    return {"id":u["id"],"name":u["name"],"email":u["email"],"role":u["role"]}
