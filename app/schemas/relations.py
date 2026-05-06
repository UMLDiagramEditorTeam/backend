from typing import Optional
from uuid import UUID

from app.models import RelationEndType, RelationKind
from app.schemas.base import CommonListFilters


class RelationFilters(CommonListFilters):
    type: Optional[RelationKind] = None
    begin_type: Optional[RelationEndType] = None
    end_type: Optional[RelationEndType] = None
    begin_class_id: Optional[UUID] = None
    begin_interface_id: Optional[UUID] = None
    end_class_id: Optional[UUID] = None
    end_interface_id: Optional[UUID] = None
