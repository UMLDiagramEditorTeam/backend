from typing import Optional

from app.models.enums import DiagramType
from app.schemas.base import CommonListFilters


class WindowFilters(CommonListFilters):
    type: Optional[DiagramType] = None
