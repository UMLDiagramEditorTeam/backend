from typing import Optional

from app.models import AccessModifier
from app.schemas.base import CommonListFilters


class AttributeFilters(CommonListFilters):
    name: Optional[str] = None
    access_modifier: Optional[AccessModifier] = None
    type: Optional[str] = None
    is_final: Optional[bool] = None
    is_static: Optional[bool] = None
