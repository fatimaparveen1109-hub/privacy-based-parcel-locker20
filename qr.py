import io,secrets,qrcode
from db import one,execute
def issue_token(order_id,customer_id):
    o=one("SELECT id,payment_status FROM orders WHERE id=%s AND customer_id=%s",(order_id,customer_id))
    if not o or o["payment_status"]!="paid": raise ValueError("Complete payment first.")
    old=one("SELECT token FROM qr_tokens WHERE order_id=%s AND used_at IS NULL AND expires_at>NOW()",(order_id,))
    if old: return old["token"]
    token=secrets.token_urlsafe(32)
    execute("INSERT INTO qr_tokens(order_id,token,expires_at) VALUES(%s,%s,NOW()+INTERVAL '48 hours')",(order_id,token))
    execute("UPDATE orders SET status='ready_for_pickup' WHERE id=%s",(order_id,))
    return token
def qr_png(token):
    b=io.BytesIO(); qrcode.make(token).save(b,format="PNG"); b.seek(0); return b
