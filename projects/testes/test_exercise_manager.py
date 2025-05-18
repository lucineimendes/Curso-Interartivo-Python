from flask import Flask
import pytest
import logging # Para logs de teste

# A função add_exercise foi removida do exercise_manager.
from projects.exercise_manager import get_exercise_by_id

logger = logging.getLogger(__name__)


# A definição de BASE_DIR, DATA_DIR, e EXERCISES_FILE local é removida.
# A limpeza dos arquivos de dados reais é feita pelo conftest.py.
# O exercise_manager usa o caminho correto definido internamente ou via conftest.py.

@pytest.fixture
def exercise_manager_test_data(app_test_data): # Depende diretamente de app_test_data
    """
    Fornece os dados de teste que deveriam estar nos arquivos JSON de exercícios.
    A fixture 'app_test_data' (de conftest.py) já criou os arquivos temporários
    com esses dados. Esta fixture apenas retorna os dados para facilitar as asserções.
    """
    logger.debug("Fixture exercise_manager_test_data: Fornecendo dados de teste de exercícios (já criados por app_test_data).")
    # Estes são os dados que a fixture app_test_data em conftest.py
    # deveria ter escrito nos arquivos temporários.
    # Ex: python-intermediario/exercises.json e python-avancado/exercises.json
    # Os testes de get_exercise_by_id vão ler desses arquivos temporários.
    test_exercises = [
        {
            "id": "ex-teste-1",
            "lesson_id": "lesson-interm-1", # Usar IDs de lição que podem existir nos dados de teste de lição
            "title": "Exercício de Teste 1",
            "course_id": "python-intermediario", # Adicionar course_id para a lógica de add_exercise
            "description": "Descrição do Exercício de Teste 1",
            "difficulty": "Fácil",
            "order": 1,
            "instructions": "Instruções do Exercício de Teste 1",
            "initial_code": "# Escreva seu código aqui",
            "solution_code": "print('Teste 1')",
            "test_code": "assert output.strip() == 'Teste 1'" # Adicionado .strip() para consistência
        },
        {
            "id": "ex-teste-2",
            "lesson_id": "lesson-interm-1",
            "title": "Exercício de Teste 2",
            "course_id": "python-intermediario",
            "description": "Descrição do Exercício de Teste 2",
            "difficulty": "Médio",
            "order": 2,
            "instructions": "Instruções do Exercício de Teste 2",
            "initial_code": "# Escreva seu código aqui",
            "solution_code": "print('Teste 2')",
            "test_code": "assert output.strip() == 'Teste 2'" # Adicionado .strip()
        },
        {
            "id": "ex-teste-3",
            "lesson_id": "lesson-adv-1", # Usar IDs de lição que podem existir nos dados de teste de lição
            "title": "Exercício de Teste 3",
            "course_id": "python-avancado", # Adicionar course_id
            "description": "Descrição do Exercício de Teste 3",
            "difficulty": "Difícil",
            "order": 1,
            "instructions": "Instruções do Exercício de Teste 3",
            "initial_code": "# Escreva seu código aqui",
            "solution_code": "print('Teste 3')",
            "test_code": "assert output.strip() == 'Teste 3'" # Adicionado .strip()
        }
    ]

    # Não precisamos mais adicionar dinamicamente aqui, pois app_test_data
    # já deve ter criado os arquivos JSON com esses dados.
    return test_exercises # Retorna os dados para referência nos testes

    # Não há 'yield' ou limpeza aqui; conftest.py cuida da restauração/limpeza pós-teste.

# def test_get_exercises_by_lesson(exercise_manager_test_data: None):
#     """Testa a função get_exercises_by_lesson."""
#     exercises = get_exercises_by_lesson("teste-lesson")
#     assert len(exercises) == 2
#     assert all(exercise['lesson_id'] == "teste-lesson" for exercise in exercises)
    
#     # Verificar se os exercícios estão ordenados corretamente (assumindo que a ordem é preservada ou definida)
#     exercise_ids = [exercise['id'] for exercise in exercises]
#     assert exercise_ids == ["ex-teste-1", "ex-teste-2"] # Ou a ordem esperada

# def test_get_exercises_by_lesson_empty(exercise_manager_test_data: None):
#     """Testa a função get_exercises_by_lesson com uma lesson_id que não existe."""
#     exercises = get_exercises_by_lesson("non-existent-lesson")
#     assert len(exercises) == 0

def test_get_exercise_by_id_existing(exercise_manager_test_data):
    """Testa a função get_exercise_by_id com um ID existente."""
    # Pega o primeiro exercício dos dados de teste para garantir que ele existe
    exercise_to_find = exercise_manager_test_data[0]
    exercise_id = exercise_to_find["id"]
    course_id = exercise_to_find["course_id"]

    logger.debug(f"Testando get_exercise_by_id para ID: {exercise_id} no curso {course_id}")
    exercise = get_exercise_by_id(exercise_id, course_id=course_id)

    assert exercise is not None
    assert exercise['id'] == exercise_id
    assert exercise['title'] == exercise_to_find['title']
    assert exercise['description'] == exercise_to_find['description']
    assert exercise['difficulty'] == exercise_to_find['difficulty']
    assert exercise['lesson_id'] == exercise_to_find['lesson_id']
    assert exercise['course_id'] == course_id # Verifica se o course_id está presente no retorno

def test_get_exercise_by_id_non_existent(exercise_manager_test_data):
    """Testa a função get_exercise_by_id com um ID que não existe."""
    logger.debug("Testando get_exercise_by_id para um ID não existente.")
    # Assume que 'python-intermediario' é um course_id válido criado pela fixture
    exercise = get_exercise_by_id("non-existent-id", course_id="python-intermediario")
    assert exercise is None

# O teste test_add_duplicate_exercise_id foi removido pois add_exercise não existe mais.
