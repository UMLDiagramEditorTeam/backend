from typing import Optional
from uuid import UUID

from app.models.enums import DiagramType
from app.schemas.base import CommonListFilters


class WindowFilters(CommonListFilters):
    project_id: UUID
    name: Optional[str] = None
    type: Optional[DiagramType] = None
