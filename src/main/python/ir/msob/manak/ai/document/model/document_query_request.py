from pydantic import BaseModel

class DocumentQueryRequest(BaseModel):
    query: str
    top_k: int = 5

    model_config = {
        "arbitrary_types_allowed": True
    }
