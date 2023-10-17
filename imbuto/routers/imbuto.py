from fastapi import APIRouter, Depends,HTTPException,status,Form, Response
from typing import List
from internal.database import get_db
from internal import models, schemas
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from internal.login import get_current_admin_user,get_current_user
from fastapi.encoders import jsonable_encoder
from sqlalchemy import and_ , or_
from uuid import UUID, uuid4
from fastapi_sessions.backends.implementations import InMemoryBackend
from fastapi_sessions.session_verifier import SessionVerifier
from fastapi_sessions.frontends.implementations import SessionCookie, CookieParameters
from typing import Dict


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


# cart manuplation




cookie_params = CookieParameters()

# Uses UUID
cookie = SessionCookie(
    cookie_name="cookie",
    identifier="general_verifier",
    auto_error=True,
    secret_key="21bb7064b863b22ea48468b01fbc24fed0f4307c7936056db0f75b4d0ff20e1b",
    cookie_params=cookie_params,
)

backend = InMemoryBackend[UUID, schemas.SessionData]()


class BasicVerifier(SessionVerifier[UUID, schemas.SessionData]):
    def __init__(
        self,
        *,
        identifier: str,
        auto_error: bool,
        backend: InMemoryBackend[UUID, schemas.SessionData],
        auth_http_exception: HTTPException,
    ):
        self._identifier = identifier
        self._auto_error = auto_error
        self._backend = backend
        self._auth_http_exception = auth_http_exception

    @property
    def identifier(self):
        return self._identifier

    @property
    def backend(self):
        return self._backend

    @property
    def auto_error(self):
        return self._auto_error

    @property
    def auth_http_exception(self):
        return self._auth_http_exception

    def verify_session(self, model: schemas.SessionData) -> bool:
        """If the session exists, it is valid"""
        return True


verifier = BasicVerifier(
    identifier="general_verifier",
    auto_error=True,
    backend=backend,
    auth_http_exception=HTTPException(status_code=403, detail="invalid session"),
)




@router.post("/create_session/{name}")
async def create_session(response: Response
                         , name : str
                         ):

    session = uuid4()
    data = schemas.SessionData(username=name)

    await backend.create(session, data)
    cookie.attach_to_response(response, session)

    return f"created session for {name}"


@router.post("/add_to_cart/{item_id}")
async def add_to_cart(quantity : int, item_id : int,response: Response,db : Session = Depends(get_db),session_id: UUID = Depends(cookie)):
    session_data = await backend.read(session_id)
    product_item = db.query(models.Product).filter(models.Product.id == item_id).first()
    
    if not product_item:
        raise HTTPException(status_code=404, detail="Product doesn't found")
    
    if not session_data:
        raise HTTPException(status_code=404, detail="Session not found")
    
    for key, value in session_data.cart_items.items():
        if key == item_id:
            # Item with item_id already exists, update the quantity
            value.quantity += quantity
            await backend.update(session_id, session_data)
            cookie.attach_to_response(response, session_id)
            return "Update"
        
        
    # Item with item_id does not exist, create a new entry
    item = schemas.CartItem(item_name=product_item.name, quantity=quantity)
    session_data.cart_items[item_id] = item
    await backend.update(session_id, session_data)
    cookie.attach_to_response(response, session_id)    
    return f"{product_item.name} added to cart with {quantity} quantity"

@router.post("/remove-item/{item_id}")
async def remove_from_cart(item_id : int,response: Response,session_id: UUID = Depends(cookie)):
    session_data = await backend.read(session_id)
    if not session_data:
        raise HTTPException(status_code=404, detail="Session not found")
    
    for key in list(session_data.cart_items.keys()):
        if key == item_id:
            session_data.cart_items.pop(key)
            await backend.update(session_id, session_data)
            cookie.attach_to_response(response, session_id)
            break
    else:
        raise HTTPException(status_code=404, detail="Not in cart please")
        
    return "Deleted from cart"
    

    



@router.get("/get_cart")
async def get_cart(session_id: UUID = Depends(cookie)):
    session_data = await backend.read(session_id)
    if not session_data:
        raise HTTPException(status_code=404, detail="Session not found")

    return session_data.cart_items


@router.post("/delete_session")
async def del_session(response: Response, session_id: UUID = Depends(cookie)):
    await backend.delete(session_id)
    cookie.delete_from_response(response)
    return "deleted session"

    
    
