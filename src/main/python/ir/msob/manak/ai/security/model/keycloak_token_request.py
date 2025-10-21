from pydantic import BaseModel
from typing import Optional


class KeycloakTokenRequest(BaseModel):
    grant_type: str
    client_id: str
    client_secret: str
    scope: Optional[str] = None

    def to_dict(self) -> dict:
        return {k: v for k, v in self.dict().items() if v is not None}
