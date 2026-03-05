from datetime import datetime
from uuid import UUID, uuid4

from fastapi import APIRouter

router = APIRouter(prefix='/diagrams', tags=['diagrams'])


@router.post('/create')
def create_basic_uml():
    """
    Создание новой диаграммы.
    Анонимно или для авторизованного пользователя.
    """
    return {
        'uuid': str(uuid4()),
        'title': 'New Basic UML Diagram',
        'owner_id': None,
        'created_at': datetime.utcnow().isoformat(),
    }


@router.get('/{diagram_uuid}')
def get_diagram(diagram_uuid: UUID):
    """
    Получение диаграммы по UUID.
    Доступно без аутентификации (для анонимных диаграмм).
    """
    return {
        'uuid': diagram_uuid,
        'type': 'basic-uml',
        'title': 'My Class Diagram',
        'owner_id': 1,
        'created_at': '2025-03-04T12:00:00Z',
        'interfaces': [{'id': 1, 'name': 'Drawable', 'methods': [101]}],
        'attributes': [
            {
                'id': 201,
                'name': 'color',
                'access_modifier': 'private',
                'type': 'string',
                'is_final': False,
                'is_static': False,
            }
        ],
        'methods': [
            {
                'id': 101,
                'name': 'draw',
                'access_modifier': 'public',
                'type': 'void',
                'is_final': False,
                'is_static': False,
            }
        ],
        'relations': [
            {
                'id': 301,
                'name': 'inheritance',
                'start_type': 'inheritance',
                'end_type': 'inheritance',
                'start_element_id': 1,
                'end_element_id': 101,
            }
        ],
    }


@router.post('/{diagram_uuid}/export')
def export_diagram(diagram_uuid: UUID):
    """
    Экспорт диаграммы в различных форматах.
    - Принимает: format (png, svg, pdf, etc.)
    - Возвращает: ссылку на файл или base64
    """
    return {
        'uuid': diagram_uuid,
        'format': 'png',
        'url': f'/static/exports/{diagram_uuid}.png',
        'filename': f'diagram_{diagram_uuid}.png',
    }


@router.post('/{diagram_uuid}/save')
def save_diagram(diagram_uuid: str):
    """
    Сохранение диаграммы (привязка к пользователю или обновление).
    - Для анонимных: требует аутентификации, становится личной
    - Для личных: просто обновляет
    """
    return {
        'uuid': diagram_uuid,
        'owner_id': 1,
        'type': 'basic-uml',
        'title': 'Saved Diagram',
        'created_at': '2025-03-04T12:00:00Z',
        'message': 'Diagram saved successfully',
    }


@router.post('/{diagram_uuid}/generate-code')
def generate_code(diagram_uuid: UUID):
    """
    Генерация кода по диаграмме.
    - Принимает: language (python, java, cpp, etc.)
    - Возвращает: сгенерированный код
    """
    return {
        'uuid': diagram_uuid,
        'language': 'python',
        'code': """# Generated from UML diagram
class Drawable:
    def draw(self) -> None:
        pass

class Shape(Drawable):
    def __init__(self, color: str):
        self._color = color

    def draw(self) -> None:
        print(f"Drawing {self._color} shape")""",
    }


@router.put('/{diagram_uuid}')
def update_diagram(diagram_uuid: UUID):
    """
    Полное обновление диаграммы.
    """
    return {
        'uuid': diagram_uuid,
        'type': 'basic-uml',
        'title': 'Updated Diagram Title',
        'owner_id': 1,
        'created_at': '2025-03-04T12:00:00Z',
        'interfaces': [],
        'attributes': [],
        'methods': [],
        'relations': [],
    }


@router.delete('/{diagram_uuid}')
def delete_diagram(diagram_uuid: UUID):
    """
    Удаление диаграммы.
    """
    return {'message': f'Diagram {diagram_uuid} successfully deleted'}


@router.get('/my')
def list_user_diagrams():
    """
    Список всех диаграмм текущего пользователя.
    Требуется аутентификация.
    """
    return {
        'diagrams': [
            {
                'uuid': '123e4567-e89b-12d3-a456-426614174000',
                'type': 'basic-uml',
                'title': 'Project Alpha',
                'created_at': '2025-03-01T10:00:00Z',
            },
            {
                'uuid': '223e4567-e89b-12d3-a456-426614174001',
                'type': 'seq-uml',
                'title': 'Login Sequence',
                'created_at': '2025-03-02T11:00:00Z',
            },
        ],
        'total': 2,
    }
