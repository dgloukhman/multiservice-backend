from sqlalchemy import Column, ForeignKey, Integer, String, Date,  Numeric
from sqlalchemy.orm import relationship
from datetime import date

from sqlalchemy.sql.sqltypes import Boolean, NUMERIC


from database import Base

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


    






