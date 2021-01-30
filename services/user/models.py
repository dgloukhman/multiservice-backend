from sqlalchemy import Column, ForeignKey, Integer, String, Date, DateTime
from sqlalchemy.orm import relationship
import datetime


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

    






