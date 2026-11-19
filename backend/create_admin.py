"""
Create (or reset) an admin account from the command line.

    venv\\Scripts\\python create_admin.py --email admin@adspire.app --password "Admin@12345" --name "Adspire Admin"

If the email already exists, the account is promoted to admin, re-enabled and its password reset.
Campaigns created before accounts existed (no owner) are assigned to this admin.
"""
import argparse
import sys

from dotenv import load_dotenv

load_dotenv()

from services import database_service as db  # noqa: E402
from services.auth_service import hash_password  # noqa: E402

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Create or reset an Adspire admin account.")
    ap.add_argument("--email", required=True)
    ap.add_argument("--password", required=True)
    ap.add_argument("--name", default="Adspire Admin")
    a = ap.parse_args()

    email = a.email.strip().lower()
    if len(a.password) < 8:
        sys.exit("Password must be at least 8 characters.")

    user = db.get_user_by_email(email)
    if user:
        db.update_user(user.id, role="admin", is_active=True, password_hash=hash_password(a.password))
        print(f"Updated existing account {email}: admin, active, password reset.")
    else:
        user = db.create_user(name=a.name, email=email, password_hash=hash_password(a.password), role="admin")
        print(f"Created admin account {email}.")

    claimed = db.claim_orphan_campaigns(user.id)
    if claimed:
        print(f"Assigned {claimed} unowned campaigns to this admin.")
