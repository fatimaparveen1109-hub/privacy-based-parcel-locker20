from db import query,one,execute
def place_order(customer_id,cart,hub_id,alt_id=None,allow=False):
    if not cart: raise ValueError("Cart is empty.")
    total=90
    for pid,qty in cart.items():
        p=one("SELECT id,price_pkr,stock_qty,seller_id FROM products WHERE id=%s AND is_active=TRUE",(int(pid),))
        if not p or int(qty)<1 or p["stock_qty"]<int(qty): raise ValueError("Product unavailable or stock insufficient.")
        total+=p["price_pkr"]*int(qty)
    o=execute("""INSERT INTO orders(customer_id,preferred_hub_id,alternative_hub_id,allow_alternative,total_pkr,status,payment_status)
    VALUES(%s,%s,%s,%s,%s,'placed','pending') RETURNING id""",(customer_id,hub_id,alt_id,bool(allow),total),True)
    for pid,qty in cart.items():
        p=one("SELECT seller_id,price_pkr FROM products WHERE id=%s",(int(pid),))
        execute("INSERT INTO order_items(order_id,product_id,seller_id,quantity,unit_price_pkr) VALUES(%s,%s,%s,%s,%s)",(o["id"],int(pid),p["seller_id"],int(qty),p["price_pkr"]))
        execute("UPDATE products SET stock_qty=stock_qty-%s WHERE id=%s",(int(qty),int(pid)))
    return o["id"]
def customer_orders(uid):
    return query("""SELECT o.id,o.status,o.total_pkr,o.payment_status,o.created_at FROM orders o
    WHERE o.customer_id=%s ORDER BY o.id DESC""",(uid,))
def seller_orders(uid):
    return query("""SELECT DISTINCT o.id,o.status,o.total_pkr,o.created_at FROM orders o
    JOIN order_items i ON i.order_id=o.id JOIN sellers s ON s.id=i.seller_id
    WHERE s.user_id=%s ORDER BY o.id DESC""",(uid,))
