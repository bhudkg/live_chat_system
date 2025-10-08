from fastapi import FastAPI
from routers import connection


app = FastAPI()

@app.get('/healthy', tags=['Health Checks'])
def health_check():
    return {"message": "Hello World!"}


app.include_router(connection.router)
