from typing import Optional

from app.schemas.base import CommonListFilters


class ProjectFilters(CommonListFilters):
    name: Optional[str] = None
    is_imported: Optional[bool] = None
