from fastapi import APIRouter, Depends,HTTPException,status,Form
from typing import List
from internal.database import engine, get_db
from internal import models, schemas
from sqlalchemy.orm import Session
from . import crud
from fastapi.responses import JSONResponse
from internal.login import get_current_admin_user,get_current_customer_user



router = APIRouter(
     prefix="/imbuto",
    tags=["imbuto"],
)

@router.post('/create-product/',response_model=schemas.ShowProduct ,status_code=status.HTTP_201_CREATED)
async def create_product(request : schemas.Product , db: Session =Depends(get_db)
                         ,current_admin_user: schemas.User = Depends(get_current_admin_user)
                         ):
    new_cat= models.Product(
        name =request.name,
        description =request.description,
        user_id =current_admin_user.id,
        quantity= request.quantity,
        price = request.price
    )
    db.add(new_cat)
    db.commit()
    db.refresh(new_cat)
    return new_cat

@router.get('/show-all/', response_model=List[schemas.ShowProduct],status_code=status.HTTP_200_OK)
async def all_product(db: Session = Depends(get_db)
                      ):
    all_p =db.query(models.Product).all()
    return all_p

@router.post('/cart/{product_id}/')
async def add_to_cat(product_id : int ,request: schemas.Cart ,db: Session = Depends(get_db),
                     current_customer_user: schemas.User = Depends(get_current_customer_user)
                     ):
    product =crud.get_product(product_id,db)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND
                            , detail=" Product  Doesn't exist"
                            )
        
    new_cat = models.Cart(
        user_id = current_customer_user.id,
        product_id =product.id,
        quantity = request.quantity
        
    )
    # product_obj = db.query(models.Product).filter(models.Product.id == product_id)
    prod_quantity = product.quantity
    if prod_quantity < int(request.quantity):
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE
                            ,detail= "We don't have all this product in stock" 
                            )
    new_quantity = int(prod_quantity) - int(request.quantity)
    product.quantity = new_quantity
    db.add(new_cat)
    db.commit()
    return 'Product Added Successfully'

@router.get('/cart-details/', response_model=List[schemas.ShowCart])
async def cart(db : Session = Depends(get_db),current_customer_user: schemas.User = Depends(get_current_customer_user)):
    cart = db.query(models.Cart).filter(models.Cart.user_id == current_customer_user.id)
    return cart

@router.post('/order/{cart_id}/')
async def make_order(cart_id : int , db : Session = Depends(get_db),current_customer_user: schemas.User = Depends(get_current_customer_user)):
    cart = crud.get_cart(cart_id , db)
    if not cart:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND
                            , detail=" Cart doesn't exists!"
                            )
    new_order = models.Order(
        
        quantity =cart.quantity,
        user_id =cart.user_id,
        product_id =cart.product_id
    )
    cart_to = db.query(models.Cart).filter(models.Cart.id == cart_id)
    db.add(new_order)
    cart_to.delete(synchronize_session=False)
    db.commit()
    db.refresh(new_order)
    return 'order sent successfully !'

@router.get('/product')
async def user_product(db: Session = Depends(get_db)
           ,current_admin_user: schemas.User = Depends(get_current_admin_user)
           ):
    
    products = db.query(models.Product).filter(models.Product.user_id == current_admin_user.id)
    
    for product in products:
        items = {
            'name' : product.name,
            'description' :product.description,
            'quantity' : product.quantity,
            'price' : product.price,
            'creator' : f' {product.user.username} with {product.user.email}'
        }

    return JSONResponse(items)


    
    
