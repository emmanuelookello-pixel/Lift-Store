from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
)

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect

from werkzeug.security import (
    generate_password_hash,
    check_password_hash,
)

from werkzeug.utils import secure_filename

from datetime import datetime

import os
import uuid


# ==================================================
# APPLICATION CONFIGURATION
# ==================================================

app = Flask(__name__)

def store_session_key():
    configured=os.environ.get('SECRET_KEY')
    if configured: return configured
    import secrets
    os.makedirs(app.instance_path,exist_ok=True)
    path=os.path.join(app.instance_path,'session-signing.key')
    try:
        with open(path,'x',encoding='ascii') as key_file:key_file.write(secrets.token_hex(32))
    except FileExistsError:pass
    with open(path,encoding='ascii') as key_file:return key_file.read().strip()

app.config['SECRET_KEY']=store_session_key()

DATA_DIR = os.environ.get("DATA_DIR")

if DATA_DIR:
    os.makedirs(DATA_DIR, exist_ok=True)
    DATABASE_PATH = os.path.join(DATA_DIR, "lift_store.db")
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        "sqlite:///" + DATABASE_PATH.replace("\\", "/")
    )
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///lift_store.db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


if DATA_DIR:
    UPLOAD_FOLDER = os.path.join(DATA_DIR, "uploads", "products")
else:
    UPLOAD_FOLDER = os.path.join(
        app.root_path,
        "static",
        "uploads",
        "products",
    )

ALLOWED_IMAGE_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "webp",
}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(
    app.config["UPLOAD_FOLDER"],
    exist_ok=True,
)


def allowed_image(filename):
    """
    Return True when the supplied filename has
    an allowed product-image extension.
    """

    return (
        bool(filename)
        and "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_IMAGE_EXTENSIONS
    )


def save_product_image(image_file):
    """
    Save a validated uploaded product image.

    Returns the static-relative image path, for example:
    uploads/products/abc123.jpg

    Returns None when no image was uploaded.
    """

    if not image_file or not image_file.filename:
        return None

    if not allowed_image(image_file.filename):
        raise ValueError(
            "Only JPG, JPEG, PNG and WEBP images are allowed."
        )

    safe_name = secure_filename(
        image_file.filename
    )

    extension = (
        safe_name.rsplit(".", 1)[1].lower()
    )

    unique_filename = (
        f"{uuid.uuid4().hex}.{extension}"
    )

    destination = os.path.join(
        app.config["UPLOAD_FOLDER"],
        unique_filename,
    )

    image_file.save(destination)

    return (
        f"uploads/products/{unique_filename}"
    )


def delete_local_product_image(image_path):
    """
    Delete an uploaded Lift Store product image.

    Remote HTTP/HTTPS images are never deleted.
    """

    if not image_path:
        return

    if not image_path.startswith(
        "uploads/products/"
    ):
        return

    filename = os.path.basename(image_path)

    full_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        filename,
    )

    if os.path.isfile(full_path):
        try:
            os.remove(full_path)
        except OSError:
            pass


# ==================================================
# DATABASE
# ==================================================

db = SQLAlchemy(app)

migrate = Migrate(app, db)

csrf = CSRFProtect(app)


# ==================================================
# ADMIN CONFIGURATION
# ==================================================

ADMIN_EMAIL = os.environ.get(
    "ADMIN_EMAIL",
    "admin@liftstore.ug",
)

ADMIN_PASSWORD = os.environ.get(
    "ADMIN_PASSWORD",
    "LiftAdmin123",
)

# ==================================================

# DATABASE MODELS - LIFT STORE V2

# ==================================================



from datetime import datetime





# --------------------------------------------------

# CATEGORY

# --------------------------------------------------



class Category(db.Model):

    __tablename__ = "category"



    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), unique=True, nullable=False)

    description = db.Column(db.Text)

    image = db.Column(db.String(500))

    active = db.Column(db.Boolean, default=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)





# --------------------------------------------------

# BRAND

# --------------------------------------------------



class Brand(db.Model):

    __tablename__ = "brand"



    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), unique=True, nullable=False)

    description = db.Column(db.Text)

    logo = db.Column(db.String(500))

    active = db.Column(db.Boolean, default=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)





# --------------------------------------------------

# PRODUCT

# --------------------------------------------------



class Product(db.Model):

    __tablename__ = "product"



    id = db.Column(db.Integer, primary_key=True)



    name = db.Column(

        db.String(120),

        nullable=False

    )



    # Keep these existing text columns so old products

    # remain compatible with Lift Store V1.

    brand = db.Column(

        db.String(50),

        nullable=False

    )



    category = db.Column(

        db.String(50),

        nullable=False

    )



    price = db.Column(

        db.Integer,

        nullable=False

    )



    old_price = db.Column(db.Integer)



    storage = db.Column(db.String(30))

    ram = db.Column(db.String(30))

    camera = db.Column(db.String(80))

    battery = db.Column(db.String(50))

    display = db.Column(db.String(80))



    image = db.Column(db.String(500))

    description = db.Column(db.Text)



    stock = db.Column(

        db.Integer,

        default=10

    )



    featured = db.Column(

        db.Boolean,

        default=False

    )



    # V2 additions

    category_id = db.Column(

        db.Integer,

        db.ForeignKey("category.id"),

        nullable=True

    )



    brand_id = db.Column(

        db.Integer,

        db.ForeignKey("brand.id"),

        nullable=True

    )



    discount_percent = db.Column(

        db.Integer,

        default=0

    )



    sales_count = db.Column(

        db.Integer,

        default=0

    )



    active = db.Column(

        db.Boolean,

        default=True

    )



    created_at = db.Column(

        db.DateTime,

        default=datetime.utcnow

    )



    updated_at = db.Column(

        db.DateTime,

        default=datetime.utcnow,

        onupdate=datetime.utcnow

    )



    category_record = db.relationship(

        "Category",

        backref="products"

    )



    brand_record = db.relationship(

        "Brand",

        backref="products"

    )



    @property

    def stock_status(self):

        if self.stock <= 0:

            return "Out of Stock"

        elif self.stock <= 5:

            return "Low Stock"

        return "In Stock"



    @property

    def sale_price(self):

        if self.discount_percent and self.discount_percent > 0:

            discount = (

                self.price * self.discount_percent

            ) / 100



            return int(self.price - discount)



        return self.price





# --------------------------------------------------

# USER / CUSTOMER

# --------------------------------------------------



class User(db.Model):

    __tablename__ = "user"



    id = db.Column(

        db.Integer,

        primary_key=True

    )



    name = db.Column(

        db.String(100),

        nullable=False

    )



    email = db.Column(

        db.String(150),

        unique=True,

        nullable=False

    )



    password = db.Column(

        db.String(250),

        nullable=False

    )



    phone = db.Column(db.String(30))



    active = db.Column(

        db.Boolean,

        default=True

    )



    created_at = db.Column(

        db.DateTime,

        default=datetime.utcnow

    )





# --------------------------------------------------

# ADMINISTRATOR

# --------------------------------------------------



class Admin(db.Model):

    __tablename__ = "admin"



    id = db.Column(

        db.Integer,

        primary_key=True

    )



    name = db.Column(

        db.String(100),

        nullable=False

    )



    email = db.Column(

        db.String(150),

        unique=True,

        nullable=False

    )



    password = db.Column(

        db.String(250),

        nullable=False

    )



    active = db.Column(

        db.Boolean,

        default=True

    )



    created_at = db.Column(

        db.DateTime,

        default=datetime.utcnow

    )





# --------------------------------------------------

# DELIVERY AREA

# --------------------------------------------------



class DeliveryArea(db.Model):

    __tablename__ = "delivery_area"



    id = db.Column(

        db.Integer,

        primary_key=True

    )



    name = db.Column(

        db.String(120),

        unique=True,

        nullable=False

    )



    fee = db.Column(

        db.Integer,

        default=0

    )



    active = db.Column(

        db.Boolean,

        default=True

    )





# --------------------------------------------------

# ORDER

# --------------------------------------------------



class Order(db.Model):

    __tablename__ = "order"



    id = db.Column(

        db.Integer,

        primary_key=True

    )



    customer_name = db.Column(

        db.String(100),

        nullable=False

    )



    phone = db.Column(

        db.String(30),

        nullable=False

    )



    location = db.Column(

        db.String(200),

        nullable=False

    )



    total = db.Column(

        db.Integer,

        nullable=False

    )



    status = db.Column(

        db.String(50),

        default="Pending"

    )



    # V2 fields

    user_id = db.Column(

        db.Integer,

        db.ForeignKey("user.id"),

        nullable=True

    )



    delivery_area_id = db.Column(

        db.Integer,

        db.ForeignKey("delivery_area.id"),

        nullable=True

    )



    delivery_fee = db.Column(

        db.Integer,

        default=0

    )



    payment_method = db.Column(

        db.String(50),

        default="Cash on Delivery"

    )



    payment_status = db.Column(

        db.String(50),

        default="Pending"

    )



    tracking_status = db.Column(

        db.String(50),

        default="Order Received"

    )



    created_at = db.Column(

        db.DateTime,

        default=datetime.utcnow

    )



    updated_at = db.Column(

        db.DateTime,

        default=datetime.utcnow,

        onupdate=datetime.utcnow

    )



    customer = db.relationship(

        "User",

        backref="orders"

    )



    delivery_area = db.relationship(

        "DeliveryArea",

        backref="orders"

    )



    items = db.relationship(

        "OrderItem",

        backref="order",

        lazy=True,

        cascade="all, delete-orphan"

    )





# --------------------------------------------------

# ORDER ITEM

# --------------------------------------------------



class OrderItem(db.Model):

    __tablename__ = "order_item"



    id = db.Column(

        db.Integer,

        primary_key=True

    )



    order_id = db.Column(

        db.Integer,

        db.ForeignKey("order.id"),

        nullable=False

    )



    product_id = db.Column(

        db.Integer,

        db.ForeignKey("product.id"),

        nullable=False

    )



    product_name = db.Column(

        db.String(120),

        nullable=False

    )



    price = db.Column(

        db.Integer,

        nullable=False

    )



    quantity = db.Column(

        db.Integer,

        nullable=False

    )



    product = db.relationship(

        "Product",

        backref="order_items"

    )





# --------------------------------------------------

# WISHLIST

# --------------------------------------------------



class WishlistItem(db.Model):

    __tablename__ = "wishlist_item"



    id = db.Column(

        db.Integer,

        primary_key=True

    )



    user_id = db.Column(

        db.Integer,

        db.ForeignKey("user.id"),

        nullable=False

    )



    product_id = db.Column(

        db.Integer,

        db.ForeignKey("product.id"),

        nullable=False

    )



    created_at = db.Column(

        db.DateTime,

        default=datetime.utcnow

    )



    user = db.relationship(

        "User",

        backref="wishlist_items"

    )



    product = db.relationship(

        "Product",

        backref="wishlist_items"

    )



    __table_args__ = (

        db.UniqueConstraint(

            "user_id",

            "product_id",

            name="uq_wishlist_user_product"

        ),

    )





# --------------------------------------------------

# PRODUCT REVIEW

# --------------------------------------------------



class Review(db.Model):

    __tablename__ = "review"



    id = db.Column(

        db.Integer,

        primary_key=True

    )



    user_id = db.Column(

        db.Integer,

        db.ForeignKey("user.id"),

        nullable=False

    )



    product_id = db.Column(

        db.Integer,

        db.ForeignKey("product.id"),

        nullable=False

    )



    rating = db.Column(

        db.Integer,

        nullable=False

    )



    comment = db.Column(db.Text)



    approved = db.Column(

        db.Boolean,

        default=True

    )



    created_at = db.Column(

        db.DateTime,

        default=datetime.utcnow

    )



    user = db.relationship(

        "User",

        backref="reviews"

    )



    product = db.relationship(

        "Product",

        backref="reviews"

    )





# --------------------------------------------------

# COUPON / PROMOTION

# --------------------------------------------------



class Coupon(db.Model):

    __tablename__ = "coupon"



    id = db.Column(

        db.Integer,

        primary_key=True

    )



    code = db.Column(

        db.String(50),

        unique=True,

        nullable=False

    )



    discount_percent = db.Column(

        db.Integer,

        default=0

    )



    minimum_order = db.Column(

        db.Integer,

        default=0

    )



    active = db.Column(

        db.Boolean,

        default=True

    )



    start_date = db.Column(db.DateTime)

    end_date = db.Column(db.DateTime)



    created_at = db.Column(

        db.DateTime,

        default=datetime.utcnow

    )





# --------------------------------------------------

# STORE SETTINGS

# --------------------------------------------------



class StoreSetting(db.Model):

    __tablename__ = "store_setting"



    id = db.Column(

        db.Integer,

        primary_key=True

    )



    store_name = db.Column(

        db.String(120),

        default="Lift Store"

    )



    phone = db.Column(db.String(30))

    whatsapp = db.Column(db.String(30))

    email = db.Column(db.String(150))

    address = db.Column(db.String(250))



    currency = db.Column(

        db.String(20),

        default="UGX"

    )



    opening_hours = db.Column(

        db.String(250)

    )



    delivery_message = db.Column(

        db.Text

    )



    hero_title = db.Column(

        db.String(200),

        default="Welcome to Lift Store"

    )



    hero_subtitle = db.Column(

        db.String(300),

        default="Quality technology at great prices."

    )

# ==================================================
# LIFT STORE V2 INITIAL DATA
# ==================================================

def seed_v2_data():
    """Create the initial Lift Store V2 data safely."""

    # --------------------------------------------------
    # CATEGORIES
    # --------------------------------------------------

    category_names = [
        "Smartphones",
        "Laptops",
        "Tablets",
        "Accessories",
        "Smart Watches",
        "Earphones",
        "Chargers",
        "Power Banks",
    ]

    for category_name in category_names:
        category = Category.query.filter(
            db.func.lower(Category.name)
            == category_name.lower()
        ).first()

        if category is None:
            db.session.add(
                Category(
                    name=category_name,
                    active=True
                )
            )

    # --------------------------------------------------
    # BRANDS
    # --------------------------------------------------

    brand_names = [
        "Samsung",
        "Apple",
        "Tecno",
        "Infinix",
        "itel",
        "Xiaomi",
        "Nokia",
        "Oppo",
        "Vivo",
        "Huawei",
    ]

    for brand_name in brand_names:
        brand = Brand.query.filter(
            db.func.lower(Brand.name)
            == brand_name.lower()
        ).first()

        if brand is None:
            db.session.add(
                Brand(
                    name=brand_name,
                    active=True
                )
            )

    # --------------------------------------------------
    # LIRA DELIVERY AREAS
    # --------------------------------------------------

    delivery_areas = [
        ("Lira City Centre", 5000),
        ("Adyel", 5000),
        ("Ojwina", 5000),
        ("Railways", 5000),
        ("Senior Quarters", 5000),
        ("Kichope", 7000),
        ("Ngetta", 8000),
        ("Adekokwok", 10000),
        ("Outside Lira City", 15000),
    ]

    for area_name, delivery_fee in delivery_areas:
        area = DeliveryArea.query.filter(
            db.func.lower(DeliveryArea.name)
            == area_name.lower()
        ).first()

        if area is None:
            db.session.add(
                DeliveryArea(
                    name=area_name,
                    fee=delivery_fee,
                    active=True
                )
            )

    # --------------------------------------------------
    # STORE SETTINGS
    # --------------------------------------------------

    settings = StoreSetting.query.first()

    if settings is None:
        settings = StoreSetting(
            store_name="Lift Store",
            phone="",
            whatsapp="",
            email="",
            address="Lira City, Uganda",
            currency="UGX",
            opening_hours=(
                "Monday - Saturday: "
                "8:00 AM - 7:00 PM"
            ),
            delivery_message=(
                "Fast and reliable delivery within "
                "Lira City and surrounding areas."
            ),
            hero_title=(
                "Quality Technology. Better Prices."
            ),
            hero_subtitle=(
                "Shop smartphones, accessories and "
                "technology products from Lift Store."
            )
        )

        db.session.add(settings)

    # --------------------------------------------------
    # DATABASE ADMINISTRATOR
    # --------------------------------------------------

    admin_email = ADMIN_EMAIL.strip().lower()

    admin = Admin.query.filter(
        db.func.lower(Admin.email)
        == admin_email
    ).first()

    if admin is None:
        admin = Admin(
            name="Lift Store Administrator",
            email=admin_email,
            password=generate_password_hash(
                ADMIN_PASSWORD
            ),
            active=True
        )

        db.session.add(admin)

    # Save categories, brands, areas, settings and admin
    # before linking products.
    db.session.commit()

    # --------------------------------------------------
    # LINK EXISTING PRODUCTS TO CATEGORY / BRAND TABLES
    # --------------------------------------------------

    products = Product.query.all()

    for product in products:

        # Link the existing text brand to Brand.
        if product.brand and product.brand_id is None:
            brand_record = Brand.query.filter(
                db.func.lower(Brand.name)
                == product.brand.strip().lower()
            ).first()

            if brand_record:
                product.brand_id = brand_record.id

        # Link the existing text category to Category.
        if product.category and product.category_id is None:
            category_record = Category.query.filter(
                db.func.lower(Category.name)
                == product.category.strip().lower()
            ).first()

            if category_record:
                product.category_id = category_record.id

    db.session.commit()

    print("")
    print("======================================")
    print("LIFT STORE V2 INITIALIZATION COMPLETE")
    print("======================================")
    print(
        "Categories:",
        Category.query.count()
    )
    print(
        "Brands:",
        Brand.query.count()
    )
    print(
        "Delivery Areas:",
        DeliveryArea.query.count()
    )
    print(
        "Administrators:",
        Admin.query.count()
    )
    print(
        "Store Settings:",
        StoreSetting.query.count()
    )
    print(
        "Products:",
        Product.query.count()
    )
    print("======================================")
    print("")


# ==================================================
# FLASK CLI - INITIALIZE LIFT STORE V2
# ==================================================
@app.cli.command("bootstrap-demo-db")
def bootstrap_demo_db():
    """Create a fresh demo database and initialize Lift Store V2 data."""
    print("Creating Lift Store demo database...")

    db.create_all()

    try:
        seed_v2_data()
        print("Lift Store demo database initialized successfully.")
    except Exception as error:
        db.session.rollback()
        print("Demo database initialization failed.")
        print("Error:", error)
        raise

@app.cli.command("seed-v2")
def seed_v2_command():
    """Initialize Lift Store V2 data."""

    try:
        seed_v2_data()

    except Exception as error:
        db.session.rollback()

        print("")
        print("Lift Store V2 initialization failed.")
        print("Error:", error)
        print("")

        raise

def seed_products():



    # Do not add products again if the database

    # already contains products.

    if Product.query.count() > 0:

        return



    products = [



        Product(

            name="Samsung Galaxy A16",

            brand="Samsung",

            category="Smartphones",

            price=650000,

            old_price=720000,

            storage="128GB",

            ram="4GB",

            camera="50MP Main Camera",

            battery="5000mAh",

            display="6.7-inch Display",

            image=(

                "https://images.samsung.com/is/image/"

                "samsung/p6pim/africa_en/sm-a165fzkgafb/"

                "gallery/africa-en-galaxy-a16-sm-a165-"

                "sm-a165fzkgafb-thumb-543484807"

            ),

            description=(

                "A stylish Samsung smartphone suitable for "

                "everyday communication, social media, "

                "photography and entertainment."

            ),

            stock=12,

            featured=True

        ),



        Product(

            name="Apple iPhone 15",

            brand="Apple",

            category="Smartphones",

            price=2850000,

            old_price=3100000,

            storage="128GB",

            ram="6GB",

            camera="48MP Main Camera",

            battery="All-day battery",

            display="6.1-inch Super Retina XDR",

            image=(

                "https://store.storeimages.cdn-apple.com/"

                "4982/as-images.apple.com/is/MTP03?"

                "wid=600&hei=600&fmt=jpeg&qlt=95"

            ),

            description=(

                "Premium Apple smartphone featuring a "

                "powerful processor, advanced camera system "

                "and high-quality display."

            ),

            stock=6,

            featured=True

        ),



        Product(

            name="Tecno Camon 40",

            brand="Tecno",

            category="Smartphones",

            price=980000,

            old_price=1050000,

            storage="256GB",

            ram="8GB",

            camera="High-resolution AI Camera",

            battery="Large capacity battery",

            display="AMOLED Display",

            image=(

                "https://d13pvy8xd75yde.cloudfront.net/"

                "global/camon40/CAMON40-green.png"

            ),

            description=(

                "A modern Tecno smartphone designed for "

                "photography, entertainment and everyday "

                "productivity."

            ),

            stock=15,

            featured=True

        ),



        Product(

            name="Infinix NOTE 50",

            brand="Infinix",

            category="Smartphones",

            price=850000,

            old_price=920000,

            storage="256GB",

            ram="8GB",

            camera="Advanced Main Camera",

            battery="Long-lasting battery",

            display="Large AMOLED Display",

            image=(

                "https://fdn2.gsmarena.com/vv/bigpic/"

                "infinix-note-50.jpg"

            ),

            description=(

                "A powerful Infinix smartphone offering "

                "generous storage, a large display and "

                "strong everyday performance."

            ),

            stock=9,

            featured=True

        ),



        Product(

            name="Samsung Galaxy A06",

            brand="Samsung",

            category="Smartphones",

            price=420000,

            old_price=470000,

            storage="64GB",

            ram="4GB",

            camera="50MP Camera",

            battery="5000mAh",

            display="6.7-inch Display",

            image=(

                "https://fdn2.gsmarena.com/vv/bigpic/"

                "samsung-galaxy-a06.jpg"

            ),

            description=(

                "An affordable Samsung Galaxy smartphone "

                "for calls, WhatsApp, social media and "

                "daily use."

            ),

            stock=20,

            featured=False

        ),



        Product(

            name="Tecno Spark 30",

            brand="Tecno",

            category="Smartphones",

            price=550000,

            old_price=610000,

            storage="128GB",

            ram="8GB",

            camera="50MP Camera",

            battery="5000mAh",

            display="Large HD Display",

            image=(

                "https://fdn2.gsmarena.com/vv/bigpic/"

                "tecno-spark-30.jpg"

            ),

            description=(

                "A stylish and affordable Tecno smartphone "

                "for entertainment and everyday use."

            ),

            stock=18,

            featured=False

        ),



        Product(

            name="Infinix Hot 50",

            brand="Infinix",

            category="Smartphones",

            price=590000,

            old_price=650000,

            storage="128GB",

            ram="8GB",

            camera="AI Camera",

            battery="5000mAh",

            display="Large Display",

            image=(

                "https://fdn2.gsmarena.com/vv/bigpic/"

                "infinix-hot-50.jpg"

            ),

            description=(

                "Affordable performance with generous "

                "storage and a large display."

            ),

            stock=14,

            featured=False

        ),



        Product(

            name="itel A80",

            brand="itel",

            category="Smartphones",

            price=350000,

            old_price=390000,

            storage="128GB",

            ram="4GB",

            camera="50MP Camera",

            battery="5000mAh",

            display="Large Display",

            image=(

                "https://fdn2.gsmarena.com/vv/bigpic/"

                "itel-a80.jpg"

            ),

            description=(

                "A budget-friendly smartphone suitable for "

                "students, families and everyday communication."

            ),

            stock=25,

            featured=False

        )

    ]



    db.session.add_all(products)

    db.session.commit()

# ==================================================
# HOME / STOREFRONT
# ==================================================

@app.route("/")
def home():
    search = request.args.get(
        "search",
        "",
    ).strip()

    selected_brand = request.args.get(
        "brand",
        "",
    ).strip()

    selected_category = request.args.get(
        "category",
        "",
    ).strip()

    # --------------------------------------------------
    # MAIN PRODUCT QUERY
    # --------------------------------------------------

    query = Product.query.filter(
        Product.active.is_(True)
    )

    # --------------------------------------------------
    # SEARCH
    # --------------------------------------------------

    if search:
        search_term = f"%{search}%"

        query = query.filter(
            db.or_(
                Product.name.ilike(
                    search_term
                ),
                Product.brand.ilike(
                    search_term
                ),
                Product.category.ilike(
                    search_term
                ),
                Product.description.ilike(
                    search_term
                ),
            )
        )

    # --------------------------------------------------
    # BRAND FILTER
    # --------------------------------------------------

    if selected_brand:
        query = query.filter(
            db.func.lower(
                Product.brand
            )
            == selected_brand.lower()
        )

    # --------------------------------------------------
    # CATEGORY FILTER
    # --------------------------------------------------

    if selected_category:
        query = query.filter(
            db.func.lower(
                Product.category
            )
            == selected_category.lower()
        )

    if request.args.get('deals')=='1': query=query.filter(db.or_(Product.discount_percent>0,Product.old_price>Product.price))
    selling=db.case((Product.discount_percent>0,db.cast(Product.price*(100-Product.discount_percent)/100.0,db.Integer)),else_=Product.price)
    for key,comparison in [('min_price',lambda amount:selling>=amount),('max_price',lambda amount:selling<=amount)]:
        raw=request.args.get(key,'').strip()
        if raw:
            try:
                amount=int(raw)
                if amount<0 or amount>2147483647: raise ValueError()
                query=query.filter(comparison(amount))
            except ValueError: flash('Enter a valid non-negative price in UGX.','warning')
    sorting={'price_asc':selling.asc(),'price_desc':selling.desc(),'name':Product.name.asc(),'popular':Product.sales_count.desc()}
    minimum_rating=request.args.get('rating',type=int)
    if minimum_rating in (1,2,3,4,5):
        rated=db.session.query(Review.product_id).filter(Review.approved.is_(True)).group_by(Review.product_id).having(db.func.avg(Review.rating)>=minimum_rating)
        query=query.filter(Product.id.in_(rated))
    products=query.order_by(sorting.get(request.args.get('sort'),Product.created_at.desc()),Product.id.desc()).all()

    # --------------------------------------------------
    # ACTIVE CATEGORIES
    # --------------------------------------------------

    categories = (
        Category.query
        .filter_by(active=True)
        .order_by(Category.name.asc())
        .all()
    )

    # --------------------------------------------------
    # ACTIVE BRANDS
    # --------------------------------------------------

    brands = (
        Brand.query
        .filter_by(active=True)
        .order_by(Brand.name.asc())
        .all()
    )

    # --------------------------------------------------
    # FEATURED PRODUCTS
    # --------------------------------------------------

    featured_products = (
        Product.query
        .filter(
            Product.active.is_(True),
            Product.featured.is_(True),
            Product.stock > 0,
        )
        .order_by(
            Product.created_at.desc()
        )
        .limit(8)
        .all()
    )

    # --------------------------------------------------
    # SPECIAL OFFERS
    # --------------------------------------------------

    special_offers = (
        Product.query
        .filter(
            Product.active.is_(True),
            Product.stock > 0,
            db.or_(
                Product.discount_percent > 0,
                Product.old_price
                > Product.price,
            ),
        )
        .order_by(
            Product.discount_percent.desc(),
            Product.created_at.desc(),
        )
        .limit(8)
        .all()
    )

    # --------------------------------------------------
    # NEW ARRIVALS
    # --------------------------------------------------

    new_arrivals = (
        Product.query
        .filter(
            Product.active.is_(True),
            Product.stock > 0,
        )
        .order_by(
            Product.created_at.desc()
        )
        .limit(8)
        .all()
    )

    # --------------------------------------------------
    # BEST SELLERS
    # --------------------------------------------------

    best_sellers = (
        Product.query
        .filter(
            Product.active.is_(True),
            Product.stock > 0,
            Product.sales_count > 0,
        )
        .order_by(
            Product.sales_count.desc(),
            Product.created_at.desc(),
        )
        .limit(8)
        .all()
    )

    import difflib
    suggested_search=None
    if search and not products:
        names=[name for (name,) in db.session.query(Product.name).filter(Product.active.is_(True)).all()]
        suggestions=difflib.get_close_matches(search,names,n=1,cutoff=0.45)
        suggested_search=suggestions[0] if suggestions else None
    return render_template(
        "index.html",
        suggested_search=suggested_search,
        products=products,
        categories=categories,
        brands=brands,
        featured_products=featured_products,
        special_offers=special_offers,
        new_arrivals=new_arrivals,
        best_sellers=best_sellers,
        selected_brand=selected_brand,
        selected_category=selected_category,
        search=search,
    )

# ==================================================

# PRODUCT DETAILS

# ==================================================



@app.route("/product/<int:product_id>")

def product_detail(product_id):
    product=Product.query.filter_by(id=product_id,active=True).first_or_404()
    related=Product.query.filter(Product.active.is_(True),Product.brand==product.brand,Product.id!=product.id).limit(4).all()
    reviews=Review.query.filter_by(product_id=product.id,approved=True).order_by(Review.created_at.desc()).all()
    return render_template('product.html',product=product,related=related,reviews=reviews,verified_reviewers={uid for (uid,) in db.session.query(Order.user_id).join(OrderItem).filter(OrderItem.product_id==product.id,Order.status=='Delivered').all()},average_rating=round(sum(review.rating for review in reviews)/len(reviews),1) if reviews else None)




# ==================================================
# ADD TO CART
# ==================================================

@app.route(
    "/add-to-cart/<int:product_id>",
    methods=["POST"],
)
def add_to_cart(product_id):
    product = Product.query.filter_by(
        id=product_id,
        active=True,
    ).first_or_404()

    if product.stock <= 0:
        flash(
            f"{product.name} is currently out of stock.",
            "warning",
        )

        return redirect(
            request.referrer
            or url_for("home")
        )

    cart_data = session.get(
        "cart",
        {},
    )

    key = str(product.id)

    try:
        current_quantity = int(
            cart_data.get(key, 0)
        )
    except (TypeError, ValueError):
        current_quantity = 0

    if current_quantity >= product.stock:
        flash(
            "You cannot add more than "
            "the available stock.",
            "warning",
        )

        return redirect(
            request.referrer
            or url_for("home")
        )

    cart_data[key] = (
        current_quantity + 1
    )

    session["cart"] = cart_data
    session.modified = True

    flash(
        f"{product.name} added to your cart.",
        "success",
    )

    return redirect(
        request.referrer
        or url_for("home")
    )


# ==================================================
# CART
# ==================================================

@app.route("/cart")
def cart():
    cart_data = session.get(
        "cart",
        {},
    )

    items = []
    total = 0

    for product_id, quantity in cart_data.items():
        product = db.session.get(
            Product,
            int(product_id),
        )

        if (
            not product
            or not product.active
        ):
            continue

        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            continue

        if quantity <= 0:
            continue

        unit_price = product.sale_price

        subtotal = (
            unit_price * quantity
        )

        total += subtotal

        items.append({
            "product": product,
            "quantity": quantity,
            "unit_price": unit_price,
            "subtotal": subtotal,
        })

    return render_template(
        "cart.html",
        items=items,
        total=total,
    )


# ==================================================
# UPDATE CART
# ==================================================

@app.route(
    "/update-cart/<int:product_id>",
    methods=["POST"],
)
def update_cart(product_id):
    product = Product.query.filter_by(
        id=product_id,
        active=True,
    ).first_or_404()

    cart_data = session.get(
        "cart",
        {},
    )

    quantity = request.form.get(
        "quantity",
        1,
        type=int,
    )

    key = str(product.id)

    if quantity <= 0:
        cart_data.pop(
            key,
            None,
        )

    else:
        if quantity > product.stock:
            quantity = product.stock

            flash(
                f"Only {product.stock} units "
                f"of {product.name} are available.",
                "warning",
            )

        if quantity <= 0:
            cart_data.pop(
                key,
                None,
            )
        else:
            cart_data[key] = quantity

    session["cart"] = cart_data
    session.modified = True

    return redirect(
        url_for("cart")
    )




# ==================================================

# REMOVE FROM CART

# ==================================================



@app.route(

    "/remove-from-cart/<int:product_id>"

)

def remove_from_cart(product_id):



    cart_data = session.get(

        "cart",

        {}

    )



    cart_data.pop(

        str(product_id),

        None

    )



    session["cart"] = cart_data

    session.modified = True



    flash(

        "Product removed from your cart.",

        "success"

    )



    return redirect(

        url_for("cart")

    )

# ==================================================
# CHECKOUT
# ==================================================

@app.route(
    "/checkout",
    methods=["GET", "POST"],
)
def checkout():
    cart_data = session.get(
        "cart",
        {},
    )

    if not cart_data:
        flash(
            "Your cart is empty.",
            "warning",
        )

        return redirect(
            url_for("home")
        )

    cart_items = []
    subtotal = 0

    # --------------------------------------------------
    # BUILD CART
    # --------------------------------------------------

    for product_id, quantity in cart_data.items():
        product = db.session.get(
            Product,
            int(product_id),
        )

        if (
            not product
            or not product.active
        ):
            flash(
                "One of the products in your cart "
                "is no longer available.",
                "warning",
            )

            return redirect(
                url_for("cart")
            )

        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            flash(
                "Your cart contains an invalid quantity.",
                "danger",
            )

            return redirect(
                url_for("cart")
            )

        if quantity <= 0:
            flash(
                "Your cart contains an invalid quantity.",
                "danger",
            )

            return redirect(
                url_for("cart")
            )

        if quantity > product.stock:
            flash(
                f"Only {product.stock} units "
                f"of {product.name} are available.",
                "warning",
            )

            return redirect(
                url_for("cart")
            )

        unit_price = product.sale_price

        item_subtotal = (
            unit_price * quantity
        )

        subtotal += item_subtotal

        cart_items.append({
            "product": product,
            "quantity": quantity,
            "unit_price": unit_price,
            "subtotal": item_subtotal,
        })

    if not cart_items:
        flash(
            "No valid products were found "
            "in your cart.",
            "warning",
        )

        return redirect(
            url_for("home")
        )

    # --------------------------------------------------
    # DELIVERY AREAS
    # --------------------------------------------------

    delivery_areas = (
        DeliveryArea.query
        .filter_by(active=True)
        .order_by(
            DeliveryArea.name.asc()
        )
        .all()
    )

    delivery_fee = 0
    total = subtotal

    # --------------------------------------------------
    # PROCESS ORDER
    # --------------------------------------------------

    if request.method == "POST":
        customer_name = request.form.get(
            "customer_name",
            "",
        ).strip()

        phone = request.form.get(
            "phone",
            "",
        ).strip()

        location = request.form.get(
            "location",
            "",
        ).strip()

        delivery_area_id = request.form.get(
            "delivery_area_id",
            type=int,
        )

        payment_method = request.form.get(
            "payment_method",
            "Cash on Delivery",
        ).strip()

        if (
            not customer_name
            or not phone
            or not location
            or not delivery_area_id
        ):
            flash(
                "Please complete all checkout fields.",
                "danger",
            )

            return render_template(
                "checkout.html",
                cart_items=cart_items,
                subtotal=subtotal,
                delivery_fee=0,
                total=subtotal,
                delivery_areas=delivery_areas,
            )

        delivery_area = db.session.get(
            DeliveryArea,
            delivery_area_id,
        )

        if (
            not delivery_area
            or not delivery_area.active
        ):
            flash(
                "Please select a valid delivery area.",
                "danger",
            )

            return redirect(
                url_for("checkout")
            )

        allowed_payment_methods = {'Cash on Delivery'}

        if (
            payment_method
            not in allowed_payment_methods
        ):
            flash(
                "Please select a valid payment method.",
                "danger",
            )

            return redirect(
                url_for("checkout")
            )

        discount_amount=0
        coupon_code=request.form.get('coupon','').strip().upper()
        if coupon_code:
            coupon=Coupon.query.filter(db.func.upper(Coupon.code)==coupon_code,Coupon.active.is_(True)).first()
            now=datetime.utcnow()
            if not coupon or (coupon.start_date and coupon.start_date>now) or (coupon.end_date and coupon.end_date<now) or subtotal<(coupon.minimum_order or 0) or not 0<=coupon.discount_percent<=100:
                flash('This coupon is unavailable or the minimum order has not been met.','danger')
                return redirect(url_for('checkout'))
            discount_amount=subtotal*coupon.discount_percent//100
        delivery_fee = (
            delivery_area.fee or 0
        )

        total = (
            subtotal + delivery_fee - discount_amount
        )

        try:
            # ------------------------------------------
            # FINAL STOCK CHECK
            # ------------------------------------------

            for item in cart_items:
                product = db.session.get(
                    Product,
                    item["product"].id,
                )

                quantity = item["quantity"]

                if (
                    not product
                    or not product.active
                    or product.stock < quantity
                ):
                    raise ValueError(
                        f"{item['product'].name} "
                        "does not have enough stock."
                    )

            # ------------------------------------------
            # CREATE ORDER
            # ------------------------------------------

            order = Order(
                customer_name=customer_name,
                phone=phone,
                location=location,
                total=total,
                status="Pending",
                user_id=session.get(
                    "user_id"
                ),
                delivery_area_id=(
                    delivery_area.id
                ),
                delivery_fee=(
                    delivery_fee
                ),
                payment_method=(
                    payment_method
                ),
                payment_status="Pending",
                tracking_status=(
                    "Order Received"
                ),
            )

            db.session.add(order)

            db.session.flush()
            if discount_amount: db.session.add(OrderDiscount(order_id=order.id,code=coupon_code,amount=discount_amount))

            # ------------------------------------------
            # CREATE ORDER ITEMS
            # ------------------------------------------

            for item in cart_items:
                product = db.session.get(
                    Product,
                    item["product"].id,
                )

                quantity = (
                    item["quantity"]
                )

                unit_price = (
                    product.sale_price
                )

                order_item = OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    product_name=product.name,
                    price=unit_price,
                    quantity=quantity,
                )

                db.session.add(
                    order_item
                )

                changed=db.session.execute(db.update(Product).where(Product.id==product.id,Product.active.is_(True),Product.stock>=quantity).values(stock=Product.stock-quantity,sales_count=db.func.coalesce(Product.sales_count,0)+quantity))
                if changed.rowcount!=1:
                    raise ValueError(f'{product.name} no longer has enough stock.')

            db.session.commit()

        except ValueError as error:
            db.session.rollback()

            flash(
                str(error),
                "danger",
            )

            return redirect(
                url_for("cart")
            )

        except Exception as error:
            db.session.rollback()

            print(
                "Checkout error:",
                error,
            )

            flash(
                "The order could not be saved. "
                "Please try again.",
                "danger",
            )

            return redirect(
                url_for("cart")
            )

        # ----------------------------------------------
        # CLEAR CART ONLY AFTER SUCCESSFUL COMMIT
        # ----------------------------------------------

        session['guest_order_ids']=(session.get('guest_order_ids',[])+[order.id])[-20:]
        session["cart"] = {}
        session.modified = True

        flash(
            f"Order #{order.id} was received successfully. "
            "Lift Store will contact you to confirm delivery.",
            "success",
        )

        return redirect(
            url_for("customer_order",order_id=order.id)
        )

    # --------------------------------------------------
    # DISPLAY CHECKOUT
    # --------------------------------------------------

    return render_template(
        "checkout.html",
        cart_items=cart_items,
        subtotal=subtotal,
        delivery_fee=delivery_fee,
        total=total,
        delivery_areas=delivery_areas,
    )

@app.route(

    "/register",

    methods=["GET", "POST"]

)

def register():
    if request.method=='POST':
        name=request.form.get('name','').strip()
        identity=request.form.get('identity',request.form.get('email','')).strip()
        password=request.form.get('password','')
        try:
            email,phone=account_identity(identity)
            if not name or len(name)>100: raise ValueError('Enter your name, up to 100 characters.')
            if len(password)<8 or len(password)>128: raise ValueError('Use a password between 8 and 128 characters.')
            if identity_in_use(identity): raise ValueError('An account already uses these details. Please sign in.')
            user=User(name=name,email=email or ('phone-'+phone+'@accounts.invalid'),phone=phone,password=generate_password_hash(password),active=True)
            db.session.add(user);db.session.commit()
            session['user_id']=user.id;session['user_name']=user.name
            stamp_customer_session(user)
            merge_saved_cart(user)
            flash('Your account is ready.','success')
            return redirect(url_for('customer_profile'))
        except ValueError as error: flash(str(error),'danger')
        except IntegrityError:
            db.session.rollback();flash('An account already uses these details.','danger')
    return render_template('register.html')





# ==================================================

# CUSTOMER LOGIN

# ==================================================



@app.route(

    "/login",

    methods=["GET", "POST"]

)

def login():
    if current_customer(): return redirect(url_for('customer_dashboard'))
    if request.method=='POST':
        identity=request.form.get('identity',request.form.get('email','')).strip()
        user=find_customer(identity)
        if user and user.active is not False and check_password_hash(user.password,request.form.get('password','')):
            session['user_id']=user.id;session['user_name']=user.name
            stamp_customer_session(user)
            merge_saved_cart(user)
            return redirect(url_for('customer_dashboard'))
        flash('Incorrect email, phone number or password.','danger')
    return render_template('login.html')





# ==================================================

# CUSTOMER LOGOUT

# ==================================================



@app.route("/logout")

def logout():
    session.pop("cart",None)
    session.pop("guest_order_ids",None)



    session.pop(

        "user_id",

        None

    )



    session.pop(

        "user_name",

        None

    )



    flash(

        "You have been logged out.",

        "success"

    )



    return redirect(

        url_for("home")

    )





# ==================================================

# ADMIN HELPER

# ==================================================



def admin_is_logged_in():

    return bool(

        session.get("admin_logged_in")

    )





# ==================================================

# ADMIN LOGIN

# ==================================================



@app.route(

    "/admin/login",

    methods=["GET", "POST"]

)

def admin_login():



    if admin_is_logged_in():



        return redirect(

            url_for("admin_dashboard")

        )



    if request.method == "POST":



        email = request.form.get(

            "email",

            ""

        ).strip().lower()



        password = request.form.get(

            "password",

            ""

        )



        if not email or not password:



            flash(

                "Please enter the administrator "

                "email and password.",

                "danger"

            )



            return render_template(

                "admin_login.html"

            )



        admin = Admin.query.filter(
            db.func.lower(Admin.email)
            == email
        ).first()

        if (
            admin
            and admin.active
            and check_password_hash(
                admin.password,
                password,
            )
        ):
            session.clear()

            session["admin_logged_in"] = True
            session["admin_id"] = admin.id
            session["admin_email"] = admin.email

            flash(
                "Welcome to the Lift Store "
                "Admin Dashboard.",
                "success",
            )

            return redirect(
                url_for("admin_dashboard")
            )

        flash(
            "Invalid administrator email or password.",
            "danger",
        )

    return render_template(
        "admin_login.html"
    )




# ==================================================

# ADMIN DASHBOARD

# ==================================================



@app.route(
    "/admin",
    methods=["GET"]
)
def admin_dashboard():

    if not admin_is_logged_in():
        flash(
            "Please login as administrator.",
            "warning"
        )
        return redirect(
            url_for("admin_login")
        )

    # ------------------------------------------
    # MAIN STATISTICS
    # ------------------------------------------

    total_products = Product.query.count()
    total_customers = User.query.count()
    total_orders = Order.query.count()

    total_categories = Category.query.count()
    total_brands = Brand.query.count()

    pending_orders = Order.query.filter_by(
        status="Pending"
    ).count()

    low_stock_count = Product.query.filter(
        Product.stock <= 5,
        Product.stock > 0
    ).count()

    out_of_stock_count = Product.query.filter(
        Product.stock <= 0
    ).count()

    # ------------------------------------------
    # REVENUE
    # ------------------------------------------

    revenue = db.session.query(
        db.func.coalesce(
            db.func.sum(Order.total),
            0
        )
    ).scalar()

    # ------------------------------------------
    # INVENTORY VALUE
    # ------------------------------------------

    products = Product.query.all()

    inventory_value = sum(
        (product.price or 0)
        * (product.stock or 0)
        for product in products
    )

    # ------------------------------------------
    # RECENT ORDERS
    # ------------------------------------------

    recent_orders = (
        Order.query
        .order_by(Order.id.desc())
        .limit(5)
        .all()
    )

    # ------------------------------------------
    # LOW STOCK PRODUCTS
    # ------------------------------------------

    low_stock_products = (
        Product.query
        .filter(Product.stock <= 5)
        .order_by(Product.stock.asc())
        .limit(10)
        .all()
    )

    # ------------------------------------------
    # BEST SELLING PRODUCTS
    # ------------------------------------------

    best_sellers = (
        Product.query
        .order_by(
            Product.sales_count.desc()
        )
        .limit(5)
        .all()
    )

    return render_template(
        "admin_dashboard.html",

        total_products=total_products,
        total_customers=total_customers,
        total_orders=total_orders,

        total_categories=total_categories,
        total_brands=total_brands,

        revenue=revenue,
        inventory_value=inventory_value,

        pending_orders=pending_orders,
        low_stock_count=low_stock_count,
        out_of_stock_count=out_of_stock_count,

        recent_orders=recent_orders,
        low_stock_products=low_stock_products,
        best_sellers=best_sellers
    )



@app.route(
    "/admin/products",
    methods=["GET"]
)
def admin_products():
    if not admin_is_logged_in():
        return redirect(url_for('admin_login'))
    search=request.args.get('search','').strip()
    query=Product.query
    if search:
        query=query.filter(db.or_(Product.name.contains(search,autoescape=True),Product.brand.contains(search,autoescape=True),Product.category.contains(search,autoescape=True)))
    return render_template('admin_products.html',products=query.order_by(Product.id.desc()).all(),search=search)

# ==================================================
# ADMIN INVENTORY
# ==================================================

# ==================================================
# ADMIN CATEGORIES
# ==================================================

@app.route("/admin/categories")
def admin_categories():

    if not admin_is_logged_in():
        flash(
            "Please log in as administrator.",
            "warning"
        )
        return redirect(
            url_for("admin_login")
        )

    categories = (
        Category.query
        .order_by(Category.name.asc())
        .all()
    )

    return render_template(
        "admin_categories.html",
        categories=categories
    )


# ==================================================
# ADMIN - ADD CATEGORY
# ==================================================

@app.route(
    "/admin/categories/add",
    methods=["POST"]
)
def admin_add_category():

    if not admin_is_logged_in():
        flash(
            "Please log in as administrator.",
            "warning"
        )
        return redirect(
            url_for("admin_login")
        )

    name = request.form.get(
        "name",
        ""
    ).strip()

    description = request.form.get(
        "description",
        ""
    ).strip()

    # Category name is required
    if not name or len(name) > 100:
        flash(
            "Category name is required.",
            "danger"
        )
        return redirect(
            url_for("admin_categories")
        )

    # Prevent duplicate category names
    existing_category = (
        Category.query
        .filter(
            db.func.lower(Category.name)
            == name.lower()
        )
        .first()
    )

    if existing_category:
        flash(
            f'Category "{name}" already exists.',
            "warning"
        )
        return redirect(
            url_for("admin_categories")
        )

    # Create new category
    category = Category(
        name=name,
        description=description,
        active=True
    )

    try:
        db.session.add(category)
        db.session.commit()

        flash(
            f'Category "{category.name}" added successfully.',
            "success"
        )

    except Exception:
        db.session.rollback()

        flash(
            "The category could not be added. Please try again.",
            "danger"
        )

    return redirect(
        url_for("admin_categories")
    )

# ==================================================
# ADMIN - EDIT CATEGORY
# ==================================================

@app.route(
    "/admin/categories/<int:category_id>/edit",
    methods=["POST"]
)
def admin_edit_category(category_id):

    if not admin_is_logged_in():
        flash(
            "Please log in as administrator.",
            "warning"
        )
        return redirect(url_for("admin_login"))

    category = db.session.get(Category, category_id)

    if category is None:
        flash(
            "Category not found.",
            "danger"
        )
        return redirect(url_for("admin_categories"))

    name = request.form.get("name", "").strip()
    description = request.form.get("description", "").strip()

    if not name or len(name) > 100:
        flash(
            "Category name is required.",
            "danger"
        )
        return redirect(url_for("admin_categories"))

    duplicate = (
        Category.query
        .filter(
            db.func.lower(Category.name) == name.lower(),
            Category.id != category.id
        )
        .first()
    )

    if duplicate:
        flash(
            f'Another category named "{name}" already exists.',
            "warning"
        )
        return redirect(url_for("admin_categories"))

    old_name = category.name

    try:
        category.name = name
        category.description = description

        # Synchronize the old text-based product category field
        Product.query.filter(
            db.func.lower(Product.category) == old_name.lower()
        ).update(
            {
                Product.category: name
            },
            synchronize_session=False
        )

        db.session.commit()

        flash(
            f'Category "{name}" updated successfully.',
            "success"
        )

    except Exception:
        db.session.rollback()

        flash(
            "The category could not be updated.",
            "danger"
        )

    return redirect(url_for("admin_categories"))
# ==================================================
# ADMIN - ACTIVATE / DEACTIVATE CATEGORY
# ==================================================

@app.route(
    "/admin/categories/<int:category_id>/toggle",
    methods=["POST"]
)
def admin_toggle_category(category_id):

    if not admin_is_logged_in():
        flash(
            "Please log in as administrator.",
            "warning"
        )
        return redirect(
            url_for("admin_login")
        )

    category = db.session.get(
        Category,
        category_id
    )

    if category is None:
        flash(
            "Category not found.",
            "danger"
        )
        return redirect(
            url_for("admin_categories")
        )

    try:
        # Switch the current status
        category.active = not category.active

        db.session.commit()

        if category.active:
            flash(
                f'Category "{category.name}" activated successfully.',
                "success"
            )
        else:
            flash(
                f'Category "{category.name}" deactivated successfully.',
                "success"
            )

    except Exception:
        db.session.rollback()

        flash(
            "The category status could not be changed.",
            "danger"
        )

    return redirect(
        url_for("admin_categories")
    )

    # ------------------------------------------
    # CREATE CATEGORY
    # ------------------------------------------

    category = Category(
        name=name,
        description=description,
        active=True
    )

    try:
        db.session.add(category)
        db.session.commit()

        flash(
            f'Category "{category.name}" added successfully.',
            "success"
        )

    except Exception:
        db.session.rollback()

        flash(
            "The category could not be added. Please try again.",
            "danger"
        )

    return redirect(
        url_for("admin_categories")
    )
# ==================================================
# ADMIN BRANDS
# ==================================================

@app.route("/admin/brands")
def admin_brands():

    if not admin_is_logged_in():
        flash(
            "Please log in as administrator.",
            "warning"
        )
        return redirect(
            url_for("admin_login")
        )

    brands = (
        Brand.query
        .order_by(Brand.name.asc())
        .all()
    )

    return render_template(
        "admin_brands.html",
        brands=brands
    )
    
    if not admin_is_logged_in():
        flash("Please login as administrator.", "warning")
        return redirect(url_for("admin_login"))

    categories = (
        Category.query
        .filter_by(active=True)
        .order_by(Category.name.asc())
        .all()
    )
    brands = (
        Brand.query
        .filter_by(active=True)
        .order_by(Brand.name.asc())
        .all()
    )

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        brand_id = request.form.get("brand_id", type=int)
        category_id = request.form.get("category_id", type=int)
        price = request.form.get("price", type=int)
        old_price = request.form.get("old_price", type=int)
        stock = request.form.get("stock", default=0, type=int)
        storage = request.form.get("storage", "").strip()
        ram = request.form.get("ram", "").strip()
        camera = request.form.get("camera", "").strip()
        battery = request.form.get("battery", "").strip()
        display = request.form.get("display", "").strip()
        description = request.form.get("description", "").strip()
        featured = request.form.get("featured") == "on"

        # Support both the newer select fields and older text fields.
        brand_record = db.session.get(Brand, brand_id) if brand_id else None
        category_record = (
            db.session.get(Category, category_id) if category_id else None
        )
        brand_text = (
            brand_record.name if brand_record
            else request.form.get("brand", "").strip() or "Other"
        )
        category_text = (
            category_record.name if category_record
            else request.form.get("category", "").strip() or "Other"
        )

        if not name or price is None:
            flash("Product name and price are required.", "danger")
            return render_template(
                "admin_product_form.html",
                product=None, categories=categories, brands=brands,
                form_title="Add Product", submit_text="Add Product"
            )

        if price < 0 or (old_price is not None and old_price < 0):
            flash("Product prices cannot be negative.", "danger")
            return render_template(
                "admin_product_form.html",
                product=None, categories=categories, brands=brands,
                form_title="Add Product", submit_text="Add Product"
            )

        if stock is None or stock < 0:
            flash("Stock cannot be negative.", "danger")
            return render_template(
                "admin_product_form.html",
                product=None, categories=categories, brands=brands,
                form_title="Add Product", submit_text="Add Product"
            )

        try:
            image_path = save_product_image(request.files.get("image"))
        except ValueError as error:
            flash(str(error), "danger")
            return render_template(
                "admin_product_form.html",
                product=None, categories=categories, brands=brands,
                form_title="Add Product", submit_text="Add Product"
            )

        # Backward compatibility: allow an image URL/text field if the form
        # still uses one and no uploaded file was supplied.
        if not image_path:
            image_path = request.form.get("image", "").strip() or None

        product = Product(
            name=name,
            brand=brand_text,
            category=category_text,
            brand_id=brand_record.id if brand_record else None,
            category_id=category_record.id if category_record else None,
            price=price,
            old_price=old_price,
            stock=stock,
            storage=storage,
            ram=ram,
            camera=camera,
            battery=battery,
            display=display,
            image=image_path,
            description=description,
            featured=featured,
            active=True
        )

        try:
            db.session.add(product)
            db.session.commit()
            flash(f"{product.name} was added successfully.", "success")
            return redirect(url_for("admin_products"))
        except Exception as error:
            db.session.rollback()
            if image_path and image_path.startswith("uploads/products/"):
                delete_local_product_image(image_path)
            print("Add product error:", error)
            flash("The product could not be added.", "danger")

    return render_template(
        "admin_product_form.html",
        product=None,
        categories=categories,
        brands=brands,
        form_title="Add Product",
        submit_text="Add Product"
    )
# ==================================================
# ADMIN - EDIT BRAND
# ==================================================

@app.route(
    "/admin/brands/<int:brand_id>/edit",
    methods=["POST"]
)
def admin_edit_brand(brand_id):

    if not admin_is_logged_in():
        flash(
            "Please log in as administrator.",
            "warning"
        )
        return redirect(
            url_for("admin_login")
        )

    brand = Brand.query.get_or_404(brand_id)

    name = request.form.get(
        "name",
        ""
    ).strip()

    description = request.form.get(
        "description",
        ""
    ).strip()

    # ------------------------------------------
    # VALIDATE BRAND NAME
    # ------------------------------------------

    if not name or len(name) > 100:
        flash(
            "Brand name is required.",
            "danger"
        )
        return redirect(
            url_for("admin_brands")
        )

    # ------------------------------------------
    # CHECK FOR DUPLICATE BRAND NAME
    # ------------------------------------------

    existing_brand = (
        Brand.query
        .filter(
            db.func.lower(Brand.name) == name.lower(),
            Brand.id != brand.id
        )
        .first()
    )

    if existing_brand:
        flash(
            f'Another brand named "{name}" already exists.',
            "warning"
        )
        return redirect(
            url_for("admin_brands")
        )

    old_name = brand.name

    try:
        # Update brand
        brand.name = name
        brand.description = description

        # Keep legacy Product.brand text synchronized
        Product.query.filter(
            Product.brand == old_name
        ).update(
            {Product.brand: name},
            synchronize_session=False
        )

        db.session.commit()

        flash(
            f'Brand "{name}" updated successfully.',
            "success"
        )

    except Exception:
        db.session.rollback()

        flash(
            "The brand could not be updated. Please try again.",
            "danger"
        )

    return redirect(
        url_for("admin_brands")
    )
    # ==================================================
# ADMIN - ADD BRAND
# ==================================================

@app.route(
    "/admin/brands/add",
    methods=["POST"]
)
def admin_add_brand():

    if not admin_is_logged_in():
        flash(
            "Please log in as administrator.",
            "warning"
        )
        return redirect(
            url_for("admin_login")
        )

    name = request.form.get(
        "name",
        ""
    ).strip()

    description = request.form.get(
        "description",
        ""
    ).strip()

    # ------------------------------------------
    # VALIDATE BRAND NAME
    # ------------------------------------------

    if not name or len(name) > 100:
        flash(
            "Brand name is required.",
            "danger"
        )
        return redirect(
            url_for("admin_brands")
        )

    # ------------------------------------------
    # PREVENT DUPLICATE BRAND NAMES
    # ------------------------------------------

    existing_brand = (
        Brand.query
        .filter(
            db.func.lower(Brand.name)
            == name.lower()
        )
        .first()
    )

    if existing_brand:
        flash(
            f'Brand "{name}" already exists.',
            "warning"
        )
        return redirect(
            url_for("admin_brands")
        )

    # ------------------------------------------
    # CREATE BRAND
    # ------------------------------------------

    brand = Brand(
        name=name,
        description=description,
        active=True
    )

    try:

        db.session.add(brand)
        db.session.commit()

        flash(
            f'Brand "{brand.name}" added successfully.',
            "success"
        )

    except Exception:

        db.session.rollback()

        flash(
            "The brand could not be added. Please try again.",
            "danger"
        )

    return redirect(
        url_for("admin_brands")
    )

# ==================================================
# ADMIN - ADD PRODUCT
# ==================================================

@app.route(
    "/admin/products/add",
    methods=["GET", "POST"]
)
def admin_add_product():
    return manage_product()

# ==================================================
# ADMIN - EDIT PRODUCT
# ==================================================

@app.route(
    "/admin/products/<int:product_id>/edit",
    methods=["GET", "POST"]
)
def admin_edit_product(product_id):
    return manage_product(product_id)
# ==================================================
# ADMIN - DELETE PRODUCT
# ==================================================

@app.route(
    "/admin/products/<int:product_id>/delete",
    methods=["POST"]
)
def admin_delete_product(product_id):

    if not admin_is_logged_in():
        flash(
            "Please log in as administrator.",
            "warning"
        )
        return redirect(
            url_for("admin_login")
        )

    product = db.session.get(
        Product,
        product_id
    )

    if not product:
        flash(
            "Product not found.",
            "danger"
        )
        return redirect(
            url_for("admin_products")
        )

    # Check whether this product already belongs
    # to any historical order.
    has_order_history = (
        OrderItem.query
        .filter_by(product_id=product.id)
        .first()
        is not None
    )

    if has_order_history:

        # Preserve the product because historical
        # order_item.product_id cannot be NULL.
        product.active = False
        product.featured = False
        product.stock = 0

        db.session.commit()

        flash(
            f"{product.name} has order history, so it was "
            "deactivated instead of permanently deleted.",
            "warning"
        )

        return redirect(
            url_for("admin_products")
        )

    # No order history: related non-historical
    # records can safely be removed.
    WishlistItem.query.filter_by(
        product_id=product.id
    ).delete(
        synchronize_session=False
    )

    Review.query.filter_by(
        product_id=product.id
    ).delete(
        synchronize_session=False
    )

    product_name = product.name
    image_path = product.image

    db.session.delete(product)
    db.session.commit()

    # Delete image only after database deletion succeeds.
    if image_path:
        delete_local_product_image(
            image_path
        )

    flash(
        f"{product_name} deleted successfully.",
        "success"
    )

    return redirect(
        url_for("admin_products")
    )

# ==================================================

# ADMIN - MANAGE ORDERS

# ==================================================



@app.route(

    "/admin/orders",

    methods=["GET"]

)

def admin_orders():
    if not admin_is_logged_in():
        return redirect(url_for('admin_login'))
    selected_status=request.args.get('status','')
    search=request.args.get('search','').strip()
    query=Order.query
    if selected_status in ORDER_STATUSES:
        query=query.filter_by(status=selected_status)
    else:
        selected_status=''
    if search:
        query=query.filter(db.or_(Order.customer_name.contains(search,autoescape=True),Order.phone.contains(search,autoescape=True),db.cast(Order.id,db.String)==search.lstrip('#')))
    return render_template('admin_orders.html',orders=query.order_by(Order.id.desc()).all(),search=search,selected_status=selected_status)





# ==================================================

# ADMIN - UPDATE ORDER STATUS

# ==================================================



@app.route(

    "/admin/orders/<int:order_id>/status",

    methods=["POST"]

)

def admin_update_order_status(order_id):
    if not admin_is_logged_in():
        return redirect(url_for('admin_login'))
    order=db.get_or_404(Order,order_id)
    status=request.form.get('status','')
    payment=request.form.get('payment_status',order.payment_status)
    if status not in ORDER_STATUSES or payment not in ('Pending','Paid','Failed','Refunded'):
        flash('Invalid order or payment status.','danger')
    elif request.form.get('original_status',order.status)!=order.status:
        flash('This order changed. Review its current status before saving.','warning')
    else:
        if 'estimated_delivery' in request.form:
            raw=request.form.get('estimated_delivery','').strip()
            try: estimate=datetime.strptime(raw,'%Y-%m-%d').date() if raw else None
            except ValueError:
                flash('Enter a valid delivery date.','danger')
                return redirect(url_for('admin_order_detail',order_id=order.id))
            delivery=db.session.get(OrderDelivery,order.id) or OrderDelivery(order_id=order.id)
            delivery.estimated_delivery=estimate;db.session.add(delivery)
        order.status=status
        order.payment_status=payment
        order.tracking_status={'Pending':'Order Received','Processing':'Preparing Order','Shipped':'Out for Delivery','Delivered':'Delivered','Cancelled':'Cancelled'}[status]
        if commit_admin_change('Order updated.') and order.user_id:
            from push_delivery import send_push
            for subscription in PushSubscription.query.filter_by(user_id=order.user_id):
                send_push(json.loads(subscription.subscription),{'title':'Lift Store order update','body':f'Order #{order.id}: {order.tracking_status}','url':url_for('customer_order',order_id=order.id)})
    if request.form.get('return_to') == 'orders':
        return redirect(url_for('admin_orders', search=request.form.get('search',''), status=request.form.get('filter_status','')))
    return redirect(url_for('admin_order_detail',order_id=order.id))





# ==================================================

# ADMIN - VIEW ORDER DETAILS

# ==================================================



@app.route(

    "/admin/orders/<int:order_id>",

    methods=["GET"]

)

def admin_order_detail(order_id):



    if not admin_is_logged_in():



        flash(

            "Please login as administrator.",

            "warning"

        )



        return redirect(

            url_for("admin_login")

        )



    order = Order.query.get_or_404(

        order_id

    )



    return render_template(

        "admin_order_detail.html",

        order=order

    )





# ==================================================

# ADMIN - CUSTOMER MANAGEMENT

# ==================================================



@app.route(

    "/admin/customers",

    methods=["GET"]

)

def admin_customers():



    if not admin_is_logged_in():



        flash(

            "Please login as administrator.",

            "warning"

        )



        return redirect(

            url_for("admin_login")

        )



    search = request.args.get(

        "search",

        ""

    ).strip()



    query = User.query



    if search:



        query = query.filter(

            db.or_(

                User.name.ilike(

                    f"%{search}%"

                ),

                User.email.ilike(

                    f"%{search}%"

                )

            )

        )



    customers = (

        query

        .order_by(User.id.desc())

        .all()

    )



    return render_template(

        "admin_customers.html",

        customers=customers,

        search=search

    )



# ==================================================

# ADMIN LOGOUT

# ==================================================



@app.route("/admin/logout")

def admin_logout():
    session.clear()



    session.pop(

        "admin_logged_in",

        None

    )



    session.pop(

        "admin_email",

        None

    )



    flash(

        "Administrator logged out successfully.",

        "success"

    )



    return redirect(

        url_for("admin_login")

    )





# ==================================================
# GLOBAL TEMPLATE DATA
# ==================================================

@app.context_processor
def inject_store_data():

    cart_data = session.get("cart", {})

    try:
        cart_total_count = sum(
            int(quantity)
            for quantity in cart_data.values()
        )
    except (TypeError, ValueError):
        cart_total_count = 0

    try:
        nav_categories = (
            Category.query
            .filter_by(active=True)
            .order_by(Category.name.asc())
            .all()
        )

        nav_brands = (
            Brand.query
            .filter_by(active=True)
            .order_by(Brand.name.asc())
            .all()
        )

    except Exception:
        nav_categories = []
        nav_brands = []

    wishlist_count = 0

    if session.get("user_id"):

        wishlist_count = WishlistItem.query.filter_by(
            user_id=session["user_id"]
        ).count()

    store_settings = StoreSetting.query.first()

    return {
        "cart_count": cart_total_count,
        "wishlist_count": wishlist_count,
        "nav_categories": nav_categories,
        "nav_brands": nav_brands,
        "store_settings": store_settings
    }





@app.template_filter("ugx")

def ugx(value):



    try:



        return (

            f"UGX {float(value):,.0f}"

        )



    except (TypeError, ValueError):



        return "UGX 0"





# ==================================================

# CREATE DATABASE AND START APPLICATION

# ==================================================



# ==================================================

# START APPLICATION

# ==================================================



# ==================================================
# ADMIN - INVENTORY
# ==================================================

@app.route("/admin/inventory", methods=["GET"])
def admin_inventory():
    if not admin_is_logged_in():
        flash("Please log in as administrator.", "warning")
        return redirect(url_for("admin_login"))

    search = request.args.get("search", "").strip()
    stock_filter = request.args.get("stock_filter", "")
    if stock_filter not in ("", "in", "low", "out"):
        stock_filter = ""

    query = Product.query
    if search:
        query = query.filter(db.or_(
            Product.name.contains(search, autoescape=True),
            Product.brand.contains(search, autoescape=True),
            Product.category.contains(search, autoescape=True),
        ))
    quantity = db.func.coalesce(Product.stock, 0)
    if stock_filter == "in":
        query = query.filter(quantity > 5)
    elif stock_filter == "low":
        query = query.filter(quantity.between(1, 5))
    elif stock_filter == "out":
        query = query.filter(quantity <= 0)

    products = query.order_by(Product.name.asc(), Product.id.asc()).all()

    total_products = Product.query.count()

    low_stock_count = (
        Product.query
        .filter(Product.stock > 0, Product.stock <= 5)
        .count()
    )

    out_of_stock_count = (
        Product.query
        .filter(Product.stock <= 0)
        .count()
    )

    total_stock_units = (
        db.session.query(
            db.func.coalesce(db.func.sum(Product.stock), 0)
        )
        .scalar()
    )

    inventory_value = (
        db.session.query(
            db.func.coalesce(
                db.func.sum(Product.price * Product.stock),
                0
            )
        )
        .scalar()
    )

    return render_template(
        "admin_inventory.html", products=products,
        search=search, stock_filter=stock_filter,
        total_products=total_products, low_stock_count=low_stock_count,
        out_of_stock_count=out_of_stock_count, total_stock_units=total_stock_units,
        inventory_value=inventory_value,
    )


@app.route("/admin/inventory/<int:product_id>/stock", methods=["POST"])
def admin_update_stock(product_id):
    if not admin_is_logged_in():
        flash("Please log in as administrator.", "warning")
        return redirect(url_for("admin_login"))

    product = Product.query.get_or_404(product_id)
    destination = url_for(
        "admin_inventory",
        search=request.form.get("search", "").strip(),
        stock_filter=request.form.get("stock_filter", ""),
    )
    raw_stock = request.form.get("stock", "").strip()
    original = request.form.get("original_stock", "")
    if (not raw_stock.isascii() or not raw_stock.isdecimal()
            or len(raw_stock) > 10 or int(raw_stock) > 2147483647):
        flash("Enter a whole-number stock quantity from 0 to 2,147,483,647.", "danger")
        return redirect(destination)

    # Compare against the displayed quantity to avoid overwriting newer changes.
    if original == "none":
        stock_matches = Product.stock.is_(None)
    else:
        try:
            if len(original) > 11:
                raise ValueError
            original_quantity = int(original)
            if not -2147483648 <= original_quantity <= 2147483647:
                raise ValueError
        except (TypeError, ValueError):
            flash("Reload inventory before updating stock.", "warning")
            return redirect(destination)
        stock_matches = Product.stock == original_quantity

    product_name = product.name
    try:
        changed = Product.query.filter(
            Product.id == product_id, stock_matches,
        ).update({Product.stock: int(raw_stock)}, synchronize_session=False)
        if changed != 1:
            db.session.rollback()
            flash("Stock changed since this page was loaded. Review the latest quantity and try again.", "warning")
        else:
            db.session.commit()
            flash(f"Stock for {product_name} updated to {int(raw_stock)}.", "success")
    except Exception:
        db.session.rollback()
        app.logger.exception("Inventory stock update failed")
        flash("Stock could not be updated. Please try again.", "danger")
    return redirect(destination)




# Admin review moderation, coupon management and delivery areas.
from functools import wraps
from sqlalchemy.exc import IntegrityError
import re

def admin_required(view):
    @wraps(view)
    def secured(*args, **kwargs):
        if not admin_is_logged_in():
            flash("Please log in as administrator.", "warning")
            return redirect(url_for("admin_login"))
        return view(*args, **kwargs)
    return secured

def commit_admin_change(message):
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        flash("That name or code is already in use.", "danger")
        return False
    except Exception:
        db.session.rollback()
        app.logger.exception("Admin change failed")
        flash("Changes could not be saved. Please try again.", "danger")
        return False
    flash(message, "success")
    return True

@app.route('/admin/reviews')
@admin_required
def admin_reviews():
    search = request.args.get('search', '').strip()
    status = request.args.get('status', '')
    query = Review.query.outerjoin(Product).outerjoin(User)
    if search:
        query = query.filter(db.or_(Product.name.contains(search, autoescape=True), User.name.contains(search, autoescape=True), Review.comment.contains(search, autoescape=True)))
    if status in ('approved', 'hidden'):
        query = query.filter(Review.approved == (status == 'approved'))
    else:
        status = ''
    return render_template('admin_reviews.html', reviews=query.order_by(Review.created_at.desc(), Review.id.desc()).all(), search=search, status=status)

@app.route('/admin/reviews/<int:review_id>/visibility', methods=['POST'])
@admin_required
def admin_review_visibility(review_id):
    review = db.get_or_404(Review, review_id)
    action = request.form.get('action')
    if action not in ('approve', 'hide'):
        flash('Invalid review action.', 'danger')
    else:
        review.approved = action == 'approve'
        commit_admin_change('Review approved.' if review.approved else 'Review hidden.')
    return redirect(url_for('admin_reviews', search=request.form.get('search', ''), status=request.form.get('status', '')))

def admin_integer(name, label, maximum=2147483647):
    raw = request.form.get(name, '').strip()
    if not raw.isascii() or not raw.isdecimal() or len(raw) > 10 or int(raw) > maximum:
        raise ValueError(f'{label} must be a whole number from 0 to {maximum:,}.')
    return int(raw)

@app.route('/admin/coupons')
@admin_required
def admin_coupons():
    return render_template('admin_coupons.html', coupons=Coupon.query.order_by(Coupon.code).all(), now=datetime.utcnow())

@app.route('/admin/coupons/new', methods=['GET', 'POST'])
@app.route('/admin/coupons/<int:coupon_id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_coupon_form(coupon_id=None):
    coupon = db.get_or_404(Coupon, coupon_id) if coupon_id else None
    if request.method == 'POST':
        try:
            code = request.form.get('code', '').strip().upper()
            if not re.fullmatch(r'[A-Z0-9_-]{1,50}', code):
                raise ValueError('Use 1–50 letters, numbers, hyphens or underscores for the code.')
            discount = admin_integer('discount_percent', 'Discount', 100)
            if discount == 0:
                raise ValueError('Discount must be between 1 and 100 percent.')
            minimum = admin_integer('minimum_order', 'Minimum order')
            dates = []
            for field in ('start_date', 'end_date'):
                raw = request.form.get(field, '').strip()
                try:
                    dates.append(datetime.strptime(raw, '%Y-%m-%dT%H:%M') if raw else None)
                except ValueError:
                    raise ValueError('Enter a valid date and time.')
            if all(dates) and dates[1] <= dates[0]:
                raise ValueError('End time must be after start time.')
            duplicate = Coupon.query.filter(db.func.lower(Coupon.code) == code.lower())
            if coupon:
                duplicate = duplicate.filter(Coupon.id != coupon.id)
            if duplicate.first():
                raise ValueError('That coupon code is already in use.')
            record = coupon or Coupon()
            record.code, record.discount_percent, record.minimum_order = code, discount, minimum
            record.start_date, record.end_date = dates
            record.active = request.form.get('active') == 'on'
            if coupon is None:
                db.session.add(record)
            if commit_admin_change('Coupon saved.'):
                return redirect(url_for('admin_coupons'))
        except ValueError as error:
            flash(str(error), 'danger')
    return render_template('admin_coupon_form.html', coupon=coupon)

@app.route('/admin/coupons/<int:coupon_id>/active', methods=['POST'])
@admin_required
def admin_coupon_active(coupon_id):
    record = db.get_or_404(Coupon, coupon_id)
    if request.form.get('active') not in ('0', '1'):
        flash('Invalid status.', 'danger')
    else:
        record.active = request.form['active'] == '1'
        commit_admin_change('Coupon status updated.')
    return redirect(url_for('admin_coupons'))

@app.route('/admin/delivery-areas')
@admin_required
def admin_delivery_areas():
    return render_template('admin_delivery_areas.html', areas=DeliveryArea.query.order_by(DeliveryArea.name).all())

@app.route('/admin/delivery-areas/new', methods=['GET', 'POST'])
@app.route('/admin/delivery-areas/<int:area_id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_delivery_area_form(area_id=None):
    area = db.get_or_404(DeliveryArea, area_id) if area_id else None
    if request.method == 'POST':
        try:
            name = request.form.get('name', '').strip()
            if not name or len(name) > 120:
                raise ValueError('Area name must contain 1–120 characters.')
            fee = admin_integer('fee', 'Delivery fee')
            duplicate = DeliveryArea.query.filter(db.func.lower(DeliveryArea.name) == name.lower())
            if area:
                duplicate = duplicate.filter(DeliveryArea.id != area.id)
            if duplicate.first():
                raise ValueError('That delivery area already exists.')
            record = area or DeliveryArea()
            record.name, record.fee = name, fee
            record.active = request.form.get('active') == 'on'
            if area is None:
                db.session.add(record)
            if commit_admin_change('Delivery area saved.'):
                return redirect(url_for('admin_delivery_areas'))
        except ValueError as error:
            flash(str(error), 'danger')
    return render_template('admin_delivery_area_form.html', area=area)

@app.route('/admin/delivery-areas/<int:area_id>/active', methods=['POST'])
@admin_required
def admin_delivery_area_active(area_id):
    record = db.get_or_404(DeliveryArea, area_id)
    if request.form.get('active') not in ('0', '1'):
        flash('Invalid status.', 'danger')
    else:
        record.active = request.form['active'] == '1'
        commit_admin_change('Delivery area status updated.')
    return redirect(url_for('admin_delivery_areas'))


ORDER_STATUSES=('Pending','Processing','Shipped','Delivered','Cancelled')

@app.context_processor
def admin_template_options():
    return {'order_statuses':ORDER_STATUSES}

def manage_product(product_id=None):
    if not admin_is_logged_in():
        return redirect(url_for('admin_login'))
    product=db.get_or_404(Product,product_id) if product_id else None
    categories=Category.query.order_by(Category.name).all()
    brands=Brand.query.order_by(Brand.name).all()
    if request.method=='POST':
        uploaded=None
        try:
            name=request.form.get('name','').strip()
            if not name or len(name)>120:
                raise ValueError('Product name must contain 1–120 characters.')
            price=admin_integer('price','Price')
            stock=admin_integer('stock','Stock')
            old_price=admin_integer('old_price','Previous price') if request.form.get('old_price','').strip() else None
            selected={}
            for key,model in [('category',Category),('brand',Brand)]:
                raw=request.form.get(key+'_id','')
                record=db.session.get(model,int(raw)) if raw.isascii() and raw.isdecimal() and len(raw)<10 else None
                if not record or (not record.active and (not product or getattr(product,key+'_id')!=record.id)):
                    raise ValueError('Choose an active '+key+'.')
                selected[key]=record
            values={}
            for key,limit in [('storage',30),('ram',30),('camera',80),('battery',50),('display',80),('description',10000)]:
                values[key]=request.form.get(key,'').strip()
                if len(values[key])>limit:
                    raise ValueError(f'{key.title()} is too long (maximum {limit} characters).')
            uploaded=save_product_image(request.files.get('image'))
            record=product or Product()
            old_image=record.image
            record.name,record.price,record.stock,record.old_price=name,price,stock,old_price
            for key,value in values.items(): setattr(record,key,value)
            for key,value in selected.items():
                setattr(record,key,value.name);setattr(record,key+'_id',value.id)
            record.active=request.form.get('active')=='on'
            record.featured=request.form.get('featured')=='on'
            if uploaded: record.image=uploaded
            if not product: db.session.add(record)
            db.session.commit()
            if uploaded and old_image: delete_local_product_image(old_image)
            flash('Product saved.','success')
            return redirect(url_for('admin_products'))
        except ValueError as error:
            db.session.rollback()
            if uploaded: delete_local_product_image(uploaded)
            flash(str(error),'danger')
        except Exception:
            db.session.rollback()
            if uploaded: delete_local_product_image(uploaded)
            app.logger.exception('Product save failed')
            flash('Product could not be saved. Please try again.','danger')
    return render_template('admin_product_form.html',product=product,categories=categories,brands=brands,form_title='Edit Product' if product else 'Add Product',submit_text='Save Product')

@app.route('/admin/customers/<int:customer_id>')
@admin_required
def admin_customer_detail(customer_id):
    customer=db.get_or_404(User,customer_id)
    orders=Order.query.filter_by(user_id=customer.id).order_by(Order.id.desc()).all()
    return render_template('admin_customer_detail.html',customer=customer,orders=orders)

@app.route('/admin/settings',methods=['GET','POST'])
@admin_required
def admin_settings():
    settings=StoreSetting.query.first()
    if request.method=='POST':
        try:
            values={}
            for key,limit in [('store_name',120),('phone',30),('whatsapp',30),('email',150),('address',250),('opening_hours',250),('delivery_message',1000),('hero_title',200),('hero_subtitle',300)]:
                value=request.form.get(key,'').strip()
                if len(value)>limit: raise ValueError(f'{key.replace("_"," ").title()} must be {limit} characters or fewer.')
                values[key]=value
            if not values['store_name']: raise ValueError('Store name is required.')
            if values['email'] and not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+',values['email']):
                raise ValueError('Enter a valid contact email.')
            record=settings or StoreSetting()
            for key,value in values.items(): setattr(record,key,value)
            record.currency='UGX'
            if not settings: db.session.add(record)
            if commit_admin_change('Store settings saved.'):
                return redirect(url_for('admin_settings'))
        except ValueError as error:
            flash(str(error),'danger')
    return render_template('admin_settings.html',settings=settings)



from flask import send_file, abort
from pathlib import Path
import struct, zlib, binascii
import io

def profile_admin():
    if not admin_is_logged_in():
        return None
    return db.session.get(Admin, session.get('admin_id')) if session.get('admin_id') else None

def profile_photo_path(admin):
    return Path(app.config.get('ADMIN_PROFILE_FOLDER', os.path.join(app.instance_path, 'admin_profiles'))) / f'{admin.id}.png'

@app.context_processor
def inject_admin_profile():
    admin=profile_admin()
    path=profile_photo_path(admin) if admin else None
    return {'profile_admin':admin, 'profile_photo_version':path.stat().st_mtime_ns if path and path.is_file() else None}

@app.route('/admin/profile',methods=['GET','POST'])
@admin_required
def admin_profile():
    admin=profile_admin()
    if not admin:
        flash('Please sign in again to manage your profile.', 'warning')
        return redirect(url_for('admin_login'))
    if request.method=='POST':
        temporary=None
        try:
            upload=request.files.get('photo')
            if not upload or not upload.filename:
                raise ValueError('Choose a profile photo first.')
            data=upload.read(2*1024*1024+1)
            if len(data)>2*1024*1024:
                raise ValueError('Choose an image smaller than 2 MB.')
            if not data.startswith(b'\x89PNG\r\n\x1a\n'):
                raise ValueError('Please select the photo again and allow the preview to load.')
            offset=8
            cleaned=bytearray(data[:8])
            compressed=bytearray()
            width=height=channels=0
            ended=False
            while offset+12<=len(data):
                length=struct.unpack('>I',data[offset:offset+4])[0]
                kind=data[offset+4:offset+8]
                payload=data[offset+8:offset+8+length]
                if offset+12+length>len(data): raise ValueError('Invalid photo.')
                crc=struct.unpack('>I',data[offset+8+length:offset+12+length])[0]
                if binascii.crc32(kind+payload)&0xffffffff != crc: raise ValueError('Invalid photo.')
                if kind==b'IHDR':
                    if offset!=8 or length!=13: raise ValueError('Invalid photo.')
                    width,height,depth,color,compression,filtering,interlace=struct.unpack('>IIBBBBB',payload)
                    if not (1<=width<=512 and 1<=height<=512 and depth==8 and color in (2,6) and compression==filtering==interlace==0):
                        raise ValueError('Please use the photo picker to resize your image.')
                    channels=3 if color==2 else 4
                elif kind==b'IDAT': compressed.extend(payload)
                elif kind==b'IEND':
                    if length: raise ValueError('Invalid photo.')
                    ended=True
                elif kind[0]&32==0: raise ValueError('Unsupported photo format.')
                if kind in (b'IHDR',b'IDAT',b'IEND'): cleaned.extend(data[offset:offset+12+length])
                offset+=12+length
                if ended: break
            expected=height*(1+width*channels)
            decoder=zlib.decompressobj()
            pixels=decoder.decompress(bytes(compressed),expected+1)
            if not ended or not channels or len(pixels)!=expected or not decoder.eof:
                raise ValueError('Invalid photo.')
            path=profile_photo_path(admin)
            path.parent.mkdir(parents=True,exist_ok=True)
            temporary=path.with_name(uuid.uuid4().hex+'.tmp')
            temporary.write_bytes(cleaned)
            os.replace(temporary,path)
            flash('Profile photo updated.', 'success')
            return redirect(url_for('admin_profile'))
        except (OSError,ValueError,struct.error,zlib.error) as error:
            if temporary and temporary.exists(): temporary.unlink()
            flash(str(error) if isinstance(error,ValueError) else 'The image could not be saved. Choose a valid JPG, PNG or WEBP image.', 'danger')
    return render_template('admin_profile.html',admin=admin)

@app.route('/admin/profile/photo')
@admin_required
def admin_profile_photo():
    admin=profile_admin()
    if not admin or not profile_photo_path(admin).is_file(): abort(404)
    response=send_file(io.BytesIO(profile_photo_path(admin).read_bytes()),mimetype='image/png')
    response.headers['Cache-Control']='private, no-store'
    return response



def current_customer():
    customer=db.session.get(User,session.get('user_id')) if session.get('user_id') else None
    return customer if customer and customer.active is not False else None

def customer_photo_path(customer):
    return Path(app.config.get('CUSTOMER_PROFILE_FOLDER',os.path.join(app.instance_path,'customer_profiles'))) / f'{customer.id}.png'

@app.context_processor
def inject_customer_profile():
    customer=current_customer()
    path=customer_photo_path(customer) if customer else None
    return {'profile_customer':customer,'customer_photo_version':path.stat().st_mtime_ns if path and path.is_file() else None}

@app.route('/account/profile',methods=['GET','POST'])
def customer_profile():
    customer=current_customer()
    if not customer:
        flash('Please sign in again to manage your profile.', 'warning')
        return redirect(url_for('login'))
    if request.method=='POST':
        temporary=None
        try:
            upload=request.files.get('photo')
            if not upload or not upload.filename:
                raise ValueError('Choose a profile photo first.')
            data=upload.read(2*1024*1024+1)
            if len(data)>2*1024*1024:
                raise ValueError('Choose an image smaller than 2 MB.')
            if not data.startswith(b'\x89PNG\r\n\x1a\n'):
                raise ValueError('Please select the photo again and allow the preview to load.')
            offset=8
            cleaned=bytearray(data[:8])
            compressed=bytearray()
            width=height=channels=0
            ended=False
            while offset+12<=len(data):
                length=struct.unpack('>I',data[offset:offset+4])[0]
                kind=data[offset+4:offset+8]
                payload=data[offset+8:offset+8+length]
                if offset+12+length>len(data): raise ValueError('Invalid photo.')
                crc=struct.unpack('>I',data[offset+8+length:offset+12+length])[0]
                if binascii.crc32(kind+payload)&0xffffffff != crc: raise ValueError('Invalid photo.')
                if kind==b'IHDR':
                    if offset!=8 or length!=13: raise ValueError('Invalid photo.')
                    width,height,depth,color,compression,filtering,interlace=struct.unpack('>IIBBBBB',payload)
                    if not (1<=width<=512 and 1<=height<=512 and depth==8 and color in (2,6) and compression==filtering==interlace==0):
                        raise ValueError('Please use the photo picker to resize your image.')
                    channels=3 if color==2 else 4
                elif kind==b'IDAT': compressed.extend(payload)
                elif kind==b'IEND':
                    if length: raise ValueError('Invalid photo.')
                    ended=True
                elif kind[0]&32==0: raise ValueError('Unsupported photo format.')
                if kind in (b'IHDR',b'IDAT',b'IEND'): cleaned.extend(data[offset:offset+12+length])
                offset+=12+length
                if ended: break
            expected=height*(1+width*channels)
            decoder=zlib.decompressobj()
            pixels=decoder.decompress(bytes(compressed),expected+1)
            if not ended or not channels or len(pixels)!=expected or not decoder.eof:
                raise ValueError('Invalid photo.')
            path=customer_photo_path(customer)
            path.parent.mkdir(parents=True,exist_ok=True)
            temporary=path.with_name(uuid.uuid4().hex+'.tmp')
            temporary.write_bytes(cleaned)
            os.replace(temporary,path)
            flash('Profile photo updated.', 'success')
            return redirect(url_for('customer_profile'))
        except (OSError,ValueError,struct.error,zlib.error) as error:
            if temporary and temporary.exists(): temporary.unlink()
            flash(str(error) if isinstance(error,ValueError) else 'The image could not be saved. Choose a valid JPG, PNG or WEBP image.', 'danger')
    return render_template('customer_profile.html',customer=customer)

@app.route('/account/profile/photo')
def customer_profile_photo():
    customer=current_customer()
    if not customer: return redirect(url_for('login'))
    path=customer_photo_path(customer)
    if not path.is_file(): abort(404)
    response=send_file(io.BytesIO(path.read_bytes()),mimetype='image/png')
    response.headers['Cache-Control']='private, no-store'
    return response

# Customer account, catalogue and delivery services.
import re
import json
from urllib.parse import urlparse
from flask import jsonify
from sqlalchemy.exc import IntegrityError

class OrderDelivery(db.Model):
    order_id=db.Column(db.Integer,db.ForeignKey('order.id'),primary_key=True)
    estimated_delivery=db.Column(db.Date)

class PushSubscription(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False,index=True)
    endpoint=db.Column(db.Text,unique=True,nullable=False)
    subscription=db.Column(db.Text,nullable=False)
    promotions=db.Column(db.Boolean,default=False,nullable=False)

@app.cli.command('init-customer-features')
def init_customer_features():
    OrderDelivery.__table__.create(db.engine,checkfirst=True)
    PushSubscription.__table__.create(db.engine,checkfirst=True)
    for model in (SavedAddress,SavedCart,OrderDiscount,SupportRequest): model.__table__.create(db.engine,checkfirst=True)
    print('Customer feature tables are ready.')

def normalize_phone(value):
    number=re.sub(r'[\s()\-]','',value)
    if number.startswith('0') and len(number)==10: number='+256'+number[1:]
    elif number.startswith('256') and len(number)==12: number='+'+number
    if not re.fullmatch(r'\+[1-9][0-9]{7,14}',number): raise ValueError('Enter a valid phone number, including the country code.')
    return number

def account_identity(value):
    if '@' in value:
        email=value.lower()
        if len(email)>150 or not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+',email) or email.endswith('@accounts.invalid'):
            raise ValueError('Enter a valid email address.')
        return email,None
    return None,normalize_phone(value)

def find_customer(value):
    try: email,phone=account_identity(value)
    except ValueError: return None
    if email: return User.query.filter(db.func.lower(User.email)==email).first()
    # Also support phone formats already stored by the existing admin.
    matches=[]
    for user in User.query.filter(User.phone.isnot(None)).all():
        try:
            if normalize_phone(user.phone)==phone: matches.append(user)
        except ValueError: pass
    return matches[0] if len(matches)==1 else None

@app.route('/account/details',methods=['POST'])
def customer_details():
    customer=current_customer()
    if not customer: return redirect(url_for('login'))
    try:
        if not check_password_hash(customer.password,request.form.get('current_password','')): raise ValueError('Enter your current password to save account details.')
        name=request.form.get('name','').strip();email=request.form.get('email','').strip();phone=request.form.get('phone','').strip()
        if not name or len(name)>100: raise ValueError('Enter your name, up to 100 characters.')
        if not email and not phone: raise ValueError('Keep at least an email address or a phone number.')
        email=account_identity(email)[0] if email else None
        phone=normalize_phone(phone) if phone else None
        for identity in (email,phone):
            if identity and identity_in_use(identity,exclude_id=customer.id): raise ValueError('These contact details already belong to another account.')
        customer.name=name;customer.email=email or ('phone-'+phone+'@accounts.invalid');customer.phone=phone
        db.session.commit();session['user_name']=name;flash('Account details saved.','success')
    except ValueError as error: flash(str(error),'danger')
    except IntegrityError:
        db.session.rollback();flash('These contact details already belong to another account.','danger')
    return redirect(url_for('customer_profile'))

@app.route('/api/products/suggestions')
def product_suggestions():
    query=request.args.get('q','').strip()[:100]
    if len(query)<2: return jsonify([])
    products=Product.query.filter(Product.active.is_(True),Product.name.ilike('%'+query+'%')).order_by(Product.name).limit(8).all()
    return jsonify([{'name':p.name,'url':url_for('product_detail',product_id=p.id)} for p in products])

@app.route('/product/<int:product_id>/review',methods=['POST'])
def customer_review(product_id):
    customer=current_customer()
    if not customer: return redirect(url_for('login'))
    product=Product.query.filter_by(id=product_id,active=True).first_or_404()
    rating=request.form.get('rating',type=int);comment=request.form.get('comment','').strip()
    if rating not in range(1,6) or not comment or len(comment)>2000:
        flash('Choose a rating from 1 to 5 and write a review of up to 2,000 characters.','danger')
    else:
        review=Review.query.filter_by(user_id=customer.id,product_id=product.id).first()
        if not review: review=Review(user_id=customer.id,product_id=product.id)
        review.rating=rating;review.comment=comment;review.approved=False
        db.session.add(review);db.session.commit();flash('Thank you. Your review is awaiting approval.','success')
    return redirect(url_for('product_detail',product_id=product.id)+'#reviews')

def accessible_order(order_id):
    order=db.get_or_404(Order,order_id);customer=current_customer()
    if order.user_id:
        if not customer or customer.id!=order.user_id: abort(404)
    elif order.id not in session.get('guest_order_ids',[]): abort(404)
    return order

def delivery_payload(order):
    delivery=db.session.get(OrderDelivery,order.id)
    return {'id':order.id,'status':order.status,'tracking':order.tracking_status,'payment':order.payment_status,
            'estimate':delivery.estimated_delivery.isoformat() if delivery and delivery.estimated_delivery else 'Awaiting confirmation',
            'updated':order.updated_at.isoformat() if order.updated_at else ''}

@app.route('/account/orders')
def customer_orders():
    customer=current_customer()
    if not customer: return redirect(url_for('login'))
    orders=Order.query.filter_by(user_id=customer.id).order_by(Order.created_at.desc()).all()
    return render_template('customer_orders.html',orders=orders)

@app.route('/account/orders/<int:order_id>')
def customer_order(order_id):
    order=accessible_order(order_id)
    return render_template('customer_order.html',order=order,progress=delivery_payload(order))

@app.route('/api/account/orders/<int:order_id>')
def customer_order_updates(order_id):
    response=jsonify(delivery_payload(accessible_order(order_id)))
    response.headers['Cache-Control']='private, no-store'
    return response

@app.context_processor
def customer_feature_context():
    return {'push_available':bool(os.environ.get('VAPID_PUBLIC_KEY') and os.environ.get('VAPID_PRIVATE_KEY') and os.environ.get('VAPID_SUBJECT')),
            'order_estimate':lambda order_id: (db.session.get(OrderDelivery,order_id).estimated_delivery if db.session.get(OrderDelivery,order_id) else None)}

@app.route('/service-worker.js')
def customer_service_worker():
    response=send_file(os.path.join(app.static_folder,'js','service-worker.js'),mimetype='application/javascript')
    response.headers['Cache-Control']='no-cache'
    return response

@app.route('/api/push/config')
def push_config():
    if not current_customer(): abort(401)
    configured=bool(os.environ.get('VAPID_PRIVATE_KEY') and os.environ.get('VAPID_SUBJECT'))
    return jsonify(publicKey=os.environ.get('VAPID_PUBLIC_KEY','') if configured else '')

@app.route('/api/push/subscription',methods=['POST','DELETE'])
def push_subscription():
    customer=current_customer()
    if not customer: abort(401)
    data=request.get_json(silent=True) or {};subscription=data.get('subscription',{});endpoint=subscription.get('endpoint','')
    host=urlparse(endpoint).hostname or ''
    allowed=('fcm.googleapis.com','updates.push.services.mozilla.com','web.push.apple.com')
    if urlparse(endpoint).scheme!='https' or not any(host==h or host.endswith('.'+h) for h in allowed) or len(endpoint)>2048:
        return jsonify(error='Unsupported push service.'),400
    existing=PushSubscription.query.filter_by(endpoint=endpoint).first()
    if existing and existing.user_id!=customer.id: abort(403)
    if request.method=='DELETE':
        if existing: db.session.delete(existing);db.session.commit()
        return jsonify(ok=True)
    if not os.environ.get('VAPID_PUBLIC_KEY'): return jsonify(error='Notifications are not available yet.'),503
    keys=subscription.get('keys',{})
    if not all(isinstance(keys.get(k),str) and 10<=len(keys[k])<=256 for k in ('p256dh','auth')): abort(400)
    if not existing and PushSubscription.query.filter_by(user_id=customer.id).count()>=10: return jsonify(error='Device limit reached.'),400
    row=existing or PushSubscription(user_id=customer.id,endpoint=endpoint)
    row.subscription=json.dumps({'endpoint':endpoint,'keys':keys});row.promotions=data.get('promotions') is True
    db.session.add(row);db.session.commit();return jsonify(ok=True)

@app.cli.command('send-promotion')
@__import__('click').argument('message')
def send_promotion(message):
    """Send a real promotion only to explicitly opted-in customers."""
    from push_delivery import send_push
    delivered=0
    for row in PushSubscription.query.filter_by(promotions=True):
        if send_push(json.loads(row.subscription),{'title':'Lift Store offers','body':message[:200],'url':'/#products'}): delivered+=1
    print(f'Sent to {delivered} subscriptions.')

class SavedAddress(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False,index=True)
    label=db.Column(db.String(60),nullable=False)
    recipient=db.Column(db.String(100),nullable=False)
    phone=db.Column(db.String(30),nullable=False)
    location=db.Column(db.String(200),nullable=False)

class SavedCart(db.Model):
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'),primary_key=True)
    contents=db.Column(db.Text,nullable=False,default='{}')

class OrderDiscount(db.Model):
    order_id=db.Column(db.Integer,db.ForeignKey('order.id'),primary_key=True)
    code=db.Column(db.String(50),nullable=False)
    amount=db.Column(db.Integer,nullable=False)

class SupportRequest(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    order_id=db.Column(db.Integer,db.ForeignKey('order.id'),nullable=False)
    kind=db.Column(db.String(30),nullable=False)
    message=db.Column(db.Text,nullable=False)
    status=db.Column(db.String(30),default='Open',nullable=False)
    created_at=db.Column(db.DateTime,default=datetime.utcnow)

@app.before_request
def restore_customer_cart():
    if session.get('user_id') and 'cart' not in session:
        row=db.session.get(SavedCart,session['user_id'])
        if row: session['cart']=json.loads(row.contents)

@app.after_request
def persist_customer_cart(response):
    if session.get('user_id') and session.modified and 'cart' in session:
        row=db.session.get(SavedCart,session['user_id']) or SavedCart(user_id=session['user_id'])
        row.contents=json.dumps(session['cart']);db.session.add(row)
        try: db.session.commit()
        except Exception:
            db.session.rollback();app.logger.exception('Could not save customer cart')
    return response

def merge_saved_cart(customer):
    row=db.session.get(SavedCart,customer.id)
    saved=json.loads(row.contents) if row else {}
    for product_id,quantity in session.get('cart',{}).items(): saved[product_id]=max(int(saved.get(product_id,0)),int(quantity))
    session['cart']=saved

@app.route('/account/addresses',methods=['GET','POST'])
def customer_addresses():
    customer=current_customer()
    if not customer: return redirect(url_for('login'))
    if request.method=='POST':
        try:
            fields={key:request.form.get(key,'').strip() for key in ('label','recipient','phone','location')}
            for key,limit in [('label',60),('recipient',100),('location',200)]:
                if not fields[key] or len(fields[key])>limit: raise ValueError('Complete all address fields within the allowed length.')
            fields['phone']=normalize_phone(fields['phone'])
            if SavedAddress.query.filter_by(user_id=customer.id).count()>=10: raise ValueError('You can save up to ten addresses.')
            db.session.add(SavedAddress(user_id=customer.id,**fields));db.session.commit();flash('Address saved.','success')
            return redirect(url_for('customer_addresses'))
        except ValueError as error: flash(str(error),'danger')
    return render_template('customer_addresses.html',addresses=SavedAddress.query.filter_by(user_id=customer.id).all())

@app.route('/account/addresses/<int:address_id>/remove',methods=['POST'])
def remove_address(address_id):
    customer=current_customer()
    if not customer: return redirect(url_for('login'))
    row=SavedAddress.query.filter_by(id=address_id,user_id=customer.id).first_or_404()
    db.session.delete(row);db.session.commit();return redirect(url_for('customer_addresses'))

@app.route('/account/wishlist')
def customer_wishlist():
    customer=current_customer()
    if not customer: return redirect(url_for('login'))
    return render_template('customer_wishlist.html',items=WishlistItem.query.filter_by(user_id=customer.id).order_by(WishlistItem.created_at.desc()).all())

@app.route('/account/wishlist/<int:product_id>',methods=['POST'])
def save_wishlist(product_id):
    customer=current_customer()
    if not customer: return redirect(url_for('login'))
    item=WishlistItem.query.filter_by(user_id=customer.id,product_id=product_id).first()
    if request.form.get('action')=='remove':
        if item: db.session.delete(item)
    else:
        Product.query.filter_by(id=product_id,active=True).first_or_404()
        if not item: db.session.add(WishlistItem(user_id=customer.id,product_id=product_id))
    try: db.session.commit()
    except IntegrityError: db.session.rollback()
    return redirect(url_for('customer_wishlist'))

@app.route('/account/orders/<int:order_id>/reorder',methods=['POST'])
def customer_reorder(order_id):
    order=accessible_order(order_id);cart_data=session.get('cart',{}).copy();unavailable=[]
    for item in order.items:
        product=db.session.get(Product,item.product_id) if item.product_id else None
        if not product or not product.active or product.stock<=0:
            unavailable.append(item.product_name);continue
        cart_data[str(product.id)]=min(product.stock,int(cart_data.get(str(product.id),0))+item.quantity)
    session['cart']=cart_data
    flash('Available items added at current prices.'+(' Some items are unavailable.' if unavailable else ''),'success')
    return redirect(url_for('cart'))

@app.route('/account/orders/<int:order_id>/receipt')
def customer_receipt(order_id):
    order=accessible_order(order_id)
    return render_template('customer_receipt.html',order=order,discount=db.session.get(OrderDiscount,order.id))

@app.route('/account/support',methods=['GET','POST'])
def customer_support():
    customer=current_customer()
    if not customer: return redirect(url_for('login'))
    if request.method=='POST':
        order=Order.query.filter_by(id=request.form.get('order_id',type=int),user_id=customer.id).first_or_404()
        kind=request.form.get('kind','');message=request.form.get('message','').strip()
        if kind not in ('Question','Return','Dispute') or not 10<=len(message)<=3000:
            flash('Choose a request type and describe the issue in 10 to 3,000 characters.','danger')
        else:
            db.session.add(SupportRequest(user_id=customer.id,order_id=order.id,kind=kind,message=message));db.session.commit()
            flash('Your request has been sent to the store.','success');return redirect(url_for('customer_support'))
    return render_template('customer_support.html',orders=Order.query.filter_by(user_id=customer.id).all(),tickets=SupportRequest.query.filter_by(user_id=customer.id).order_by(SupportRequest.created_at.desc()).all())

@app.route('/admin/support',methods=['GET','POST'])
@admin_required
def admin_support():
    if request.method=='POST':
        ticket=db.get_or_404(SupportRequest,request.form.get('ticket_id',type=int))
        status=request.form.get('status')
        if status in ('Open','In review','Resolved'):
            ticket.status=status;commit_admin_change('Support request updated.')
        return redirect(url_for('admin_support'))
    return render_template('admin_support.html',tickets=SupportRequest.query.order_by(SupportRequest.created_at.desc()).all())

@app.context_processor
def customer_saved_data():
    customer=current_customer()
    return {'saved_addresses':SavedAddress.query.filter_by(user_id=customer.id).all() if customer and request.endpoint=='checkout' else []}


@app.route('/api/cart/coupon',methods=['POST'])
def preview_coupon():
    code=(request.get_json(silent=True) or {}).get('code','').strip().upper()
    subtotal=0
    for product_id,quantity in session.get('cart',{}).items():
        product=db.session.get(Product,int(product_id))
        if product and product.active: subtotal+=product.sale_price*int(quantity)
    coupon=Coupon.query.filter(db.func.upper(Coupon.code)==code,Coupon.active.is_(True)).first()
    now=datetime.utcnow()
    if not coupon or (coupon.start_date and coupon.start_date>now) or (coupon.end_date and coupon.end_date<now) or subtotal<(coupon.minimum_order or 0) or not 0<=coupon.discount_percent<=100:
        return jsonify(error='This coupon is unavailable or the minimum order has not been met.'),400
    return jsonify(subtotal=subtotal,discount=subtotal*coupon.discount_percent//100)


def identity_in_use(value,exclude_id=None):
    email,phone=account_identity(value)
    query=User.query.filter(User.id!=exclude_id) if exclude_id else User.query
    if email: return query.filter(db.func.lower(User.email)==email).first() is not None
    for user in query.filter(User.phone.isnot(None)):
        try:
            if normalize_phone(user.phone)==phone: return True
        except ValueError: pass
    return False


from flask.sessions import SecureCookieSessionInterface

class DashboardSessionInterface(SecureCookieSessionInterface):
    """Independent signed sessions and CSRF tokens for the two website areas."""
    def is_admin(self):
        return request.path == '/admin' or request.path.startswith('/admin/')
    def get_cookie_name(self, app):
        return 'lift_admin_session' if self.is_admin() else app.config['SESSION_COOKIE_NAME']
    def get_cookie_path(self, app):
        return '/admin' if self.is_admin() else '/'
    def get_signing_serializer(self, app):
        serializer=super().get_signing_serializer(app)
        if serializer and self.is_admin(): serializer.salt='lift-admin-session'
        return serializer

app.session_interface=DashboardSessionInterface()

@app.before_request
def remove_legacy_admin_session():
    if not (request.path == '/admin' or request.path.startswith('/admin/')):
        for key in ('admin_logged_in','admin_id','admin_email'): session.pop(key,None)

@app.route('/account')
def customer_dashboard():
    customer=current_customer()
    if not customer: return redirect(url_for('login'))
    return render_template('customer_dashboard.html',customer=customer,
        order_count=Order.query.filter_by(user_id=customer.id).count(),
        wishlist_count=WishlistItem.query.filter_by(user_id=customer.id).count())

from types import SimpleNamespace
from account_security import install as install_account_security
stamp_customer_session, account_security_models = install_account_security(SimpleNamespace(**globals()))

from admin_security import install as install_admin_security
admin_security_models = install_admin_security(SimpleNamespace(**globals()))

from live_chat import install as install_live_chat
chat_models = install_live_chat(SimpleNamespace(**globals()))

if __name__ == "__main__":

    app.run(debug=True)


