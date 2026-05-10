class NotFoundError(Exception):
    message = 'Ресурс не найден'


class InternalServerError(Exception):
    message = 'Внутренняя ошибка сервера'


class ForbiddenError(Exception):
    message = 'Недостаточно прав для доступа к ресурсу'


class UnauthorizedError(Exception):
    message = 'Требуется аутентификация'


class ConflictError(Exception):
    message = 'Конфликт при создании/обновлении ресурса'


class BadRequestError(Exception):
    message = 'Ошибка валидации запроса'
