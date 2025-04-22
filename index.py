


@app.get("/image/{image_id}")
async def get_image(image_id: str):
    # Retrieve the image from the MongoDB collection
    image_data = await app.mongodb["images"].find_one({"_id": image_id})
    if not image_data:
        return {"message": "Image not found"}

    # Generate a URL for the image
    image_url = f"http://localhost:8000/image/{image_id}/download"
    return {"id": image_id, "url": image_url}