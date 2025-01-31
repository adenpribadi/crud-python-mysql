from dotenv import load_dotenv
import os
import urllib.parse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Fungsi untuk memuat ulang file .env dan memperbarui DB_CONFIG
def reload_and_update_config():
    load_dotenv(override=True)  # Memuat ulang file .env
    print("reload_and_update_config")
    return {
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "host": os.getenv("DB_HOST"),
        "port": os.getenv("DB_PORT"),
        "db_name": os.getenv("DB_NAME")
    }

# Inisialisasi awal koneksi database
DB_CONFIG = reload_and_update_config()

# Pastikan semua konfigurasi ada sebelum melanjutkan
for key, value in DB_CONFIG.items():
    if not value:
        raise ValueError(f"{key} is missing in DB_CONFIG")

# Pastikan password ada sebelum melakukan encoding
if DB_CONFIG["password"]:
    # Encode password untuk memastikan karakter @ dan lainnya ditangani dengan benar
    DB_CONFIG["password"] = urllib.parse.quote_plus(DB_CONFIG["password"])
else:
    raise ValueError("Password is not set in DB_CONFIG")

# Bangun URI koneksi
DATABASE_URI = "mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}".format(**DB_CONFIG)

# Buat engine SQLAlchemy
engine = create_engine(DATABASE_URI, echo=True)

# Buat session factory
Session = sessionmaker(bind=engine)

# Buat base untuk model
Base = declarative_base()

# Helper function untuk mendapatkan sesi
def get_session():
    try:
        # Memperbarui konfigurasi hanya jika perlu
        DB_CONFIG = reload_and_update_config()

        # Pastikan password di-encode ulang setiap kali sesi diambil
        if DB_CONFIG["password"]:
            DB_CONFIG["password"] = urllib.parse.quote_plus(DB_CONFIG["password"])

        # Bangun ulang URI koneksi dengan parameter terbaru
        DATABASE_URI = "mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}".format(**DB_CONFIG)

        # Periksa apakah engine perlu diperbarui
        global engine
        if not engine.url == DATABASE_URI:
            print("Updating engine due to DB_CONFIG change")
            engine = create_engine(DATABASE_URI, echo=True)
            Session.configure(bind=engine)

        # Cobalah untuk membuat sesi baru dan kembalikan
        return Session()

    except Exception as e:
        # Tangani kesalahan saat membuat sesi
        print(f"Error while creating session: {str(e)}")
        raise

# Impor model dengan urutan yang benar
from .unit_model import Unit
from .material_model import Material
from .general_model import General
from .employee_model import Employee
from .department_model import Department
from .employee_section_model import EmployeeSection
from .position_model import Position  # Pastikan model Position diimpor setelah definisi model lainnya
from .purchases.request_model import PurchaseRequest
from .purchases.request_item_model import PurchaseRequestItem
from .purchases.order_model import PurchaseOrder
from .purchases.order_item_model import PurchaseOrderItem

# Ditambahkan pada 2024-12-31 untuk model Product
from .product_model import Product

# Ditambahkan pada 2025-01-31 untuk model contact
from .contact_model import Contact

# Ditambahkan pada 2025-01-31 untuk model Currency
from .currency_model import Currency

# Ditambahkan pada 2025-01-31 untuk model Tax
from .tax_model import Tax

# Ditambahkan pada 2025-01-31 untuk model TermOfPayment
from .term_of_payment_model import TermOfPayment
