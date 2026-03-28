from typing import Optional
from uuid import UUID

from app.schemas.base import CommonListFilters


class InterfaceFilters(CommonListFilters):
    window_id: UUID
    name: Optional[str] = None
