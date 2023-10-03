from fastapi import FastAPI

from internal.database import engine
from internal import models, schemas

models.Base.metadata.create_all(bind=engine)



app = FastAPI()


@app.get('/')
def index():
    return {'message':'Imbuto Derivering System'}