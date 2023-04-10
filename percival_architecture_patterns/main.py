from fastapi import FastAPI
from dotenv import dotenv_values
from pymongo import MongoClient
from percival_architecture_patterns.entrypoints.http.batch import batch_router
from percival_architecture_patterns.entrypoints.http.order import order_line_router

config = dotenv_values(".env")

app = FastAPI()


@app.on_event("startup")
def startup_db_client():
    app.mongodb_client = MongoClient(config["ATLAS_URI"])
    app.database = app.mongodb_client[config["DB_NAME"]]
    print(f"Connected to MongoDB database: {app.database}")


@app.on_event("shutdown")
def shutdown_db_client():
    app.mongodb_client.close()


@app.get("/")
async def root():
    return {"message": "Welcome to our batch project, with FastAPI and MongoDB!"}


app.include_router(batch_router)
app.include_router(order_line_router)
