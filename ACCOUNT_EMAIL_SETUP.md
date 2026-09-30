# Gmail setup for Listo

Intended sender: emmanuelookello@gmail.com. Delivery remains disabled; no live message has been sent.

Set these environment variables privately on the server running Flask:

- SMTP_HOST=smtp.gmail.com
- SMTP_PORT=587
- SMTP_FROM=emmanuelookello@gmail.com
- SMTP_USERNAME=emmanuelookello@gmail.com
- SMTP_PASSWORD: your Gmail app password (never paste it into chat or source code)
- STORE_PUBLIC_URL: your real public HTTPS store address

Restart the app after configuration. The localhost address is not accessible to customers on other devices. Test verification and recovery with an account you control before activation.

Google documents STARTTLS port 587 and app-password use at https://support.google.com/mail/answer/7104828 . Do not use your ordinary Gmail password.

Included: email verification, email recovery, hashed single-use tokens with 30-minute expiry, request limits, CSRF protection, email-change invalidation and customer-session revocation after reset. Verification is optional and does not block checkout. Phone-only accounts must first add an email while signed in. SMS recovery, administrator 2FA and staff roles are upcoming work.

Database setup: flask --app app init-account-security
Admin status page: /admin/account-security
