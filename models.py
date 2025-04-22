from pydantic import BaseModel

class ImageUpload(BaseModel):
    id: str
    image_base64: str