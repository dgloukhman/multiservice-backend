from pydantic import BaseModel, EmailStr
from datetime import date,time
from enum import Enum
from typing import List, Optional




class Supplier(BaseModel):
    name: str
    industry: str
    country: str
    contact_name: str
    phone_number: str
    adress: str


class SupplierResponse(Supplier):
    id: int
    
    class Config:
        orm_mode = True


class ProductListing(BaseModel):
    name: str
    description: str
    price: float
    delivery_time: int
    available: bool
    supplier_name: str 

class ProductListingResponse(ProductListing):
    supplier_id: int
    good_id: int

