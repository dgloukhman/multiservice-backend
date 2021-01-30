from fastapi import FastAPI, status, Depends, Response, HTTPException
from sqlalchemy.sql.functions import mode
from database import SessionLocal, engine, get_db
import models
import schema
from sqlalchemy.orm import Session
from typing import Dict, List
from typing import Optional
import threading


app = FastAPI(docs_url='/user/docs', openapi_url="/user/openapi.json")

# with threading.Lock():
#     models.Base.metadata.create_all(bind=engine)



#### helper functions ####
def get_user_by_id(user_id: int, db: Session) -> Optional[models.User]:
    return db.query(models.User).get(user_id)

def get_user_by_email(email_adress: str, db: Session) -> Optional[models.User]:
    email_adress = email_adress.strip().lower()
    return db.query(models.User).filter(models.User.email_adress == email_adress).first()

def get_company_by_name(company: schema.Company, db: Session) -> Optional[models.Company]:
    name = company.name.strip().lower()
    return db.query(models.Company).filter(models.Company.name == name).first()

def update_resource_in_memory(orm_obj: models.Base, **kwargs):
    for key, value in kwargs.items():
        if hasattr(orm_obj, key):
            setattr(orm_obj, key, value)



##############################################
################# Routes #####################
##############################################

@app.get('/user', tags=["User"])
def get_all_users(db: Session = Depends(get_db)):
    """
    List all users
    """
    return db.query(models.User).all()


@app.post('/user', tags=["User"], status_code=status.HTTP_201_CREATED)
def create_user(user: schema.UserRegister, db: Session = Depends(get_db)):
    """
    Create a user
    """
    if get_user_by_email(user.email_adress, db):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, \
            detail='A user with this e-mail is already registered.')
    
    db_user = models.User(**user.dict( exclude={'employer'}))
    db_user.email_adress = db_user.email_adress.strip().lower()

    if not (company_db := get_company_by_name(user.employer, db)):
        company_db = models.Company(**user.employer.dict())
    db_user.employer = company_db
    db.add(db_user)
    db.commit()
    return {'detail':'User succesfully created!'}


@app.get('/user/{user_id}', response_model=schema.UserResponse, tags=["User"])
def get_user(user_id: int, db: Session = Depends(get_db)):
    """
    Get user with {user_id}
    """
    user = get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return schema.UserResponse(**user.__dict__)


@app.put('/user/{user_id}', status_code=status.HTTP_204_NO_CONTENT, tags=["User"])
def update_user(user_id: int, user: schema.User, db: Session = Depends(get_db)):
    """
    Update user with {user_id}
    """
    if not (user_db := get_user_by_id(user_id,db)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    if user_db.email_adress != user.email_adress:
        if get_user_by_email(user.email_adress, db):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, \
                detail='A user with this e-mail is already registered.')
    update_resource_in_memory(user_db, **user.dict())
    db.add(user_db)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.delete('/user/{user_id}', status_code=status.HTTP_204_NO_CONTENT, tags=["User"])
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """
    Delete user with {user_id}
    """
    db.query(models.User).filter(models.User.id == user_id).delete()
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

################################################
################## Company #####################
################################################

@app.get('/company', response_model=List[schema.CompanyResponse], tags=["Company"])
def get_all_companies(db: Session=Depends(get_db)):
    return db.query(models.Company).all()

@app.post('/company', response_model=List[schema.CompanyResponse], status_code=status.HTTP_201_CREATED, tags=["Company"])
def create_company(company: schema.Company, db: Session = Depends(get_db)):
    """
    Create a user
    """
    if get_company_by_name(company, db):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, \
            detail='A Company with this name already exists.')  
    
    company_db = models.Company(**company.dict())
    db.add(company_db)
    db.commit()
    return {'detail':'Company succesfully created!'}

@app.get('/company/{company_id}',response_model=schema.CompanyResponse, tags=["Company"])
def get_company(company_id: int, company: schema.Company, db: Session = Depends(get_db)):
    if not (company_db := db.query(models.Company).get(company_id)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return company_db

@app.put('/company/{company_id}', status_code=status.HTTP_204_NO_CONTENT, tags=["Company"])
def update_company(company_id: int, company: schema.Company, db: Session = Depends(get_db)):
    """
    Update user with {user_id}
    """
    if not (company_db := db.query(models.Company).get(company_id)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    if company.name != company_db.name:
        if get_company_by_name(company, db):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, \
                detail='A company with this name exists already')
    update_resource_in_memory(company_db, **company.dict())
    db.add(company_db)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.delete('/company/{company_id}', status_code=status.HTTP_204_NO_CONTENT, tags=["Company"])
def delete_company(company_id: int, db: Session = Depends(get_db)):
    """
    Delete user with {user_id}
    """
    db.query(models.User).filter(models.Company.id == company_id).delete()
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


if __name__ == '__main__':
    import uvicorn
    uvicorn.run("user:app", host="127.0.0.1", port=8000,
                log_level="info", reload=True)
