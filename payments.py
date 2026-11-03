from db import one,execute
def simulate_payment(order_id,customer_id):
    o=one("SELECT id,total_pkr,payment_status FROM orders WHERE id=%s AND customer_id=%s",(order_id,customer_id))
    if not o: raise ValueError("Order not found.")
    execute("INSERT INTO payments(order_id,amount_pkr,status,provider_reference) VALUES(%s,%s,'success',%s)",(order_id,o["total_pkr"],"DEMO-"+str(order_id)))
    execute("UPDATE orders SET payment_status='paid',status='paid' WHERE id=%s",(order_id,))
    return True
