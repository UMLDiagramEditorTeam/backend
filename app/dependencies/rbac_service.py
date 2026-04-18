from typing import Annotated

from fastapi import Depends

from app.dependencies.session import SessionDep
from app.services.rbac import RBACService


async def get_rbac_service(session: SessionDep) -> RBACService:
    return RBACService(session)


RBACServiceDep = Annotated[RBACService, Depends(get_rbac_service)]
