# main.py
from fastapi import FastAPI, UploadFile, File, Request
from fastapi.staticfiles import StaticFiles
from motor.motor_asyncio import AsyncIOMotorClient
from models import CheckImageRequest, ImageUpload
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
from bson import ObjectId

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


app.mount("/images", StaticFiles(directory="images"), name="images")


@app.post("/upload")
async def upload_image(image: ImageUpload, request: Request):
    image_id = image.id

    # Check if the ID already exists in the database
    existing_image = await app.mongodb["images"].find_one({"_id": image_id})
    if existing_image:
        return {
            "status": "error",
            "message": "ID already exists"
        }, 400

    image_data = {
        "_id": image_id,
        "filename": f"{image_id}.png",
        "content_type": "image/png",
        "data": image.image_base64
    }

    await app.mongodb["images"].insert_one(image_data)

    image_path = Path(f"./images/{image_id}.png")
    image_path.parent.mkdir(parents=True, exist_ok=True)

    with open(image_path, "wb") as image_file:
        image_file.write(base64.b64decode(image.image_base64))

    image_url = f"{request.base_url}images/{image_id}.png"

    return {
        "status": "saved",
        "id": image_id,
        "url": image_url
    }

@app.post("/image/check")
async def check_image(image: CheckImageRequest, request: Request):
    image_id=image.id
    # Check if the image exists in the /images/ folder with .jpg or .png extension
    image_path_jpg = Path(f"./images/{image_id}.jpg")
    image_path_png = Path(f"./images/{image_id}.png")

    if image_path_jpg.exists():
        image_url = f"{request.base_url}images/{image_id}.jpg"
        return {"exists": 1, "image_url": image_url}, 200
    elif image_path_png.exists():
        image_url = f"{request.base_url}images/{image_id}.png"
        return {"exists": 1, "image_url": image_url}, 200

    # If not found in the folder, check the MongoDB collection
    image_data = await app.mongodb["images"].find_one({"_id": image_id})
    if not image_data:
        return {"exists": 0, "message": "Image not found"}, 404

    # Decode the base64 image data and save it to the /images/ folder
    image_extension = "jpg" if image_data["content_type"] == "image/jpeg" else "png"
    image_path = Path(f"./images/{image_id}.{image_extension}")
    image_path.parent.mkdir(parents=True, exist_ok=True)

    with open(image_path, "wb") as image_file:
        image_file.write(base64.b64decode(image_data["data"]))

    # Generate the image URL
    image_url = f"{request.base_url}images/{image_id}.{image_extension}"
    return {"exists": 1, "image_url": image_url}, 200

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

# @app.get("/image/{image_id}")
# async def get_image(image_id: str, request: Request):
#     # Check if the image exists in the /images/ folder with .jpg or .png extension
#     image_path_jpg = Path(f"./images/{image_id}.jpg")
#     image_path_png = Path(f"./images/{image_id}.png")

#     if image_path_jpg.exists():
#         image_url = f"{request.base_url}images/{image_id}.jpg"
#         return {"image_url": image_url}
#     elif image_path_png.exists():
#         image_url = f"{request.base_url}images/{image_id}.png"
#         return {"image_url": image_url}

#     # If not found in the folder, check the MongoDB collection
#     image_data = await app.mongodb["images"].find_one({"_id": image_id})
#     if not image_data:
#         return {"error": "Image not found"}, 404

#     # Decode the base64 image data and save it to the /images/ folder
#     image_extension = "jpg" if image_data["content_type"] == "image/jpeg" else "png"
#     image_path = Path(f"./images/{image_id}.{image_extension}")
#     image_path.parent.mkdir(parents=True, exist_ok=True)

#     with open(image_path, "wb") as image_file:
#         image_file.write(base64.b64decode(image_data["data"]))

#     # Generate the image URL
#     image_url = f"{request.base_url}images/{image_id}.{image_extension}"
#     return {"image_url": image_url}




















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