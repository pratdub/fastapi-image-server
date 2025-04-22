@app.get("/image/{image_id}/download")
async def download_image(image_id: str):
    # Retrieve the image from the MongoDB collection
    image_data = await app.mongodb["images"].find_one({"_id": image_id})
    if not image_data:
        return {"message": "Image not found"}

    # Generate a URL for the image
    image_url = f"http://localhost:8000/static/{image_data['filename']}"
    
    # Save the image to a static directory if it doesn't already exist
    static_dir = Path("static")
    static_dir.mkdir(exist_ok=True)
    file_path = static_dir / image_data["filename"]
    if not file_path.exists():
        with open(file_path, "wb") as f:
            f.write(base64.b64decode(image_data["data"]))

    return {"url": image_url}