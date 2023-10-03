from fastapi import APIRouter, Depends,HTTPException,status ,Form
from internal.database import engine, get_db
from internal import models, schemas
from sqlalchemy.orm import Session
from . import crud

models.Base.metadata.create_all(bind=engine)


router = APIRouter(
    prefix="/users",
    tags=["users"],
)

@router.post('/create-account/',response_model=schemas.ShowUser ,status_code=status.HTTP_201_CREATED)
async def create(request : schemas.User , db: Session = Depends(get_db)):
    user_email =crud.get_user_email(request.email,db)
    user_username =crud.get_user_username(request.username , db)
    hash_pass = crud.hashing_password(request.password)
    if user_email:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND 
                            ,detail= f"The email {request.email} already exists! "
                            )
        
    if user_username:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND 
                            ,detail= f"The username {request.username} already exists! "
                            )
        
    new_user=models.User(
        username = request.username,
        email = request.email,
        password = hash_pass
        
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user