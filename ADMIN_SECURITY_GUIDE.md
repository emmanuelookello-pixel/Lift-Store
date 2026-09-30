# Admin two-factor authentication and staff permissions

Open /admin/security to start authenticator setup. Enter your current admin password, add the displayed setup key to a time-based authenticator, then confirm a six-digit code. Protection stays off until confirmation succeeds. Eight recovery codes appear once; save them privately. Each recovery code can be used once. Do not share setup keys, passwords or recovery codes in chat.

Staff roles are managed at /admin/staff. The existing administrator remains Owner. Managers handle catalogue/sales; Inventory staff handle products and stock; Support staff can view orders/reviews and manage support requests. Only Owners manage roles or add staff. Changing permissions invalidates that staff member's sessions. An owner cannot demote or disable their own account.

The old development session-signing key has been replaced by a random local key when SECRET_KEY is not configured. Existing sessions will need one new sign-in. Keep instance/session-signing.key private and back it up with the application. MFA setup creates instance/admin-mfa.key unless ADMIN_MFA_KEY is provided by the server environment. Back up the MFA encryption key alongside the database; encrypted authenticator secrets cannot be recovered without it. Do not commit either key or the instance database to Git.

Two-factor authentication follows the time-based standard https://www.rfc-editor.org/rfc/rfc6238 . Secrets are encrypted with Fernet: https://cryptography.io/en/latest/fernet/ . Keep the server clock synchronized. Codes use 30-second periods; successful codes cannot be reused. Five failed code attempts trigger a five-minute pause. Password sign-in attempts also have a per-address limit.

Installation creates three new tables via flask --app app init-admin-security. cryptography is required for authenticator setup. Existing passwords, products and orders are retained. No real staff account was added and no user's two-factor protection was activated during testing.
