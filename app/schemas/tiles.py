from typing import Optional

from app.schemas.base import CommonListFilters


class TileFilters(CommonListFilters):
    x: Optional[int] = None
    y: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
