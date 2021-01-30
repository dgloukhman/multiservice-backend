from pydantic import BaseModel, EmailStr
from datetime import date,time
from enum import Enum
from typing import List, Optional




class Company(BaseModel):
    name: str
    industry: str

class CompanyResponse(Company):
    class Config:
        orm_mode = True


class User(BaseModel):
    first_name: str
    last_name: str
    birthdate: date
    birthdate: date
    email_adress: EmailStr
    company_function: str

class UserRegister(User):
    employer: Company


    

class UserResponse(User):
    id: int
    registration_date: date


    class Config:
        orm_mode = True


