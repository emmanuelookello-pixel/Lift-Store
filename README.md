# Lift Store

A complete starter e-commerce website built with Flask, SQLite, HTML and CSS.
The visual identity uses blue and white and the storefront is localized for Lira City, Uganda.

## Features
- Responsive storefront
- Search and category filters
- Product detail pages
- Shopping cart with quantity updates
- Checkout and order storage
- Customer registration/login
- Demo admin product management
- UGX pricing
- Lira City delivery messaging
- SQLite database seeded with sample products

## Run it

1. Install Python 3.
2. Open a terminal in this folder.
3. Create a virtual environment:

   python -m venv venv

4. Activate it:
   Windows: venv\Scripts\activate
   macOS/Linux: source venv/bin/activate

5. Install packages:

   pip install -r requirements.txt

6. Start the site:

   python app.py

7. Open http://127.0.0.1:5000 in your browser.

## Important before publishing
This is a functional starter/demo, not a production payment platform.
Before going live, change the SECRET_KEY, protect /admin with role-based authentication,
add CSRF protection, validate all inputs, configure a production database, HTTPS,
payment provider integration, delivery pricing, inventory controls, email/SMS notifications,
and proper product photographs.
