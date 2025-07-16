"""
Base domain model classes.

This module provides base classes for all domain models in the application.
"""

from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict


class BaseDomainModel(BaseModel):
    """Base class for all domain models.

    Domain models represent business entities in the application domain.
    They are used to enforce business rules and validation across the application.
    """

    model_config = ConfigDict(
        populate_by_name=True,
        extra="allow",
        arbitrary_types_allowed=True,
    )

    def model_dump(self, *args, **kwargs) -> Dict[str, Any]:
        """Return a dictionary representation of the model.

        This method can be overridden by subclasses to customize serialization.

        Returns:
            Dict[str, Any]: Dictionary representation of the model
        """
        return super().model_dump(*args, **kwargs)
