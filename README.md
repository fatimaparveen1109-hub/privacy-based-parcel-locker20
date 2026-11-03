# Privacy-Based Automated Parcel Locker Delivery System

Student prototype using Streamlit + Supabase PostgreSQL.

## Included
- Public home page and role login/registration
- Customer catalogue, order placement, demo payment, pickup QR
- Seller product management and order view
- Rider privacy-restricted demonstration portal
- Admin overview, pending approvals, order/product tables
- PostgreSQL schema, 5 Karachi hubs and 8 locker compartments per hub
- Modular services package: auth, catalog, orders, lockers, payments, QR, admin, notifications, housekeeping
- Hardware API adapter placeholder and local SVG illustrations

## Supabase setup
1. Create a new Supabase project.
2. Open SQL Editor, create a new query, paste `schema.sql`, click Run.
3. In Supabase Project Settings, get the **PostgreSQL connection URI**. This is different from the Publishable/Secret API keys.
4. Keep your database password private.

## Streamlit Cloud
1. Upload the CONTENTS of this extracted folder to the root of a GitHub repository. Root must show `app.py`, `db.py`, `requirements.txt`, `schema.sql`, `services/`, `assets/`.
2. Streamlit Cloud: Create app → repository → branch `main` → main file `app.py` → Python 3.11.
3. App settings → Secrets: add the actual PostgreSQL connection URI:
```toml
DATABASE_URL = "postgresql://postgres:YOUR_DB_PASSWORD@db.YOUR_PROJECT_REF.supabase.co:5432/postgres?sslmode=require"
```
4. Reboot app. Never put real credentials in GitHub or chat.

## Admin account
Register a user first, then in Supabase SQL Editor run this for YOUR own account:
```sql
UPDATE users SET role='admin', status='active' WHERE email='YOUR_EMAIL';
```
Then log in again.

## Fees and prototype boundaries
Order total currently adds Rs. 30 rider fee + Rs. 60 locker fee.
Payments are simulated only. No real card/bank details or payment gateway.
QR is a generated demo token with a 48-hour expiry. Single-use scan validation and actual locker unlocking still require the partner hardware API.
Rider assignment, returns workflow, full messaging, production RLS and security audit are not complete. Do not use real customer data or expose publicly as a live service.
The SVGs are clean local illustrations, not real product photographs. Replace with licensed product photos when available.
