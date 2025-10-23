import re
from pydantic import BaseModel, model_validator

class NormalizedModel(BaseModel):

    model_config = {
        "arbitrary_types_allowed": True
    }

    @model_validator(mode="before")
    def normalize_keys(cls, data):
        """Normalize keys from camelCase, kebab-case, or mixed forms to snake_case."""
        if not isinstance(data, dict):
            return data

        def normalize_key(key: str) -> str:
            # 1️⃣ Replace dashes with underscores (kebab-case → snake_case)
            key = key.replace("-", "_")

            # 2️⃣ Insert underscore before uppercase letters (camelCase → snake_case)
            key = re.sub(r'(?<!^)(?=[A-Z])', '_', key)

            # 3️⃣ Convert everything to lowercase
            key = key.lower()

            return key

        # Rebuild the dictionary with normalized keys
        normalized = {normalize_key(k): v for k, v in data.items()}
        return normalized