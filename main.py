from fastapi import FastAPI, Depends,HTTPException,status
from imbuto.routers import user, imbuto
from internal import login
from starlette.middleware.sessions import SessionMiddleware



app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="c48e495259610da4741e379e0c9414c8cfa9b6751fbf2fbac01d479d448dccde")

app.include_router(login.router)
app.include_router(user.router)
app.include_router(imbuto.router)






