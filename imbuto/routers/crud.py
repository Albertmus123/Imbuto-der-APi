from sqlalchemy.orm import Session
from internal import schemas,models
from passlib.context import CryptContext


password_context=CryptContext(schemes=['bcrypt'], deprecated="auto")

def get_user_email(email : str,db : Session):
    user_obj = db.query(models.User).filter(models.User.email == email).first()
    return user_obj

def get_user_username(username : str,db : Session):
    user_obj = db.query(models.User).filter(models.User.username == username).first()
    return user_obj

def hashing_password(password : str):
    hashed_password=password_context.hash(password)
    return hashed_password
    