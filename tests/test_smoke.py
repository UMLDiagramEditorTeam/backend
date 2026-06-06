from typing import Any
from uuid import UUID

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.email_notifications import (
    EmailNotificationAction,
    EmailNotificationModel,
)
from tests.conftest import API_PREFIX, load_fixture

pytestmark = pytest.mark.asyncio


async def register_confirm_and_login(
    client: AsyncClient,
    db_session: AsyncSession,
    user_payload: dict[str, Any],
) -> str:
    register_response = await client.post(
        f'{API_PREFIX}/auth/register',
        json=user_payload,
    )
    assert register_response.status_code == status.HTTP_201_CREATED
    registered_user = register_response.json()
    assert registered_user['email'] == user_payload['email']
    assert registered_user['status'] == 'CREATED'

    statement = select(EmailNotificationModel).where(
        EmailNotificationModel.user_id == UUID(registered_user['id']),
        EmailNotificationModel.action == EmailNotificationAction.ACCOUNT_CONFIRMATION,
        EmailNotificationModel.is_used.is_(False),
    )
    notification = (await db_session.exec(statement)).one()

    confirm_response = await client.post(
        f'{API_PREFIX}/auth/confirm-account',
        params={
            'user_id': registered_user['id'],
            'code': notification.code,
        },
    )
    assert confirm_response.status_code == status.HTTP_200_OK
    assert confirm_response.json()['status'] == 'CONFIRMED'

    login_response = await client.post(
        f'{API_PREFIX}/auth/login',
        json={
            'email': user_payload['email'],
            'password': user_payload['password'],
        },
    )
    assert login_response.status_code == status.HTTP_200_OK
    access_token = login_response.json()['access_token']
    assert access_token
    assert 'refresh_token' in login_response.cookies

    return access_token


async def test_registration_confirmation_login_and_logout_flow(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    user_payload = load_fixture('auth.json')['user']
    access_token = await register_confirm_and_login(client, db_session, user_payload)

    me_response = await client.get(
        f'{API_PREFIX}/auth/me',
        headers={'Authorization': f'Bearer {access_token}'},
    )
    assert me_response.status_code == status.HTTP_200_OK
    assert me_response.json()['email'] == user_payload['email']

    logout_response = await client.post(
        f'{API_PREFIX}/auth/logout',
        headers={'Authorization': f'Bearer {access_token}'},
    )
    assert logout_response.status_code == status.HTTP_200_OK
    assert logout_response.json() == {'success': True}
    assert logout_response.cookies.get('refresh_token') is None


async def test_code_generation_request_flow(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    user_payload = load_fixture('auth.json')['user'] | {
        'email': 'codegen.user@example.com'
    }
    fixture = load_fixture('code_generation.json')
    access_token = await register_confirm_and_login(client, db_session, user_payload)
    auth_headers = {'Authorization': f'Bearer {access_token}'}

    project_response = await client.post(
        f'{API_PREFIX}/projects/',
        headers=auth_headers,
        json=fixture['project'],
    )
    assert project_response.status_code == status.HTTP_201_CREATED
    project_id = project_response.json()['id']

    window_response = await client.post(
        f'{API_PREFIX}/projects/{project_id}/windows/',
        headers=auth_headers,
        json=fixture['window'],
    )
    assert window_response.status_code == status.HTTP_201_CREATED
    window_id = window_response.json()['id']

    class_response = await client.post(
        f'{API_PREFIX}/windows/{window_id}/classes/',
        headers=auth_headers,
        json=fixture['class'],
    )
    assert class_response.status_code == status.HTTP_201_CREATED
    class_id = class_response.json()['id']

    method_response = await client.post(
        f'{API_PREFIX}/classes/{class_id}/methods/',
        headers=auth_headers,
        json=fixture['method'],
    )
    assert method_response.status_code == status.HTTP_201_CREATED

    generation_response = await client.post(
        f'{API_PREFIX}/projects/{project_id}/windows/{window_id}/generate_code',
        headers=auth_headers,
        params={'language': 'java'},
    )
    assert generation_response.status_code == status.HTTP_200_OK
    body = generation_response.json()
    assert body['files_count'] == 1
    assert 'GreetingService.java' in body['files']
    assert 'class GreetingService' in body['files']['GreetingService.java']
    assert 'String greet(String name)' in body['files']['GreetingService.java']
