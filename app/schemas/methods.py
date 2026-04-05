from typing import Optional

from app.models import AccessModifier
from app.schemas.base import CommonListFilters


class MethodFilters(CommonListFilters):
    name: Optional[str] = None
    access_modifier: Optional[AccessModifier] = None
    return_type: Optional[str] = None
