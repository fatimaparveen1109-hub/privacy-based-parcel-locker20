from db import query
def get_notifications(uid): return query("SELECT id,message,created_at FROM notifications WHERE user_id=%s ORDER BY id DESC LIMIT 50",(uid,))
