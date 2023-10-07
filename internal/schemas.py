from pydantic import BaseModel

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
    
#     class Config:
#         orm_mode = True
        
# class Cart(BaseModel):
#     quantity : int
    
# class ShowCart(BaseModel):
#     product : ShowProductCart
#     quantity : int
#     user : ShowUser
    
#     class Config:
#         orm_mode = True
        
# class Order(BaseModel):
#     quantity : int
#     Products : ShowProductCart
#     users : ShowUser

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str 
    



    
    

    