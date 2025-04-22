# main.py
from fastapi import FastAPI, UploadFile, File
from motor.motor_asyncio import AsyncIOMotorClient
from models import ImageUpload
from fastapi.responses import FileResponse
import base64
# import os
import uuid
from pathlib import Path
# from fastapi.responses import StreamingResponse
# import httpx
# from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start the database connection
    await startup_db_client(app)
    yield
    # Close the database connection
    await shutdown_db_client(app)

# method for start the MongoDb Connection
async def startup_db_client(app):
    app.mongodb_client = AsyncIOMotorClient(
        "mongodb+srv://prateeknamandubey:1234@fastapi.sjtauvt.mongodb.net/?retryWrites=true&w=majority&appName=fastapi")
    app.mongodb = app.mongodb_client.get_database("fastapi")
    print("MongoDB connected.")

# method to close the database connection
async def shutdown_db_client(app):
    app.mongodb_client.close()
    print("Database disconnected.")

# creating a server with python FastAPI
app = FastAPI(lifespan=lifespan)

@app.get("/")
async def home():
    return {"data": "Hello World"}


@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    if not file.content_type.startswith("image"):
        return {"message":"only image fils allowed "}

    contents = await file.read()
    encoded = base64.b64encode(contents).decode("utf-8")

    image_id = str(uuid.uuid4())
    image_data = {
        "_id": image_id,
        "filename": file.filename,
        "content_type": file.content_type,
        "data": encoded
    }

    # Insert the image into the MongoDB collection
    await app.mongodb["images"].insert_one(image_data)

    return {"id": image_id, "message": "Image uploaded successfully"}

@app.get("/image/{image_id}")
async def get_image(image_id: str):
    # Retrieve the image from the MongoDB collection
    image_data = await app.mongodb["images"].find_one({"_id": image_id})
    if not image_data:
        return {"message": "Image not found"}

    # Generate a URL for the image
    image_url = f"http://localhost:8000/image/{image_id}/download"
    return {"id": image_id, "url": image_url}


# Optional utility for generating ID and converting image to base64
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)















# FREEIMAGE_API_KEY = "YOUR_FREEIMAGE_API_KEY" 

# @app.post("/upload")
# async def upload_image(file: UploadFile = File(...)):
#     if not file.content_type.startswith("image/"):
#         raise HTTPException(status_code=400, detail="Only image files are allowed")

#     contents = await file.read()
#     encoded = base64.b64encode(contents).decode("utf-8")

#     payload = {
#         "key": FREEIMAGE_API_KEY,
#         "action": "upload",
#         "source": encoded,
#         "format": "json"
#     }

#     async with httpx.AsyncClient() as client:
#         response = await client.post("https://freeimage.host/api/1/upload", data=payload)
    
#     if response.status_code != 200:
#         raise HTTPException(status_code=502, detail="Failed to upload image to freeimage.host")

#     data = response.json()
#     if not data.get("image") or not data["image"].get("url"):
#         raise HTTPException(status_code=502, detail="Invalid response from freeimage.host")

#     image_url = data["image"]["url"]
#     # Generate your own unique ID for reference if needed
#     image_id = str(uuid.uuid4())

#     # Optionally, store mapping image_id -> image_url in DB or cache here

#     return JSONResponse(content={"id": image_id, "url": image_url})