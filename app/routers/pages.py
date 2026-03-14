from fastapi import APIRouter

router = APIRouter(prefix='/pages', tags=['pages'])


@router.get('/about')
def about():
    """Информация о проекте"""
    return {
        'title': 'About UML Constructor',
        'content': 'This is a visual UML diagram constructor tool.',
        'version': '0.1.0',
    }


@router.get('/info')
def info():
    """Общая информация"""
    return {
        'title': 'Information',
        'content': 'You can create diagrams anonymously or register to save your work.',
    }


@router.get('/guide')
def guide():
    """Руководство пользователя"""
    return {
        'title': 'User Guide',
        'sections': [
            {
                'heading': 'Getting Started',
                'text': 'Some text.',
            },
            {
                'heading': 'Anonymity',
                'text': 'Some text.',
            },
            {
                'heading': 'Schemes',
                'text': 'Some text.',
            },
        ],
    }
