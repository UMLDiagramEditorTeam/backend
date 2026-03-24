from typing import Optional
from uuid import UUID

from app.models.enums import RelationType
from app.schemas.base import CommonListFilters


class RelationFilters(CommonListFilters):
    name: Optional[str] = None
    strat_type: Optional[RelationType] = None
    end_type: Optional[RelationType] = None
    start_class_id: Optional[UUID] = None
    start_interface_id: Optional[UUID] = None
    end_class_id: Optional[UUID] = None
    end_interface_id: Optional[UUID] = None
