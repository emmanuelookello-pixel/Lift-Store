# Integration readiness

The store is currently a single-merchant storefront. Cash on delivery is the only enabled payment method.

## Payment provider boundary
Choose a provider supporting Uganda/UGX and the required MTN, Airtel and card networks. Do not enable a method just by changing the checkout option list. Implement the interface in payment_gateway.py with the selected provider's official SDK/API and sandbox credentials. Use hosted checkout so card numbers never pass through this application. Persist provider references and idempotency keys. Verify signed callbacks and independently verify the amount, currency and order reference before marking an order paid. A browser success redirect is not proof of payment. Add duplicate-event, declined-payment and refund tests before activation. Bank-transfer instructions require the store's verified bank details; none are invented here.

## Web Push
Optional transport follows https://github.com/web-push-libs/pywebpush . Install requirements-notifications.txt in the application's own environment, then configure VAPID_PUBLIC_KEY, VAPID_PRIVATE_KEY (private key file path), VAPID_SUBJECT (mailto contact). Serve the production site over HTTPS. The profile page then offers opt-in. Order status changes send to the customer's subscribed browsers; promotional alerts require a separate checkbox. The Flask send-promotion command sends an explicitly supplied offer to opted-in subscribers. No automatic daily promotion campaign is scheduled. Add a durable background queue and remove expired subscriptions before scaling. Live delivery is not tested until credentials and a subscribed device are available.

## Social sign-in and advanced services
Google/Apple sign-in still needs application registration, verified callback domains and provider-specific integration. AI semantic search and voice transcription are not connected to external services. The current search offers catalogue suggestions and local spelling suggestions. Carrier GPS/map tracking needs a courier/location source, customer-consent rules and map credentials. Current order tracking polls the store's own status every 15 seconds and shows admin-entered estimates.

## Remaining expanded features
The current product schema has flat categories. Nested category editing, product-condition metadata, scheduled flash-sale countdowns, multi-image/video/360 media management, customer review-photo uploads, gift-card and loyalty ledgers, wishlist price-drop delivery, and live agent chat are not implemented in this release. Tax settings and jurisdiction-specific invoice requirements need business input; order receipts are not tax invoices. Existing photos are shown at their supplied resolution. Seller marketplaces are out of scope for the chosen single-store setup.

## Database setup
Run flask --app app init-customer-features once. It only creates the six added tables if absent; existing customer, product and order data is retained. Back up the database before application updates. Customer support is available at /admin/support; customers submit questions, returns or disputes at /account/support.
