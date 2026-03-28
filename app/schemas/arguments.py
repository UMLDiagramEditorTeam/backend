from typing import Optional
from uuid import UUID

from app.schemas.base import CommonListFilters


class ArgumentFilters(CommonListFilters):
    method_id: Optional[UUID] = None
    name: Optional[str] = None
    type: Optional[str] = None
    order_num: Optional[int] = None
