from typing import Optional

from app.schemas.base import CommonListFilters


class UserFilters(CommonListFilters):
    email: Optional[str] = None
