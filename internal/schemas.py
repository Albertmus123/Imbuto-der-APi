from pydantic import BaseModel
from typing import Dict

class User(BaseModel):
    username : str
    email : str
    password : str
    
class ShowUser(BaseModel):
    username : str
    email : str
    
    class Config:
        orm_mode =True
        
        
class Login(BaseModel):
    username : str
    password : str
    
class Product(BaseModel):
    name : str
    description: str
    price : int
    
    
    class Config:
        orm_mode = True
        
class UpdateProduct(BaseModel):
    price : int
    in_stock: bool
    
class CartItem(BaseModel):
    item_name: str
    quantity : int

class SessionData(BaseModel):
    username: str
    cart_items : Dict[int , CartItem] = {}

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str 
    



    
    

    