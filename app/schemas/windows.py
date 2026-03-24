from typing import Optional
from uuid import UUID

from app.models.enums import DiagramType
from app.schemas.base import CommonListFilters


class WindowFilters(CommonListFilters):
    project_id: Optional[UUID] = None
    user_id: Optional[UUID] = None
    name: Optional[str] = None
    type: Optional[DiagramType] = None
