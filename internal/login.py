from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from . import schemas
from fastapi import APIRouter,Depends,HTTPException,status
from imbuto.routers import crud
from .database import get_db
from sqlalchemy.orm import Session

router =APIRouter(
    tags=['Authentication']
)

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")




def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(db : Session = Depends(get_db),token: str =Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user =crud.get_user(db ,username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_admin_user(
    current_user: schemas.User = Depends(get_current_user)
):
    if  current_user.is_customer:
        raise HTTPException(status_code=400, detail="You're not admin user please")
    return current_user

async def get_current_customer_user(
    current_user: schemas.User = Depends(get_current_user)
):
    if  not current_user.is_customer:
        raise HTTPException(status_code=400, detail="Please you're not customer !")
    return current_user

@router.post("/token", response_model=schemas.Token)
async def login(
    request : OAuth2PasswordRequestForm =Depends(),
    db : Session = Depends(get_db)
):
    user = crud.get_user(db, request.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    password_verify =crud.verify_password(request.password , user.password)
    if not password_verify:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}