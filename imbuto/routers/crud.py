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
    return password_context.hash(password)

def verify_password(plain_password, hashed_password):
    return password_context.verify(plain_password, hashed_password)

def get_product(product_id : int, db : Session ):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    return product

def get_cart(id : int, db : Session ):
    cart = db.query(models.Cart).filter(models.Cart.id == id).first()
    return cart
    
    
def get_user(db : Session , username : str):
    user = db.query(models.User).filter(models.User.username == username).first()
    return user