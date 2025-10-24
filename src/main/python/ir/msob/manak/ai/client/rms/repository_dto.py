from typing import List, Optional, Set
from pydantic import BaseModel, Field
from src.main.python.ir.msob.manak.ai.domain.audit_info import AuditInfo
from src.main.python.ir.msob.manak.ai.domain.characteristic import Characteristic
from src.main.python.ir.msob.manak.ai.domain.object_validation import ObjectValidation
from src.main.python.ir.msob.manak.ai.domain.related_action import RelatedAction


class Branch(BaseModel):
    id: Optional[str] = None
    name: str
    description: str
    status: str = "ACTIVE"
    default_branch: bool
    audit_info: Optional[AuditInfo] = None

    class Config:
        use_enum_values = True

    def __lt__(self, other: "Branch"):
        if self.name is None and other.name is None:
            return False
        if self.name is None:
            return True
        if other.name is None:
            return False
        return self.name < other.name


class RepositorySpecification(BaseModel):
    id: Optional[str] = None
    name: str
    key: Optional[str] = None
    description: Optional[str] = None
    base_url: Optional[str] = None
    token: Optional[str] = None
    branches: List[Branch] = Field(default_factory=list)
    characteristics: List[Characteristic] = Field(default_factory=list)
    object_validations: List[ObjectValidation] = Field(default_factory=list)
    related_actions: List[RelatedAction] = Field(default_factory=list)


class RepositoryDto(BaseModel):
    id: Optional[str] = None
    name: str
    description: Optional[str] = None
    path: Optional[str] = None
    tags: Set[str] = Field(default_factory=set)
    specification: Optional[RepositorySpecification] = None
    branches: List[Branch] = Field(default_factory=list)
    characteristics: List[Characteristic] = Field(default_factory=list)
    object_validations: List[ObjectValidation] = Field(default_factory=list)
    related_actions: List[RelatedAction] = Field(default_factory=list)

    def get_default_branch(self) -> Optional[Branch]:
        """
        Returns the default branch of the repository.
        First checks the repository-level branches.
        If not found, checks the specification-level branches.
        Returns None if no default branch exists.
        """
        # 1️⃣ Check repository's own branches
        for branch in self.branches:
            if branch.default_branch:
                return branch

        # 2️⃣ Check specification's branches (if specification exists)
        if self.specification and self.specification.branches:
            for branch in self.specification.branches:
                if branch.default_branch:
                    return branch

        # 3️⃣ If no default branch found
        return None
