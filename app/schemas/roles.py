from pydantic import BaseModel


class UpdateUserRolesRequest(BaseModel):
    roles: list[str]
