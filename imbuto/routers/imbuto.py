from fastapi import APIRouter, Depends,HTTPException,status,Form,Request
from typing import List
from internal.database import get_db
from internal import models, schemas
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from internal.login import get_current_admin_user
from fastapi_session import Session
from fastapi.encoders import jsonable_encoder
from sqlalchemy import and_ , or_



router = APIRouter(
     prefix="/imbuto",
    tags=["imbuto"],
)

@router.post('/create-product/' ,status_code=status.HTTP_201_CREATED)
async def create_product(request : schemas.Product , db: Session =Depends(get_db)
                         ,current_admin_user: schemas.User = Depends(get_current_admin_user)
                         ):
    new_product= models.Product(
        name =request.name,
        description =request.description,
        user_id =current_admin_user.id,
        price = request.price
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product


@router.get('/show-all/',status_code=status.HTTP_200_OK)
async def all_product(db: Session = Depends(get_db)):
    all_p =db.query(models.Product).all()
    data =[]
    for item in all_p:
        items ={
            "name" : item.name,
            "description" : item.description,
            "price" : item.price
        }
        data.append(items)
    return data



@router.get('/product')
async def user_product(db: Session = Depends(get_db)
           ,current_admin_user: schemas.User = Depends(get_current_admin_user),
           ):
    
    products = db.query(models.Product).filter(models.Product.user_id == current_admin_user.id)
    data = []
    for product in products:
        items = {
            'name' : product.name,
            'description' :product.description,
            'now in stock' : product.in_stock,
            'price' : product.price,
            'creator' : f' {product.user.username} with {product.user.email}'
        }
        data.append(items)

    return JSONResponse(data)



@router.put("/{item_id}", status_code=200)
async def update_item(item_id: int, item: schemas.UpdateProduct , db : Session =Depends(get_db),
                      current_admin_user: schemas.User = Depends(get_current_admin_user)):
    
    filter_conditions = and_(models.Product.id == item_id, models.Product.user_id == current_admin_user.id)
    items= db.query(models.Product).filter(filter_conditions).first()
    if items is None:
        raise HTTPException(status_code=404 , detail=" Product Doesn't exists")
        
    update_item_encoded = jsonable_encoder(item)
    items.price =item.price
    items.in_stock = item.in_stock
    db.commit()
    db.refresh(items)
    data =[]
    item_json= {
        "name": items.name,
        "description" : items.description,
        "Updated Price" : items.price,
        "Updated At" : items.updated_at
    }
    return item_json



@router.delete("/{item_id}", status_code=200)
async def delete_item(item_id: int, db : Session =Depends(get_db),
                      current_admin_user: schemas.User = Depends(get_current_admin_user)):
    
    filter_conditions = and_(models.Product.id == item_id, models.Product.user_id == current_admin_user.id)
    items= db.query(models.Product).filter(filter_conditions).first()
    if items is None:
        raise HTTPException(status_code=404 , detail=" Product Doesn't exists")
        
    # update_item_encoded = jsonable_encoder(item)
    db.delete(items)
    db.commit()
    return "Product Deleted Successfully !"


    
    
