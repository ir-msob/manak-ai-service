from typing import List

from src.main.python.ir.msob.manak.ai.base.response_model import ResponseModel

class User(ResponseModel):
    id: str | None = None
    sessionId: str | None = None
    name: str | None = None
    username: str | None = None
    roles: List[str] | None = None
    audience: str | None = None
    classType: str = "User"

SYSTEM_USER = User(
    id="00000000-0000-0000-0000-000000000000",
    sessionId="00000000-0000-0000-0000-000000000000",
    name="system",
    username="system",
    roles=["adm"],
    audience="w"
)
