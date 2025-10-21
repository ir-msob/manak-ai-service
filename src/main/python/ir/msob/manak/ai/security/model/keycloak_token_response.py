from pydantic import BaseModel, Field
from typing import Optional


class KeycloakTokenResponse(BaseModel):
    # Required fields that are always present
    access_token: str
    expires_in: int
    token_type: str
    scope: str

    # Optional fields that might not be present
    refresh_expires_in: Optional[int] = None
    refresh_token: Optional[str] = None
    not_before_policy: Optional[int] = Field(None, alias='not-before-policy')
    session_state: Optional[str] = Field(None, alias='session-state')

    class Config:
        populate_by_name = True
        extra = 'ignore'  # This is crucial to ignore any missing fields