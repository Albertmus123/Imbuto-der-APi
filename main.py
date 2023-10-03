from fastapi import FastAPI, Depends,HTTPException,status
from imbuto.routers import user, imbuto
from internal import login



app = FastAPI()

app.include_router(login.router)
app.include_router(user.router)
app.include_router(imbuto.router)


