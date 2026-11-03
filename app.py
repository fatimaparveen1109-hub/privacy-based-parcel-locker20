import streamlit as st
from pathlib import Path
from db import db_ready
from services.auth import register_user, login
from services.catalog import products, add_product
from services.orders import place_order, customer_orders, seller_orders
from services.lockers import hubs
from services.payments import simulate_payment
from services.qr import issue_token, qr_png
from services.admin import counts, pending_users, approve, orders, product_list
from services.notifications import get_notifications

st.set_page_config(page_title="Privacy Parcel Locker", page_icon="🔐", layout="wide")
A=Path(__file__).parent/"assets"
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
html,body,[class*="css"]{font-family:Inter,sans-serif}.block-container{max-width:1300px;padding-top:1.4rem}
.hero{background:linear-gradient(115deg,#eff6ff,#fff 58%,#ecfeff);padding:2rem;border-radius:24px;border:1px solid #dbeafe}
.tile{background:white;border:1px solid #e2e8f0;border-radius:18px;padding:16px}.role{padding:16px;border-radius:15px;color:white;font-weight:700;text-align:center}
</style>""",unsafe_allow_html=True)

def landing():
    st.markdown('<div class="hero">',unsafe_allow_html=True)
    l,r=st.columns([1.1,1])
    with l:
        st.caption("PRIVACY-FIRST SMART DELIVERY")
        st.title("Secure. Smart. Private.")
        st.write("Safe, contactless parcel delivery through approved collection hubs.")
        if st.button("Get Started →",type="primary"): st.session_state.page="auth"; st.rerun()
    with r: st.image(str(A/"hero_locker.svg"),use_container_width=True)
    st.markdown("</div>",unsafe_allow_html=True)
    st.subheader("How it works")
    cols=st.columns(5)
    for c,(n,t) in zip(cols,[("01","Shop"),("02","Choose hub"),("03","Demo payment"),("04","Get QR"),("05","Collect")]):
        c.markdown(f'<div class="tile"><h2>{n}</h2><b>{t}</b></div>',unsafe_allow_html=True)
    st.subheader("Privacy features")
    st.write("🛡️ Restricted customer details  ·  ▦ Single-use QR  ·  📍 Approved collection hubs")
    st.subheader("Choose your role")
    cols=st.columns(4)
    for c,(role,color) in zip(cols,[("Customer","#2563eb"),("Seller","#0d9488"),("Rider","#7c3aed"),("Admin","#0f172a")]):
        c.markdown(f'<div class="role" style="background:{color}">{role}</div>',unsafe_allow_html=True)
        if c.button(role+" Login",key=role):
            st.session_state.role_hint=role.lower(); st.session_state.page="auth"; st.rerun()
    st.caption("Privacy Policy · How it works · Contact | Demo prototype only")

def auth_page():
    st.title("Privacy Parcel Locker")
    a,b=st.tabs(["Login","Create account"])
    with a:
        with st.form("login"):
            email=st.text_input("Email"); pw=st.text_input("Password",type="password")
            go=st.form_submit_button("Login")
        if go:
            try:
                u=login(email,pw)
                if u: st.session_state.user=u; st.rerun()
                else: st.error("Incorrect login or account is pending.")
            except Exception as e: st.error(str(e))
    with b:
        with st.form("register"):
            name=st.text_input("Full name / Store name"); email=st.text_input("Email")
            role=st.selectbox("Account type",["customer","seller","rider"])
            pw=st.text_input("Password (10+ characters)",type="password")
            confirm=st.text_input("Confirm password",type="password")
            go=st.form_submit_button("Register")
        if go:
            if pw!=confirm: st.error("Passwords do not match.")
            else:
                try: register_user(name,email,pw,role); st.success("Account created. Seller/rider need admin approval.")
                except Exception as e: st.error(str(e))
    st.info("Admin account is created through the SQL instruction in README.")

def customer(u):
    page=st.sidebar.radio("Customer menu",["Dashboard","Shop products","My orders","Notifications","Help & privacy"])
    if page=="Dashboard":
        rows=customer_orders(u["id"]); st.title("Customer dashboard"); st.metric("Orders",len(rows)); st.dataframe(rows,use_container_width=True)
    elif page=="Shop products":
        st.title("Product catalogue"); ps=products(); cart={}; cols=st.columns(4)
        for i,p in enumerate(ps):
            with cols[i%4]:
                st.image(str(A/p["image_file"]),use_container_width=True)
                st.markdown("**"+p["name"]+"**"); st.caption(p["seller_name"]+" · "+p["parcel_size"])
                st.write(f"Rs. {p['price_pkr']:,}")
                q=st.number_input("Quantity",0,10,0,key=f"q{p['id']}")
                if q: cart[str(p["id"])]=q
        hs=hubs()
        if hs:
            opts={h["name"]:h["id"] for h in hs}
            with st.form("place"):
                preferred=st.selectbox("Preferred hub",list(opts))
                alt=st.selectbox("Alternative hub (optional)",["None"]+list(opts))
                allow=st.checkbox("I explicitly allow alternative hub")
                go=st.form_submit_button("Place order",type="primary")
            if go:
                try: oid=place_order(u["id"],cart,opts[preferred],opts.get(alt),allow); st.success(f"Order #{oid} created.")
                except Exception as e: st.error(str(e))
        else: st.warning("No hubs configured. Run schema.sql.")
    elif page=="My orders":
        st.title("My orders")
        for o in customer_orders(u["id"]):
            with st.expander(f"Order #{o['id']} · {o['status']} · Rs. {o['total_pkr']}"):
                st.write("Payment:",o["payment_status"])
                if o["payment_status"]!="paid" and st.button("Complete demo payment",key=f"pay{o['id']}"):
                    try: simulate_payment(o["id"],u["id"]); st.success("Demo payment complete."); st.rerun()
                    except Exception as e: st.error(str(e))
                if o["payment_status"]=="paid" and st.button("Generate pickup QR",key=f"qr{o['id']}"):
                    try: st.session_state[f"token{o['id']}"]=issue_token(o["id"],u["id"]); st.rerun()
                    except Exception as e: st.error(str(e))
                token=st.session_state.get(f"token{o['id']}")
                if token: st.image(qr_png(token),width=220); st.code(token); st.caption("Single-use demo QR, valid for 48 hours.")
    elif page=="Notifications":
        st.title("Notifications")
        for n in get_notifications(u["id"]): st.write("• "+n["message"])
    else:
        st.title("Help & privacy")
        st.write("Seller and rider views do not display customer home address or phone number.")
        st.warning("Physical locker unlock is simulated until partner hardware API is provided.")

def seller(u):
    page=st.sidebar.radio("Seller menu",["Dashboard","Products","Notifications"])
    if page=="Dashboard": st.title("Seller dashboard"); st.dataframe(seller_orders(u["id"]),use_container_width=True)
    elif page=="Products":
        st.title("Add product")
        with st.form("product"):
            name=st.text_input("Product name"); desc=st.text_area("Description")
            price=st.number_input("Price PKR",min_value=1); stock=st.number_input("Stock",min_value=0)
            size=st.selectbox("Parcel size",["Small","Medium","Large"])
            image=st.selectbox("Image",["earbuds.svg","smartwatch.svg","backpack.svg","sunglasses.svg","shoes.svg","shirt.svg","hoodie.svg","cap.svg"])
            go=st.form_submit_button("Save product")
        if go:
            try: add_product(u["id"],name,desc,price,stock,size,image); st.success("Product saved.")
            except Exception as e: st.error(str(e))
        st.dataframe(seller_orders(u["id"]),use_container_width=True)
    else:
        for n in get_notifications(u["id"]): st.write(n["message"])

def rider(u):
    st.title("Rider portal")
    st.info("Privacy restriction: rider sees delivery/hub information only, not customer address, phone or product details.")
    st.write("Delivery assignment view is a demonstration placeholder.")

def admin(u):
    page=st.sidebar.radio("Admin menu",["Overview","Approvals","Orders & products","System"])
    if page=="Overview":
        st.title("Admin dashboard")
        try:
            data=counts(); cs=st.columns(len(data))
            for c,(k,v) in zip(cs,data.items()): c.metric(k.title(),v)
        except Exception as e: st.error(str(e))
    elif page=="Approvals":
        st.title("Pending accounts")
        for x in pending_users():
            a,b=st.columns([4,1]); a.write(f"{x['name']} · {x['email']} · {x['role']}")
            if b.button("Approve",key=f"ap{x['id']}"): approve(x["id"]); st.rerun()
    elif page=="Orders & products":
        st.title("Orders"); st.dataframe(orders(),use_container_width=True)
        st.subheader("Products"); st.dataframe(product_list(),use_container_width=True)
    else:
        ok,msg=db_ready(); st.write("Database connected" if ok else "Database not connected")
        if not ok: st.code(msg)

def main():
    if "page" not in st.session_state: st.session_state.page="home"
    if st.sidebar.button("Home"): st.session_state.clear(); st.session_state.page="home"; st.rerun()
    if "user" not in st.session_state:
        auth_page() if st.session_state.page=="auth" else landing()
    else:
        u=st.session_state.user
        if st.sidebar.button("Logout"): st.session_state.clear(); st.rerun()
        {"customer":customer,"seller":seller,"rider":rider,"admin":admin}.get(u["role"],landing)(u)
main()
