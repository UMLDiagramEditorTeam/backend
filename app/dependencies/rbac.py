from typing import Annotated

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, SecurityScopes

from app.dependencies.services import AuthServiceDep
from app.models.users import UserModel
from app.services.rbac import RBACService

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user_with_scopes(
    security_scopes: SecurityScopes,
    auth_service: AuthServiceDep,
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Security(bearer_scheme),
    ],
) -> UserModel:
    if credentials is None or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Not authenticated',
        )

    user = await auth_service.get_current_user_with_roles(credentials.credentials)

    if security_scopes.scopes:
        user_scopes = RBACService.collect_user_scopes(user)
        if '*' not in user_scopes:
            missing_scopes = [
                scope for scope in security_scopes.scopes if scope not in user_scopes
            ]
            if missing_scopes:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f'Missing required scopes: {", ".join(missing_scopes)}',
                )

    return user


CurrentUserWithScopesDep = Annotated[UserModel, Depends(get_current_user_with_scopes)]
