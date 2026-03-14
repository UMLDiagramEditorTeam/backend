from fastapi import APIRouter

router = APIRouter(prefix='/auth', tags=['auth'])


@router.post('/signup')
def signup():
    """
    Регистрация нового пользователя.
    - Принимает: username, email, password
    - Возвращает: данные пользователя и инструкцию по подтверждению email
    """
    return {
        'id': 1,
        'username': 'john_doe',
        'email': 'john@example.com',
        'message': 'User created. Please check your email to verify your account.',
    }


@router.post('/login')
def login():
    """
    Вход в систему.
    - Принимает: username/email и password
    - Возвращает: токен доступа и тип токена
    """
    return {
        'access_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...',
        'token_type': 'bearer',
        'expires_in': 3600,
    }


@router.post('/logout')
def logout():
    """
    Выход из системы (инвалидация токена).
    Требуется аутентификация.
    """
    return {'message': 'Successfully logged out'}


@router.post('/password/reset')
def request_password_reset():
    """
    Запрос на сброс пароля (отправка письма со ссылкой).
    - Принимает: email
    """
    return {'message': 'If the email exists, a reset link has been sent'}


@router.post('/password/reset/confirm')
def reset_password():
    """
    Установка нового пароля с использованием токена.
    - Принимает: token, new_password
    """
    return {'message': 'Password successfully reset'}


@router.post('/password/change')
def change_password():
    """
    Смена пароля для аутентифицированного пользователя.
    Требуется аутентификация.
    - Принимает: old_password, new_password
    """
    return {'message': 'Password successfully changed'}


@router.get('/profile')
def get_profile():
    """
    Получение профиля текущего пользователя.
    Требуется аутентификация.
    """
    return {
        'id': 1,
        'username': 'john_doe',
        'email': 'john@example.com',
        'email_verified': True,
        'created_at': '2025-01-01T10:00:00Z',
        'last_login': '2025-03-04T15:30:00Z',
    }


@router.put('/profile')
def update_profile():
    """
    Обновление данных профиля.
    Требуется аутентификация.
    - Принимает: любые обновляемые поля (username, email, и т.д.)
    """
    return {
        'id': 1,
        'username': 'john_updated',
        'email': 'john.new@example.com',
        'email_verified': False,  # после смены email требуется повторное подтверждение
        'message': 'Profile updated. Please verify your new email.',
    }


@router.delete('/profile')
def delete_profile():
    """
    Удаление аккаунта пользователя.
    Требуется аутентификация.
    - Может требовать подтверждение пароля
    """
    return {'message': 'Account successfully deleted'}
