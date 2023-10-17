from fastapi import FastAPI, Depends,HTTPException,status
from imbuto.routers import user, imbuto
from internal import login
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configure CORS
origins = [
    "*",  # Replace with the origin of your front-end app
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


app.add_middleware(SessionMiddleware, secret_key="c48e495259610da4741e379e0c9414c8cfa9b6751fbf2fbac01d479d448dccde")

app.include_router(login.router)
app.include_router(user.router)
app.include_router(imbuto.router)






