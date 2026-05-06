from typing import Annotated

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import SecurityScopes

from app.core.security import oauth2_scheme
from app.dependencies.auth import AuthServiceDep
from app.dependencies.services import RBACServiceDep
from app.models.users import UserModel


async def get_current_user_with_scopes(
    security_scopes: SecurityScopes,
    auth_service: AuthServiceDep,
    rbac_service: RBACServiceDep,
    access_token: Annotated[str, Security(oauth2_scheme)],
) -> UserModel:
    user = await auth_service.get_current_user_with_roles(access_token)

    if security_scopes.scopes:
        user_scopes = rbac_service.collect_user_scopes(user)
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
