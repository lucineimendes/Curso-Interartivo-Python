import pytest
import json
import os # Pode ser removido se não for usado diretamente após as mudanças

# Os imports dos managers são necessários para adicionar os dados de teste
from app.lesson_manager import (
    # get_all_lessons, # Removido se não usado nos testes deste arquivo
    get_lesson_by_id,
    get_lessons_by_course,
    add_lesson,
    # update_lesson, # Removido se não usado
    # delete_lesson, # Removido se não usado
    get_next_lesson,
    # get_prev_lesson # Removido se não usado
)
# from pathlib import Path # Não mais necessário para definir caminhos de dados aqui

# A definição de BASE_DIR, DATA_DIR, e LESSONS_FILE local é removida.
# A limpeza dos arquivos de dados reais é feita pelo conftest.py.
# O lesson_manager usa o caminho correto definido internamente ou via conftest.py.

@pytest.fixture
def lesson_manager_test_data(app): # Adicionamos 'app' para garantir o contexto, se necessário
    """
    Configura dados de teste específicos para lesson_manager.
    A limpeza dos arquivos já foi feita pela fixture manage_all_data_files_for_tests em conftest.py.
    """
    test_lessons = [
        {
            "id": "intro-python",
            "course_id": "python-basico",
            "title": "Introdução ao Python",
            "order": 1,
            "description": "Descrição da introdução", # Adicionando campos que podem faltar
            "content": "Conteúdo da lição de introdução"
        },
        {
            "id": "variaveis",
            "course_id": "python-basico",
            "title": "Variáveis e Tipos de Dados",
            "order": 2,
            "description": "Descrição sobre variáveis",
            "content": "Conteúdo sobre variáveis"
        },
        {
            "id": "estruturas-controle",
            "course_id": "python-basico",
            "title": "Estruturas de Controle",
            "order": 3,
            "description": "Descrição sobre estruturas",
            "content": "Conteúdo sobre estruturas de controle"
        }
    ]

    # Adicionar dados de teste.
    # Se add_lesson precisar do contexto da app, a fixture 'app' garante que ele está ativo.
    with app.app_context():
        for lesson in test_lessons:
            add_lesson(lesson)
    
    # Não há 'yield' ou limpeza aqui; conftest.py cuida da restauração/limpeza pós-teste.

def test_get_next_lesson(lesson_manager_test_data):
    """Testa a função get_next_lesson."""
    next_lesson = get_next_lesson("intro-python")
    assert next_lesson is not None
    assert next_lesson['id'] == "variaveis"

def test_get_next_lesson_sequence(lesson_manager_test_data):
    """Testa a sequência de get_next_lesson."""
    lesson1 = get_next_lesson("intro-python")
    assert lesson1 is not None, "A primeira lição ('intro-python') deveria ter sido encontrada."
    lesson2 = get_next_lesson(lesson1['id'])
    assert lesson2 is not None
    assert lesson2['id'] == "estruturas-controle"

def test_get_next_lesson_invalid_id(lesson_manager_test_data):
    """Testa get_next_lesson com um ID inválido."""
    next_lesson = get_next_lesson("non-existent-lesson")
    assert next_lesson is None

def test_get_lessons_by_course(lesson_manager_test_data):
    """Testa a função get_lessons_by_course."""
    lessons = get_lessons_by_course("python-basico")
    assert len(lessons) == 3
    assert all(lesson['course_id'] == "python-basico" for lesson in lessons)

def test_get_lesson_by_id(lesson_manager_test_data):
    """Testa a função get_lesson_by_id."""
    lesson = get_lesson_by_id("intro-python")
    assert lesson is not None
    assert lesson['title'] == "Introdução ao Python"
