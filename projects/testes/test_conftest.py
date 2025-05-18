import pytest
import json
from pathlib import Path
from flask import Flask
from flask.testing import FlaskClient

# Imports from your project structure, assuming conftest.py correctly sets up sys.path
from projects.app import course_mgr as app_course_manager_instance # The global instance from app.py, aliased
from projects import lesson_manager, exercise_manager

# Test data defined in conftest.py, re-declared here for assertion
# In a larger setup, this might be imported from a shared module
EXPECTED_TEST_COURSES_DATA = [
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

EXPECTED_TEST_BASIC_LESSONS_DATA = [
    {
        "id": "introducao-python",
        "title": "Introdução ao Python",
        "description": "Primeiros passos.",
        "order": 1,
        "content": "<p>Conteúdo da introdução.</p>",
        "course_id": "python-basico"
    }
]

EXPECTED_TEST_BASIC_EXERCISES_DATA = [
    {
        "id": "ex-introducao-5",
        "lesson_id": "introducao-python",
        "title": "Teste de API",
        "description": "Teste da API de verificação.",
        "difficulty": "Fácil",
        "order": 5,
        "instructions": "Imprima 'Olá, Python!'",
        "initial_code": "print('Olá, Mundo!')",
        "solution_code": "print('Olá, Python!')",
        "test_code": "assert 'Olá, Python!' in output\nprint('SUCCESS')",
        "level": "básico"
    },
    {
        "id": "ex-introducao-1",
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


def test_app_fixture(app):
    """Tests the 'app' fixture."""
    assert isinstance(app, Flask), "Fixture 'app' should provide a Flask instance."
    assert app.config['TESTING'] is True, "Flask app should be in TESTING mode."

def test_client_fixture(client):
    """Tests the 'client' fixture."""
    assert isinstance(client, FlaskClient), "Fixture 'client' should provide a FlaskClient instance."

def test_app_test_data_fixture_creates_files(app_test_data):
    """
    Tests that the 'app_test_data' fixture creates the expected temporary
    directory structure and files.
    'app_test_data' fixture provides the root of the temporary data directory.
    """
    test_data_root_dir = app_test_data # This is tmp_path / 'data' from conftest

    assert test_data_root_dir.is_dir()
    assert (test_data_root_dir / 'courses.json').is_file()
    assert (test_data_root_dir / 'basic' / 'lessons.json').is_file()
    assert (test_data_root_dir / 'basic' / 'exercises.json').is_file()
    assert (test_data_root_dir / 'intermediate').is_dir()
    assert (test_data_root_dir / 'advanced').is_dir()

def test_app_test_data_fixture_courses_content(app_test_data):
    """Tests the content of the temporary courses.json."""
    courses_file = app_test_data / 'courses.json'
    with open(courses_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    assert data == EXPECTED_TEST_COURSES_DATA, "Content of temporary courses.json does not match expected."

def test_app_test_data_fixture_basic_lessons_content(app_test_data):
    """Tests the content of the temporary basic/lessons.json."""
    lessons_file = app_test_data / 'basic' / 'lessons.json'
    with open(lessons_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    assert data == EXPECTED_TEST_BASIC_LESSONS_DATA, "Content of temporary basic/lessons.json does not match expected."

def test_app_test_data_fixture_basic_exercises_content(app_test_data):
    """Tests the content of the temporary basic/exercises.json."""
    exercises_file = app_test_data / 'basic' / 'exercises.json'
    with open(exercises_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    assert data == EXPECTED_TEST_BASIC_EXERCISES_DATA, "Content of temporary basic/exercises.json does not match expected."

def test_app_test_data_fixture_course_manager_patching(app_test_data):
    """
    Tests that the CourseManager instance is correctly patched
    by the 'app_test_data' fixture.
    """
    test_data_root_dir = app_test_data

    # app_course_manager_instance is the global instance from projects.app
    assert app_course_manager_instance.data_dir == test_data_root_dir, \
        "CourseManager.data_dir was not patched correctly."

    assert len(app_course_manager_instance.courses) == len(EXPECTED_TEST_COURSES_DATA), \
        "CourseManager did not reload courses from the temporary file or count mismatch."

    loaded_course_ids = sorted([course['id'] for course in app_course_manager_instance.courses])
    expected_course_ids = sorted([course['id'] for course in EXPECTED_TEST_COURSES_DATA])
    assert loaded_course_ids == expected_course_ids, \
        "Course IDs in reloaded CourseManager do not match expected."

def test_app_test_data_fixture_lesson_exercise_manager_patching(app_test_data):
    """
    Tests that the DATA_DIR globals in LessonManager and ExerciseManager
    are correctly patched by the 'app_test_data' fixture.
    """
    test_data_root_dir = app_test_data

    assert lesson_manager.DATA_DIR == test_data_root_dir, \
        "lesson_manager.DATA_DIR was not patched correctly."
    assert exercise_manager.DATA_DIR == test_data_root_dir, \
        "exercise_manager.DATA_DIR was not patched correctly."