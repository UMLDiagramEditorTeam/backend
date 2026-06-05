from typing import Annotated
from uuid import UUID

from fastapi import Depends

from app.core.config import settings
from app.core.errors import ForbiddenError, NotFoundError
from app.dependencies.auth import CurrentUserDep
from app.dependencies.services import (
    AttributeServiceDep,
    ClassServiceDep,
    InterfaceServiceDep,
    MethodServiceDep,
    ProjectServiceDep,
    RelationServiceDep,
    WindowServiceDep,
)
from app.models import AttributeModel, InterfaceModel, MethodModel, RelationModel
from app.models.classes import ClassModel
from app.models.projects import ProjectModel
from app.models.users import UserModel
from app.models.windows import WindowModel


async def _check_project_ownership(
    project_id: UUID,
    project_service: ProjectServiceDep,
    current_user: UserModel,
) -> ProjectModel:
    project = await project_service.get_project(project_id)
    if project is None:
        raise NotFoundError()

    if project.user_id != current_user.id:
        user_roles = (
            {role.name for role in current_user.roles}
            if hasattr(current_user, 'roles')
            else set()
        )
        if settings.rbac.admin_role not in user_roles:
            raise ForbiddenError()

    return project


async def get_verified_project(
    project_id: UUID,
    project_service: ProjectServiceDep,
    current_user: CurrentUserDep,
) -> ProjectModel:
    return await _check_project_ownership(project_id, project_service, current_user)


ProjectVerifiedDep = Annotated[ProjectModel, Depends(get_verified_project)]


async def get_verified_window(
    window_id: UUID,
    window_service: WindowServiceDep,
    project: ProjectVerifiedDep,
) -> WindowModel:
    window = await window_service.get_window(window_id)
    if window is None or window.project_id != project.id:
        raise NotFoundError()
    return window


WindowVerifiedDep = Annotated[WindowModel, Depends(get_verified_window)]


async def get_verified_window_standalone(
    window_id: UUID,
    window_service: WindowServiceDep,
    project_service: ProjectServiceDep,
    current_user: CurrentUserDep,
) -> WindowModel:
    window = await window_service.get_window(window_id)
    if window is None:
        raise NotFoundError()
    await _check_project_ownership(window.project_id, project_service, current_user)
    return window


WindowStandaloneVerifiedDep = Annotated[
    WindowModel, Depends(get_verified_window_standalone)
]


async def get_verified_class(
    class_id: UUID,
    class_service: ClassServiceDep,
    window: WindowStandaloneVerifiedDep,
) -> ClassModel:
    class_obj = await class_service.get_class(class_id)
    if class_obj is None or class_obj.window_id != window.id:
        raise NotFoundError()
    return class_obj


ClassVerifiedDep = Annotated[ClassModel, Depends(get_verified_class)]


async def get_verified_class_standalone(
    class_id: UUID,
    class_service: ClassServiceDep,
    window_service: WindowServiceDep,
    project_service: ProjectServiceDep,
    current_user: CurrentUserDep,
) -> ClassModel:
    class_obj = await class_service.get_class(class_id)
    if class_obj is None:
        raise NotFoundError()
    window = await window_service.get_window(class_obj.window_id)
    if window is None:
        raise NotFoundError()
    await _check_project_ownership(window.project_id, project_service, current_user)
    return class_obj


ClassStandaloneVerifiedDep = Annotated[
    ClassModel, Depends(get_verified_class_standalone)
]


async def get_verified_interface(
    interface_id: UUID,
    interface_service: InterfaceServiceDep,
    window: WindowStandaloneVerifiedDep,
) -> InterfaceModel:
    interface = await interface_service.get_interface(interface_id)
    if interface is None or interface.window_id != window.id:
        raise NotFoundError()
    return interface


InterfaceVerifiedDep = Annotated[InterfaceModel, Depends(get_verified_interface)]


async def get_verified_interface_standalone(
    interface_id: UUID,
    interface_service: InterfaceServiceDep,
    window_service: WindowServiceDep,
    project_service: ProjectServiceDep,
    current_user: CurrentUserDep,
) -> InterfaceModel:
    interface = await interface_service.get_interface(interface_id)
    if interface is None:
        raise NotFoundError()
    window = await window_service.get_window(interface.window_id)
    if window is None:
        raise NotFoundError()
    await _check_project_ownership(window.project_id, project_service, current_user)
    return interface


InterfaceStandaloneVerifiedDep = Annotated[
    InterfaceModel, Depends(get_verified_interface_standalone)
]


async def get_verified_attribute(
    attribute_id: UUID,
    attribute_service: AttributeServiceDep,
    class_obj: ClassStandaloneVerifiedDep,
) -> AttributeModel:
    attribute = await attribute_service.get_attribute(attribute_id)
    if attribute is None or attribute.class_id != class_obj.id:
        raise NotFoundError()
    return attribute


AttributeVerifiedDep = Annotated[AttributeModel, Depends(get_verified_attribute)]


async def get_verified_class_method(
    method_id: UUID,
    method_service: MethodServiceDep,
    class_obj: ClassStandaloneVerifiedDep,
) -> MethodModel:
    method = await method_service.get_method(method_id)
    if method is None or method.class_id != class_obj.id:
        raise NotFoundError()
    return method


ClassMethodVerifiedDep = Annotated[MethodModel, Depends(get_verified_class_method)]


async def get_verified_interface_method(
    method_id: UUID,
    method_service: MethodServiceDep,
    interface: InterfaceStandaloneVerifiedDep,
) -> MethodModel:
    method = await method_service.get_method(method_id)
    if method is None or method.interface_id != interface.id:
        raise NotFoundError()
    return method


InterfaceMethodVerifiedDep = Annotated[
    MethodModel, Depends(get_verified_interface_method)
]


async def get_verified_relation(
    relation_id: UUID,
    relation_service: RelationServiceDep,
    window: WindowStandaloneVerifiedDep,
) -> RelationModel:
    relation = await relation_service.get_relation(relation_id)
    if relation is None or relation.window_id != window.id:
        raise NotFoundError()
    return relation


RelationVerifiedDep = Annotated[RelationModel, Depends(get_verified_relation)]
