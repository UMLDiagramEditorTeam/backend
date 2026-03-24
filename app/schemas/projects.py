from typing import Optional
from uuid import UUID

from app.schemas.base import CommonListFilters


class ProjectFilters(CommonListFilters):
    user_id: Optional[UUID] = None
    name: Optional[str] = None
    is_imported: Optional[bool] = None
