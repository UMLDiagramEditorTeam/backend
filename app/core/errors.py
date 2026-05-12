class NotFoundError(Exception):
    message = 'Ресурс не найден'

    def __init__(self, message: str = None):
        self.message = message if message is not None else self.message
        super().__init__(self.message)


class InternalServerError(Exception):
    message = 'Внутренняя ошибка сервера'

    def __init__(self, message: str = None):
        self.message = message if message is not None else self.message
        super().__init__(self.message)


class ForbiddenError(Exception):
    message = 'Недостаточно прав для доступа к ресурсу'

    def __init__(self, message: str = None):
        self.message = message if message is not None else self.message
        super().__init__(self.message)


class UnauthorizedError(Exception):
    message = 'Требуется аутентификация'

    def __init__(self, message: str = None):
        self.message = message if message is not None else self.message
        super().__init__(self.message)


class ConflictError(Exception):
    message = 'Конфликт при создании/обновлении ресурса'

    def __init__(self, message: str = None):
        self.message = message if message is not None else self.message
        super().__init__(self.message)


class BadRequestError(Exception):
    message = 'Ошибка валидации запроса'

    def __init__(self, message: str = None):
        self.message = message if message is not None else self.message
        super().__init__(self.message)
