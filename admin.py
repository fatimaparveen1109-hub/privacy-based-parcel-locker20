from db import query,execute
def counts(): return {t:query(f"SELECT COUNT(*) n FROM {t}")[0]["n"] for t in ["users","products","orders","hubs","lockers"]}
def pending_users(): return query("SELECT id,name,email,role FROM users WHERE status='pending' ORDER BY id")
def approve(uid): execute("UPDATE users SET status='active' WHERE id=%s",(uid,))
def orders(): return query("SELECT id,customer_id,status,total_pkr,payment_status,created_at FROM orders ORDER BY id DESC LIMIT 200")
def product_list(): return query("SELECT id,name,price_pkr,stock_qty,is_active FROM products ORDER BY id")
