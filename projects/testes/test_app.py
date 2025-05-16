# c:\Users\lucin\OneDrive\Dev_Python\Projetos Python\Curso-Interartivo-Python\projects\testes\test_app.py
import pytest
import os
import json
import sys # Needed for test_execute_code_api
import logging

# Imports como app, add_course, add_lesson, add_exercise não são mais necessários aqui
# para o setup, pois o conftest.py e suas fixtures cuidam disso.

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Helper function (optional, for debugging)
def debug_data_files(data_dir):
    """Helper para debugar conteúdo dos arquivos de dados."""
    # Use the data_dir passed from the test context
    data_files_paths = [
        data_dir / 'courses.json',
        data_dir / 'basic' / 'lessons.json',
        data_dir / 'basic' / 'exercises.json',
        # Add other paths if needed
    ]

    for file_path in data_files_paths:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = json.load(f)
                logger.debug(f"\nConteúdo de {file_path}:\n{json.dumps(content, indent=2)}")
            except json.JSONDecodeError:
                logger.debug(f"Conteúdo de {file_path} não é JSON válido ou arquivo está vazio.")
            except Exception as e:
                 logger.debug(f"Erro ao ler {file_path}: {e}")
        else:
            logger.debug(f"Arquivo {file_path} não encontrado para debug.")

# The tests now receive 'client' and 'app_test_data' as arguments, coming from the conftest.py
def test_index_route(client, app_test_data):
    """Testa a rota inicial (index)."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Aprenda Python" in response.data

def test_course_list_route(client, app_test_data):
    """Testa a rota de listagem de cursos."""
    response = client.get('/courses')
    assert response.status_code == 200
    assert b"Cursos Dispon\xc3\xadveis" in response.data # "Cursos Disponíveis"
    assert b"Python B\xc3\xa1sico" in response.data # "Python Básico"

def test_course_detail_route(client, app_test_data):
    """Testa a rota de detalhes de um curso."""
    response = client.get('/courses/python-basico')
    assert response.status_code == 200
    assert b"Python B\xc3\xa1sico" in response.data # "Python Básico"

def test_lesson_detail_route(client, app_test_data):
    """Testa a rota de detalhes de uma lição."""
    # This test needs the 'python-basico' course and 'introducao-python' lesson to exist
    # The route is /courses/<course_id>/lessons/<lesson_id_str>
    response = client.get('/courses/python-basico/lessons/introducao-python') # Corrected path
    assert response.status_code == 200
    assert b"Introdu\xc3\xa7\xc3\xa3o ao Python" in response.data # "Introdução ao Python"
    assert b"Conte\xc3\xba" in response.data # "Conteúdo" - Assuming lesson content appears
    assert b"Exerc\xc3\xadcios:" in response.data # "Exercícios:"
    # Check for an exercise title associated with this lesson in the test data
    assert b"Ol\xc3\xa1, Mundo!" in response.data # "Olá, Mundo!" - Assuming an exercise title exists

def test_execute_code_api(client, app_test_data):
    """Testa a API de execução de código."""
    payload = {
        "code": "print('Olá, Python!')"
    }
    response = client.post('/api/execute-code', 
                          json=payload, # Use the simple payload first
                          content_type='application/json')
    # Add stderr for more complete test
    payload_with_sys = {"code": "import sys\nprint('Olá, Python!')\nprint('Erro', file=sys.stderr)"}
    assert response.status_code == 200
    data = response.get_json()
    assert 'output' in data
    assert 'Olá, Python!' in data['output']
    assert data['success'] == True

def test_check_exercise_api(client, app_test_data):
    """Testa a API de verificação de exercícios."""
    # logger.debug("Dados de teste configurados pela fixture app_test_data de conftest.py")
    # debug_data_files(app_test_data) # Descomente se precisar debugar o estado dos arquivos de dados
    
    # Use the exercise ID defined in the conftest.py test data
    exercise_id_to_test = "ex-introducao-5"
    course_id_to_test = "python-basico"

    # Test with correct solution code
    payload = {
        "course_id": course_id_to_test, # Added course_id
        "exercise_id": exercise_id_to_test,
        "code": "print('Olá, Python!')" # This matches the solution_code and should pass the test_code
    }
    
    response = client.post('/api/check-exercise', 
                          json=payload,
                          content_type='application/json')
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'success' in data
    assert data['success'] == True
    assert 'output' in data
    assert 'SUCCESS' in data['output'] # The test_code for ex-introducao-5 prints 'SUCCESS' on pass
    assert 'Olá, Python!' in data['output'] # The user code output should also be included

    # Test with incorrect solution code
    payload_incorrect = {
        "course_id": course_id_to_test, # Added course_id
        "exercise_id": exercise_id_to_test,
        "code": "print('Olá, Mundo!')" # This does NOT match the test_code assertion
    }
    
    response = client.post('/api/check-exercise', 
                          json=payload_incorrect,
                          content_type='application/json')
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'success' in data
    assert data['success'] == False # The test_code assertion should fail
    assert 'details' in data or 'output' in data # Check for error details or failure output
    # The specific error message depends on how the test_code fails and how it's captured
    # If the test_code is `assert ...`, the failure will be an AssertionError in stderr/details
    # If the test_code prints failure messages, they will be in stdout/output
    # Based on the test_code `assert 'Olá, Python!' in output\nprint('SUCCESS')`,
    # if the assertion fails, an AssertionError will be raised.
    assert 'AssertionError' in data.get('details', '') or 'AssertionError' in data.get('output', '') # Check for AssertionError

    # Test with non-existent exercise ID
    payload_nonexistent_exercise = {
        "course_id": course_id_to_test,
        "exercise_id": "non-existent-exercise",
        "code": "print('test')"
    }
    response = client.post('/api/check-exercise',
                          json=payload_nonexistent_exercise,
                          content_type='application/json')
    assert response.status_code == 404 # A API deve retornar 404 para exercício não encontrado
    data = response.get_json()
    assert 'success' in data
    assert data['success'] == False
    assert 'details' in data
    assert "Exercício 'non-existent-exercise' não encontrado" in data['details']

    # Test with non-existent course ID
    payload_nonexistent_course = {
        "course_id": "non-existent-course",
        "exercise_id": exercise_id_to_test,
        "code": "print('test')"
    }
    
    response = client.post('/api/check-exercise', 
                          json=payload_nonexistent_course,
                          content_type='application/json')
    
    assert response.status_code == 404 # A API deve retornar 404 para curso não encontrado
    data = response.get_json()
    assert 'success' in data
    assert data['success'] == False
    assert 'details' in data
    assert "Curso 'non-existent-course' não encontrado" in data['details']
