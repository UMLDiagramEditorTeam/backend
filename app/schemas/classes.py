from typing import Optional

from app.models import AccessModifier
from app.schemas.base import CommonListFilters


class ClassFilters(CommonListFilters):
    name: Optional[str] = None
    access_modifier: Optional[AccessModifier] = None
    is_abstract: Optional[bool] = None
