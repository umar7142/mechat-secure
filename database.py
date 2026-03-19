from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import random
import string
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "mechat.db")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{db_path}"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 🚀 NAYA VIP USER TABLE (With Bio, DP & Region)
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String)
    dob = Column(String)
    gender = Column(String, default="Male")
    secret_key = Column(String, unique=True, index=True)
    phone_number = Column(String, unique=True, index=True)
    region = Column(String)
    profile_pic = Column(String, default="")  
    # 👇 NAYA FEATURE: User Bio (Status)
    bio = Column(String, default="Hey there! I am using ME CHAT Secure Network.")

# THE CHAT VAULT
class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(String, index=True)
    receiver_id = Column(String, index=True)
    text = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

# 👇 NAYA FEATURE: Block List Table
class Block(Base):
    __tablename__ = "blocks"

    id = Column(Integer, primary_key=True, index=True)
    blocker_id = Column(String, index=True) # Jisne block kiya
    blocked_id = Column(String, index=True) # Jo block hua

# 🌍 THE VIP TELECOM ENGINE (Mega 40+ Countries Pack)
COUNTRY_FORMATS = {
    # 📌 SOUTH ASIA
    "PK": {"code": "+92", "region": "South Asia", "format": "399 XXXXXXX"},
    "IN": {"code": "+91", "region": "South Asia", "format": "999 XXX XXXX"},
    "BD": {"code": "+880", "region": "South Asia", "format": "1X XXX-XXXXXX"},
    "LK": {"code": "+94", "region": "South Asia", "format": "7X XXX XXXX"},
    
    # 📌 NORTH AMERICA
    "US": {"code": "+1", "region": "North America", "format": "(555) XXX-XXXX"},
    "CA": {"code": "+1", "region": "North America", "format": "(555) 01X-XXXX"},
    "MX": {"code": "+52", "region": "North America", "format": "55 XXXX XXXX"},
    
    # 📌 EUROPE
    "GB": {"code": "+44", "region": "Europe", "format": "7700 90XXXX"},
    "DE": {"code": "+49", "region": "Europe", "format": "15X XXXX XXXX"},
    "FR": {"code": "+33", "region": "Europe", "format": "6 XX XX XX XX"},
    "IT": {"code": "+39", "region": "Europe", "format": "3XX XXX XXXX"},
    "ES": {"code": "+34", "region": "Europe", "format": "6XX XXX XXX"},
    "NL": {"code": "+31", "region": "Europe", "format": "6 XXXX XXXX"},
    "CH": {"code": "+41", "region": "Europe", "format": "7X XXX XX XX"},
    "SE": {"code": "+46", "region": "Europe", "format": "7X XXX XX XX"},
    "RU": {"code": "+7", "region": "Eastern Europe", "format": "9XX XXX-XX-XX"},
    "UA": {"code": "+380", "region": "Eastern Europe", "format": "9X XXX XX XX"},
    
    # 📌 MIDDLE EAST
    "AE": {"code": "+971", "region": "Middle East", "format": "59 XXXXXXX"},
    "SA": {"code": "+966", "region": "Middle East", "format": "50 XXX XXXX"},
    "QA": {"code": "+974", "region": "Middle East", "format": "33XX XXXX"},
    "OM": {"code": "+968", "region": "Middle East", "format": "9XXX XXXX"},
    "TR": {"code": "+90", "region": "Middle East", "format": "53X XXX XXXX"},
    "EG": {"code": "+20", "region": "Middle East", "format": "1X XXXX XXXX"},
    
    # 📌 EAST ASIA & OCEANIA
    "CN": {"code": "+86", "region": "East Asia", "format": "13X XXXX XXXX"},
    "JP": {"code": "+81", "region": "East Asia", "format": "90-XXXX-XXXX"},
    "KR": {"code": "+82", "region": "East Asia", "format": "10-XXXX-XXXX"},
    "AU": {"code": "+61", "region": "Oceania", "format": "4XX XXX XXX"},
    "NZ": {"code": "+64", "region": "Oceania", "format": "2X XXX XXXX"},
    
    # 📌 SOUTHEAST ASIA
    "ID": {"code": "+62", "region": "Southeast Asia", "format": "8XX-XXXX-XXXX"},
    "MY": {"code": "+60", "region": "Southeast Asia", "format": "1X-XXX XXXX"},
    "SG": {"code": "+65", "region": "Southeast Asia", "format": "8XXX XXXX"},
    "TH": {"code": "+66", "region": "Southeast Asia", "format": "8X XXX XXXX"},
    "PH": {"code": "+63", "region": "Southeast Asia", "format": "9XX XXX XXXX"},
    
    # 📌 SOUTH AMERICA & AFRICA
    "BR": {"code": "+55", "region": "South America", "format": "11 9XXXX-XXXX"},
    "AR": {"code": "+54", "region": "South America", "format": "9 11 XXXX-XXXX"},
    "CO": {"code": "+57", "region": "South America", "format": "3XX XXX XXXX"},
    "ZA": {"code": "+27", "region": "Africa", "format": "8X XXX XXXX"},
    "NG": {"code": "+234", "region": "Africa", "format": "80X XXX XXXX"},
    "KE": {"code": "+254", "region": "Africa", "format": "7XX XXX XXX"},
    "MA": {"code": "+212", "region": "Africa", "format": "6XX-XXXXXX"}
}

def generate_secret_key():
    digits = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"KEY-{digits}"

def generate_virtual_number(country_code="US"):
    data = COUNTRY_FORMATS.get(country_code, COUNTRY_FORMATS["US"])
    fmt = data["format"]
    
    final_num = ""
    for char in fmt:
        if char == 'X':
            final_num += str(random.randint(0, 9))
        else:
            final_num += char
            
    full_number = f"{data['code']} {final_num}"
    return full_number, data["region"]

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    print("✅ VIP DATABASE READY! (Virtual Burner Phones, DP, Bio & Block Enabled!)")
