from typing import Optional

from app.schemas.base import CommonListFilters


class InterfaceFilters(CommonListFilters):
    name: Optional[str] = None
