import bcrypt
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, BigInteger, Boolean
from sqlalchemy.sql import func
from models import Base

class User(Base):
    __tablename__ = 'users'

    # Kolom-kolom untuk tabel user
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    company_profile_id = Column(Integer, default=1)
    department_id = Column(Integer, nullable=True)
    employee_id = Column(Integer, nullable=True)
    employee_section_id = Column(Integer, nullable=True)
    username = Column(String(255), unique=True, nullable=True)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    face_vector = Column(Text, nullable=True, comment='2024-07-30 kebutuhan untuk face-api.js')
    webauthn_id = Column(Text, nullable=True, comment='2024-07-30 kebutuhan gem webauthn')
    email = Column(String(255), unique=True, nullable=False)
    status = Column(Enum('active', 'suspend'), default='active', nullable=False)
    encrypted_password = Column(String(255), nullable=False)
    reset_password_token = Column(String(255), nullable=True)
    reset_password_sent_at = Column(DateTime, nullable=True)
    remember_created_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    failed_attempts = Column(Integer, nullable=True)
    unlock_token = Column(String(255), nullable=True)
    locked_at = Column(DateTime, nullable=True)
    confirmation_token = Column(String(255), nullable=True)
    confirmed_at = Column(DateTime, nullable=True)
    confirmation_sent_at = Column(DateTime, nullable=True)
    avatar = Column(String(255), nullable=True)
    signature = Column(String(255), nullable=True)
    last_sign_in_ip = Column(String(255), nullable=True)
    online = Column(Boolean, default=False)
    lockable = Column(Boolean, nullable=True)
    
    # Fungsi untuk meng-hash password
    def set_password(self, password):
        self.encrypted_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    # Fungsi untuk memverifikasi password
    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.encrypted_password.encode('utf-8'))

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, password={self.encrypted_password})>"
