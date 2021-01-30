from fastapi import FastAPI, status, Depends, Response, HTTPException
from sqlalchemy.sql.functions import mode
from database import SessionLocal, engine, get_db
import models
import schema
from sqlalchemy.orm import Session, joinedload
from typing import Dict, List
from typing import Optional


app = FastAPI(docs_url='/supplier/docs', openapi_url="/supplier/openapi.json")




#### helper functions ####
def get_supplier_by_id(supplier_id: int, db: Session) -> Optional[models.Supplier]:
    return db.query(models.Supplier).get(supplier_id)


def get_supplier_by_name(supplier_name: str, db: Session) -> Optional[models.Supplier]:
    name = supplier_name.strip().lower()
    return db.query(models.Supplier).filter(models.Supplier.name == name).first()

def get_good_by_name(good_name: str, db: Session):
    name = good_name.strip().lower()
    return db.query(models.Good).filter(models.Good.name == name).first()



def update_resource_in_memory(orm_obj: models.Base, **kwargs):
    for key, value in kwargs.items():
        if hasattr(orm_obj, key):
            setattr(orm_obj, key, value)

def serialize_product_listing(good: models.Good,\
    listing: models.Listing,\
    supplier: models.Supplier) -> schema.ProductListingResponse:
    
    combined = {**good.__dict__, **listing.__dict__, **supplier.__dict__}
    combined['name'] = good.name
    combined['supplier_name'] = supplier.name
    combined['supplier_id'] = supplier.id
    combined['good_id'] = good.id
    return schema.ProductListingResponse(**combined)

##############################################
################# Routes #####################
##############################################

@app.get('/supplier', tags=["Supplier"])
def get_all_suppliers(db: Session = Depends(get_db)):
    """
    List all suppliers
    """
    return db.query(models.Supplier).all()


@app.post('/supplier', tags=["Supplier"], status_code=status.HTTP_201_CREATED)
def create_suppliers(supplier: schema.Supplier, db: Session = Depends(get_db)):
    """
    Create a suppliers
    """
    if get_supplier_by_name(supplier.name, db):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail='A supplier with this name exists already.')

    db_supplier = models.Supplier(**supplier.dict())

    db.add(db_supplier)
    db.commit()
    return {'detail': 'Supplier succesfully created!'}


@app.get('/supplier/{supplier_id}', response_model=schema.SupplierResponse, tags=["Supplier"])
def get_supplier(supplier_id: int, db: Session = Depends(get_db)):
    """
    Get supplier with {supplier_id}
    """
    if not (supplier := get_supplier_by_id(supplier_id, db)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return schema.SupplierResponse(**supplier.__dict__)


@app.put('/supplier/{supplier_id}', status_code=status.HTTP_204_NO_CONTENT, tags=["Supplier"])
def update_supplier(supplier_id: int, supplier: schema.Supplier, db: Session = Depends(get_db)):
    """
    Update supplier with {supplier_id}
    """
    if not (supplier_db := get_supplier_by_id(supplier_id, db)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    if supplier_db.name != supplier.name:
        if get_supplier_by_name(supplier.name, db):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail='A supplier with this name exist already.')
    update_resource_in_memory(supplier_db, **supplier.dict())
    db.add(supplier_db)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.delete('/supplier/{supplier_id}', status_code=status.HTTP_204_NO_CONTENT, tags=["Supplier"])
def delete_supplier(supplier_id: int, db: Session = Depends(get_db)):
    """
    Delete supplier with {supplier_id}
    """
    db.query(models.Supplier).filter(
        models.Supplier.id == supplier_id).delete()
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

################################################
################## Listings ####################
################################################

@app.get('/listings', status_code=status.HTTP_201_CREATED, response_model=List[schema.ProductListingResponse],tags=['Products'])
def get_all_listings(db: Session = Depends(get_db)):
    """
    Get a list of all listings
    """
    listings_queryset = db.query(models.Good, models.Listing, models.Supplier).select_from(models.Good)\
        .join(models.Listing)\
        .join(models.Supplier).all()
   
    return (serialize_product_listing(g, l, s) for g, l, s in listings_queryset)

    

@app.post('/listing', status_code=status.HTTP_201_CREATED, tags=['Products'])
def create_listing(listing: schema.ProductListing, db: Session = Depends(get_db)):
    """
    Create a listing
    """
    if not (supplier_db := get_supplier_by_name(listing.supplier_name,db)):
            supplier_db = models.Supplier(name = listing.supplier_name)
    
    if not (good_db := get_good_by_name(listing.name,db)):
            props = (m.key for m in models.Good.__table__.columns)
            good_db = models.Good(**listing.dict(include=set(props)))
    
    print(models.Listing.__table__)
    props = (m.key for m in models.Listing.__table__.columns)
    listing_db = models.Listing(**listing.dict(include=set(props)))
    listing_db.supplier = supplier_db
    good_db.suppliers.append(listing_db)

    if db.query(models.Listing).get({'supplier_id': supplier_db.id, 'good_id': good_db.id}):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,\
            detail='A listing for this item from that supplier already exists')

    db.add(good_db)
    db.commit()
    return {'detail':'Listing successfully created'}

@app.delete('/listing', status_code=status.HTTP_204_NO_CONTENT, tags=["Products"])
def delete_listing(supplier_id: int, good_id: int, db: Session = Depends(get_db)):
    """
    Delete Listing with {supplier_id} and {good_id} as primary key
    """
    db.query(models.Listing).filter(
        models.Listing.supplier_id == supplier_id and\
        models.Listing.good_id == good_id
    ).delete()
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
    

if __name__ == '__main__':
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000,
                log_level="info", reload=True)
