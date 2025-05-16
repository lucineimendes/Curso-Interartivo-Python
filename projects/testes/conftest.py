# c:\Users\lucin\OneDrive\Dev_Python\Projetos Python\Curso-Interartivo-Python\projects\testes\conftest.py
import pytest
import json
import os
from pathlib import Path
import shutil
import logging
import sys

# Adiciona o diretório raiz do projeto ao sys.path
# O arquivo conftest.py está em projects/testes/
# .parent é o diretório 'testes'
# .parent.parent é o diretório 'projects'
# .parent.parent.parent é o diretório raiz do projeto 'Curso-Interartivo-Python'
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Agora as importações a partir de 'projects' devem funcionar
from projects.app import app as flask_app
# Importa a instância global do course_mgr do módulo app
from projects.app import course_mgr as app_course_manager_instance

logger = logging.getLogger(__name__)

@pytest.fixture(scope='function') # Use function scope so patching is isolated per test
def app():
    """Provides the Flask app instance for testing."""
    # Configure the app for testing
    flask_app.config.update({
        "TESTING": True,
        # Add other test configurations if needed
        # "SECRET_KEY": "testing",
        # "WTF_CSRF_ENABLED": False,
    })

    # The app instance is created for each test function
    yield flask_app

@pytest.fixture
def client(app):
    """Provides a test client for the Flask app."""
    # Use the app fixture to get the app instance
    return app.test_client()

@pytest.fixture(autouse=True) # autouse=True means this fixture runs for every test automatically
def app_test_data(app, tmp_path, monkeypatch):
    """
    Sets up temporary data files for tests and patches managers.
    This fixture runs automatically before each test.
    """
    logger.debug("Setting up temporary test data...")

    # Create a temporary data directory structure
    test_data_dir = tmp_path / 'data'
    test_data_dir.mkdir()
    basic_dir = test_data_dir / 'basic'
    basic_dir.mkdir()
    intermediate_dir = test_data_dir / 'intermediate'
    intermediate_dir.mkdir()
    advanced_dir = test_data_dir / 'advanced'
    advanced_dir.mkdir()

    # Define minimal test data
    test_courses_data = [
        {
            "id": "python-basico",
            "name": "Python Básico",
            "short_description": "Introdução aos fundamentos.",
            "level": "Básico",
            "duration": "10 horas",
            "lessons_file": "basic/lessons.json",
            "exercises_file": "basic/exercises.json"
        },
        {
            "id": "python-intermediario",
            "name": "Python Intermediário",
            "short_description": "Estruturas de dados e POO.",
            "level": "Intermediário",
            "duration": "15 horas",
            "lessons_file": "intermediate/lessons.json",
            "exercises_file": "intermediate/exercises.json"
        },
         {
            "id": "python-avancado",
            "name": "Python Avançado",
            "short_description": "Tópicos avançados e frameworks.",
            "level": "Avançado",
            "duration": "20 horas",
            "lessons_file": "advanced/lessons.json",
            "exercises_file": "advanced/exercises.json"
        }
    ]

    # Minimal lesson data for the basic course
    test_basic_lessons_data = [
        {
            "id": "introducao-python",
            "title": "Introdução ao Python",
            "description": "Primeiros passos.",
            "order": 1,
            "content": "<p>Conteúdo da introdução.</p>",
            "course_id": "python-basico"
        }
    ]

    # Minimal exercise data for the basic course
    test_basic_exercises_data = [
         {
            "id": "ex-introducao-5", # This ID is used in test_check_exercise_api
            "lesson_id": "introducao-python",
            "title": "Teste de API",
            "description": "Teste da API de verificação.",
            "difficulty": "Fácil",
            "order": 5,
            "instructions": "Imprima 'Olá, Python!'",
            "initial_code": "print('Olá, Mundo!')",
            "solution_code": "print('Olá, Python!')",
            "test_code": "assert 'Olá, Python!' in output\nprint('SUCCESS')", # test_code should print SUCCESS on pass
            "level": "básico"
        },
        {
            "id": "ex-introducao-1", # Add another exercise for lesson_detail_route test
            "lesson_id": "introducao-python",
            "title": "Olá, Mundo!",
            "description": "Escreva um programa que imprima 'Olá, Mundo!' na tela.",
            "difficulty": "Fácil",
            "order": 1,
            "instructions": "Use a função print() para exibir a mensagem.",
            "initial_code": "# Escreva seu código aqui",
            "solution_code": "print('Olá, Mundo!')",
            "test_code": "assert output.strip() == 'Olá, Mundo!'",
            "level": "básico"
        }
    ]

    # Write the test data files
    with open(test_data_dir / 'courses.json', 'w', encoding='utf-8') as f:
        json.dump(test_courses_data, f, indent=4, ensure_ascii=False)

    with open(basic_dir / 'lessons.json', 'w', encoding='utf-8') as f:
        json.dump(test_basic_lessons_data, f, indent=4, ensure_ascii=False)

    with open(basic_dir / 'exercises.json', 'w', encoding='utf-8') as f:
        json.dump(test_basic_exercises_data, f, indent=4, ensure_ascii=False)

    # Patch the CourseManager instance's data_dir attribute.
    # 'app_course_manager_instance' é a instância global do CourseManager importada de projects.app
    monkeypatch.setattr(app_course_manager_instance, 'data_dir', test_data_dir)
    logger.debug(f"Patched app_course_manager_instance.data_dir to: {app_course_manager_instance.data_dir}")

    # Reload courses in the patched manager instance so it reads from the temporary file
    app_course_manager_instance.courses = app_course_manager_instance._load_courses()
    logger.debug(f"Reloaded courses in patched CourseManager. Count: {len(app_course_manager_instance.courses)}")

    # Patch the DATA_DIR global in LessonManager and ExerciseManager modules
    # This is necessary because their load methods use this global.
    from projects import lesson_manager, exercise_manager
    monkeypatch.setattr(lesson_manager, 'DATA_DIR', test_data_dir)
    monkeypatch.setattr(exercise_manager, 'DATA_DIR', test_data_dir)
    logger.debug(f"Patched LessonManager.DATA_DIR and ExerciseManager.DATA_DIR to: {test_data_dir}")

    # The fixture yields nothing, its purpose is the setup/teardown
    yield test_data_dir # Optionally yield the test_data_dir if tests need it (e.g., for debugging)

    logger.debug("Test data setup complete.")

    # Teardown: The tmp_path fixture automatically cleans up the temporary directory.
    # The monkeypatch fixture automatically undoes the patches.
    # No explicit teardown needed here.
