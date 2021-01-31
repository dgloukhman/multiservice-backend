from sqlalchemy import Column, ForeignKey, Integer, String, Date, DateTime, Boolean, Numeric
from sqlalchemy.orm import relationship
import datetime
from datetime import date


from database import Base

class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    industry = Column(String)
    employees = relationship("User", back_populates="employer")
    

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    birthdate = Column(Date)
    email_adress = Column(String)
    company_function = Column(String)
    employer_id = Column(Integer, ForeignKey(Company.id))
    registration_date = Column(DateTime, default=datetime.datetime.utcnow)
    employer = relationship("Company", back_populates="employees")

class Listing(Base):
    __tablename__ = "supplier_goods"

    supplier_id = Column(Integer, ForeignKey('suppliers.id'), primary_key=True)
    good_id = Column(Integer, ForeignKey('goods.id'), primary_key=True)
    price = Column( Numeric(precision=2))
    delivery_time = Column(Integer)
    available = Column(Boolean)
    inserted_on = Column(Date, default=date.today())

    supplier = relationship("Supplier", back_populates="goods")
    good = relationship("Good", back_populates="suppliers")

    

class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    industry = Column(String)
    country = Column(String)
    contact_name = Column(String)
    phone_number = Column(String)
    adress = Column(String)

    goods = relationship('Listing', back_populates='supplier', cascade="all, delete")
    

class Good(Base):
    __tablename__ = "goods"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(String)
    
    suppliers = relationship('Listing', back_populates='good', cascade="all, delete")

    






