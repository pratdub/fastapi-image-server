from pydantic import BaseModel

class ImageUpload(BaseModel):
    image_base64: str