from pydantic import BaseModel


class OutFile(BaseModel):
    url: str
    original_filename: str
