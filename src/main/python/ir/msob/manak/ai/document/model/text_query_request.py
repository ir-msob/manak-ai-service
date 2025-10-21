from pydantic import BaseModel

class TextQueryRequest(BaseModel):
    query: str
    top_k: int = 5

    model_config = {
        "arbitrary_types_allowed": True
    }
