from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status

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
from app.models.windows import WindowModel


async def get_verified_project(
    project_id: UUID,
    project_service: ProjectServiceDep,
    current_user: CurrentUserDep,
) -> ProjectModel:
    project = await project_service.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    if project.user_id != current_user.id:
        user_roles = (
            {role.name for role in current_user.roles}
            if hasattr(current_user, 'roles')
            else set()
        )
        if 'admin' not in user_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    return project


ProjectVerifiedDep = Annotated[ProjectModel, Depends(get_verified_project)]


async def get_verified_window(
    window_id: UUID,
    window_service: WindowServiceDep,
    project: ProjectVerifiedDep,
) -> WindowModel:
    window = await window_service.get_window(window_id)
    if window is None or window.project_id != project.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return window


WindowVerifiedDep = Annotated[WindowModel, Depends(get_verified_window)]


async def get_verified_class(
    class_id: UUID,
    class_service: ClassServiceDep,
    window: WindowVerifiedDep,
) -> ClassModel:
    class_obj = await class_service.get_class(class_id)
    if class_obj is None or class_obj.window_id != window.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return class_obj


ClassVerifiedDep = Annotated[ClassModel, Depends(get_verified_class)]


async def get_verified_interface(
    interface_id: UUID,
    interface_service: InterfaceServiceDep,
    window: WindowVerifiedDep,
) -> InterfaceModel:
    interface = await interface_service.get_interface(interface_id)
    if interface is None or interface.window_id != window.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return interface


InterfaceVerifiedDep = Annotated[InterfaceModel, Depends(get_verified_interface)]


async def get_verified_attribute(
    attribute_id: UUID,
    attribute_service: AttributeServiceDep,
    class_obj: ClassVerifiedDep,
) -> AttributeModel:
    attribute = await attribute_service.get_attribute(attribute_id)
    if attribute is None or attribute.class_id != class_obj.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return attribute


AttributeVerifiedDep = Annotated[AttributeModel, Depends(get_verified_attribute)]


async def get_verified_class_method(
    method_id: UUID,
    method_service: MethodServiceDep,
    class_obj: ClassVerifiedDep,
) -> MethodModel:
    method = await method_service.get_method(method_id)
    if method is None or method.class_id != class_obj.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return method


ClassMethodVerifiedDep = Annotated[MethodModel, Depends(get_verified_class_method)]


async def get_verified_interface_method(
    method_id: UUID,
    method_service: MethodServiceDep,
    interface: InterfaceVerifiedDep,
) -> MethodModel:
    method = await method_service.get_method(method_id)
    if method is None or method.interface_id != interface.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return method


InterfaceMethodVerifiedDep = Annotated[
    MethodModel, Depends(get_verified_interface_method)
]


async def get_verified_relation(
    relation_id: UUID,
    relation_service: RelationServiceDep,
    window: WindowVerifiedDep,
) -> RelationModel:
    relation = await relation_service.get_relation(relation_id)
    if relation is None or relation.window_id != window.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return relation


RelationVerifiedDep = Annotated[RelationModel, Depends(get_verified_relation)]
