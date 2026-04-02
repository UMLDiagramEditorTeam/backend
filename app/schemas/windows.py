from typing import Optional

from app.models import DiagramType
from app.schemas.base import CommonListFilters


class WindowFilters(CommonListFilters):
    type: Optional[DiagramType] = None
