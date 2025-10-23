from typing import List, Optional, Set

from pydantic import Field

from src.main.python.ir.msob.manak.ai.base.normalized_model import NormalizedModel
from src.main.python.ir.msob.manak.ai.domain.audit_info import AuditInfo
from src.main.python.ir.msob.manak.ai.domain.characteristic import Characteristic
from src.main.python.ir.msob.manak.ai.domain.object_validation import ObjectValidation
from src.main.python.ir.msob.manak.ai.domain.related_action import RelatedAction


class Attachment(NormalizedModel):
    id: Optional[str] = None
    file_path: str
    status: str = "CREATED"
    file_name: str
    mime_type: str
    file_size: int
    checksum: Optional[str] = None
    audit_info: Optional[AuditInfo] = None
    order: int = 0


class DocumentSpecification(NormalizedModel):
    id: Optional[str] = None
    name: str
    description: Optional[str] = None
    key: Optional[str] = None
    storage_type: str
    characteristics: List[Characteristic] = Field(default_factory=list)
    related_actions: List[RelatedAction] = Field(default_factory=list)


class DocumentDto(NormalizedModel):
    id: Optional[str] = None
    name: str
    key: Optional[str] = None
    description: Optional[str] = None
    tags: Set[str] = Field(default_factory=set)
    specification: Optional[DocumentSpecification] = None
    attachments: List[Attachment] = Field(default_factory=list)
    characteristics: List[Characteristic] = Field(default_factory=list)
    object_validations: List[ObjectValidation] = Field(default_factory=list)
    related_actions: List[RelatedAction] = Field(default_factory=list)

    def get_latest_attachment(self) -> Optional[Attachment]:
        if not self.attachments:
            return None
        return max(self.attachments, key=lambda attachment: attachment.order)