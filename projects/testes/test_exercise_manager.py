import pytest
import json
import os # Pode ser removido se não for usado diretamente após as mudanças

# Imports dos managers são necessários para adicionar os dados de teste
from app.exercise_manager import (
    # get_all_exercises, # Removido se não usado
    # get_exercise_by_id, # Removido se não usado
    get_exercises_by_lesson,
    add_exercise,
    # update_exercise, # Removido se não usado
    # delete_exercise, # Removido se não usado
    # run_exercise_tests, # Removido se não usado
    # EXERCISES_FILE # Removido, o manager já conhece seu arquivo
)
# from pathlib import Path # Não mais necessário para definir caminhos de dados aqui

# A definição de BASE_DIR, DATA_DIR, e EXERCISES_FILE local é removida.
# A limpeza dos arquivos de dados reais é feita pelo conftest.py.
# O exercise_manager usa o caminho correto definido internamente ou via conftest.py.

@pytest.fixture
def exercise_manager_test_data(app): # Adicionamos 'app' para garantir o contexto, se necessário
    """
    Configura dados de teste específicos para exercise_manager.
    A limpeza dos arquivos já foi feita pela fixture manage_all_data_files_for_tests em conftest.py.
    """
    test_exercises = [
        {
            "id": "ex-teste-1",
            "lesson_id": "teste-lesson",
            "title": "Exercício de Teste 1",
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
            "lesson_id": "teste-lesson",
            "title": "Exercício de Teste 2",
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
            "lesson_id": "outra-lesson",
            "title": "Exercício de Teste 3",
            "description": "Descrição do Exercício de Teste 3",
            "difficulty": "Difícil",
            "order": 1,
            "instructions": "Instruções do Exercício de Teste 3",
            "initial_code": "# Escreva seu código aqui",
            "solution_code": "print('Teste 3')",
            "test_code": "assert output.strip() == 'Teste 3'" # Adicionado .strip()
        }
    ]

    # Adicionar dados de teste.
    # Se add_exercise precisar do contexto da app, a fixture 'app' garante que ele está ativo.
    with app.app_context():
        for exercise in test_exercises:
            add_exercise(exercise)
            
    # Não há 'yield' ou limpeza aqui; conftest.py cuida da restauração/limpeza pós-teste.

def test_get_exercises_by_lesson(exercise_manager_test_data):
    """Testa a função get_exercises_by_lesson."""
    exercises = get_exercises_by_lesson("teste-lesson")
    assert len(exercises) == 2
    assert all(exercise['lesson_id'] == "teste-lesson" for exercise in exercises)
    
    # Verificar se os exercícios estão ordenados corretamente (assumindo que a ordem é preservada ou definida)
    exercise_ids = [exercise['id'] for exercise in exercises]
    assert exercise_ids == ["ex-teste-1", "ex-teste-2"] # Ou a ordem esperada

def test_get_exercises_by_lesson_empty(exercise_manager_test_data):
    """Testa a função get_exercises_by_lesson com uma lesson_id que não existe."""
    exercises = get_exercises_by_lesson("non-existent-lesson")
    assert len(exercises) == 0
