from db import query,one,execute
def products():
    return query("""SELECT p.id,p.name,p.description,p.price_pkr,p.stock_qty,p.parcel_size,p.image_file,
    COALESCE(s.store_name,'Seller') seller_name FROM products p LEFT JOIN sellers s ON s.id=p.seller_id
    WHERE p.is_active=TRUE AND p.stock_qty>0 ORDER BY p.id""")
def add_product(user_id,name,desc,price,stock,size,image):
    s=one("SELECT id FROM sellers WHERE user_id=%s",(user_id,))
    if not s: raise ValueError("Seller profile not found.")
    return execute("""INSERT INTO products(seller_id,name,description,price_pkr,stock_qty,parcel_size,image_file)
    VALUES(%s,%s,%s,%s,%s,%s,%s) RETURNING id""",(s["id"],name,desc,price,stock,size,image),True)
