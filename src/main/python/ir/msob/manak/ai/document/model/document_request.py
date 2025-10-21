from pydantic import BaseModel

class DocumentRequest(BaseModel):
    file_path: str
    filename: str
    file_type: str

    model_config = {
        "arbitrary_types_allowed": True
    }
