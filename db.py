import os, streamlit as st, psycopg2
from psycopg2.extras import RealDictCursor
def database_url():
    try: return st.secrets.get("DATABASE_URL",os.getenv("DATABASE_URL",""))
    except Exception: return os.getenv("DATABASE_URL","")
def get_conn():
    url=database_url()
    if not url: raise RuntimeError("DATABASE_URL missing. Follow README.")
    return psycopg2.connect(url,sslmode="require")
def db_ready():
    try:
        with get_conn() as c:
            with c.cursor() as q: q.execute("SELECT 1")
        return True,"Connected"
    except Exception as e: return False,str(e)
def query(sql,p=None):
    with get_conn() as c:
        with c.cursor(cursor_factory=RealDictCursor) as q:
            q.execute(sql,p or ()); return [dict(x) for x in q.fetchall()]
def one(sql,p=None):
    r=query(sql,p); return r[0] if r else None
def execute(sql,p=None,returning=False):
    with get_conn() as c:
        with c.cursor(cursor_factory=RealDictCursor) as q:
            q.execute(sql,p or ()); out=dict(q.fetchone()) if returning and q.description else None
        c.commit(); return out
