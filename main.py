from fastapi import FastAPI, Depends,HTTPException,status
from imbuto.routers import user, imbuto



app = FastAPI()

app.include_router(user.router)
app.include_router(imbuto.router)

