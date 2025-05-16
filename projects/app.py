# -*- coding: utf-8 -*-
import logging
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
# Assume que estes módulos estão no mesmo diretório (projects/)
from projects.course_manager import CourseManager
from .lesson_manager import LessonManager
from .exercise_manager import ExerciseManager
from . import code_executor # Usando import relativo para code_executor também

# Configuração básica de logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Instancia os managers
course_mgr = CourseManager() # Alterado
lesson_mgr = LessonManager()
exercise_mgr = ExerciseManager()

@app.route('/')
def home():
    logger.info("Rota raiz '/' acessada, renderizando index.html.")
    all_courses = course_mgr.get_courses()
    # Pass only the first 3 courses for the "Cursos em Destaque" section,
    # or an empty list if no courses exist.
    courses_for_index = all_courses[:3] if all_courses else []
    return render_template('index.html', courses=courses_for_index)

@app.route('/courses', methods=['GET'])
def get_courses_list():
    logger.info("GET /courses - Solicitando lista de cursos.")
    courses_data = course_mgr.get_courses()
    # Assuming you have a template, e.g., 'courses.html', to display all courses
    # Create this template if it doesn't exist.
    return render_template('courses.html', courses=courses_data if courses_data else [])


@app.route('/courses/<course_id>', methods=['GET'])
def get_course_details(course_id):
    logger.info(f"GET /courses/{course_id} - Solicitando detalhes para o curso ID: {course_id}")
    course = course_mgr.get_course_by_id(course_id)
    if course: # Renderiza um template HTML para os detalhes do curso
        # O template course_details.html pode usar JavaScript (ex: Alpine.js ou fetch)
        # para buscar as lições dinamicamente do endpoint /courses/<course_id>/lessons
        return render_template('course_details.html', course=course, course_id=course_id)
        # Se fosse apenas API: return jsonify(course)
    logger.warning(f"GET /courses/{course_id} - Curso não encontrado.")    
    return render_template('error.html', error_message="Curso não encontrado"), 404
    # Se fosse apenas API: return jsonify({"error": "Curso não encontrado"}), 404

@app.route('/courses/<course_id>/lessons', methods=['GET'])
def get_lessons_for_course(course_id):
    logger.info(f"GET /courses/{course_id}/lessons - Solicitando lições para o curso ID: {course_id}")
    course = course_mgr.get_course_by_id(course_id)
    if not course:
        logger.warning(f"GET /courses/{course_id}/lessons - Curso não encontrado.")
        return jsonify({"error": "Curso não encontrado"}), 404

    lessons_file_relative_path = course.get("lessons_file")
    if not lessons_file_relative_path:
        logger.error(f"GET /courses/{course_id}/lessons - 'lessons_file' não definido para este curso.")
        return jsonify({"error": "Arquivo de lições não definido para este curso"}), 500

    lessons = lesson_mgr.load_lessons_from_file(lessons_file_relative_path)
    return jsonify(lessons)


@app.route('/courses/<course_id>/lessons/<lesson_id_str>', methods=['GET'])
def get_specific_lesson(course_id, lesson_id_str):
    logger.info(f"GET /courses/{course_id}/lessons/{lesson_id_str} - Solicitando lição específica.")
    current_course = course_mgr.get_course_by_id(course_id)
    if not current_course:
        logger.warning(f"Curso {course_id} não encontrado ao tentar obter lição {lesson_id_str}.")
        return render_template('error.html', error_message="Curso não encontrado"), 404

    lessons_file_relative_path = current_course.get("lessons_file")
    if not lessons_file_relative_path:
        logger.error(f"'lessons_file' não definido para o curso {course_id}.")
        return render_template('error.html', error_message="Arquivo de lições não definido para este curso"), 500

    all_lessons_for_course = lesson_mgr.load_lessons_from_file(lessons_file_relative_path)
    if not all_lessons_for_course: # Pode ser lista vazia, o que é válido. Checar se é None ou se o carregamento falhou.
                                  # lesson_mgr.load_lessons_from_file já retorna [] em caso de erro.
        logger.warning(f"Nenhuma lição encontrada no arquivo {lessons_file_relative_path} para o curso {course_id} ou arquivo vazio.")
        # Não necessariamente um erro 404 se o arquivo existe mas está vazio.
        # A lógica abaixo lidará com current_lesson não sendo encontrado.

    current_lesson = None
    current_lesson_index = -1
    for i, lesson_item_loop in enumerate(all_lessons_for_course):
        if isinstance(lesson_item_loop, dict) and str(lesson_item_loop.get('id')) == lesson_id_str:
            current_lesson = lesson_item_loop
            current_lesson_index = i
            break

    if not current_lesson:
        logger.warning(f"Lição com ID '{lesson_id_str}' não encontrada no curso '{course_id}'.")
        return render_template('error.html', error_message="Lição não encontrada"), 404
    
    # Determina o nível esperado dos exercícios com base no nível do curso atual
    # Assegura que current_course.get('level') exista e o converte para minúsculas para comparação.
    # Se current_course.get('level') for None, expected_exercise_level será None,
    # e a comparação ex_item.get('level') == expected_exercise_level falhará corretamente se ex_item.get('level') não for None.
    course_level_from_course_json = current_course.get('level')
    expected_exercise_level = course_level_from_course_json.lower() if course_level_from_course_json else None
    if not expected_exercise_level:
        logger.warning(f"Nível do curso (level) não definido para o curso ID '{course_id}'. Não será possível filtrar exercícios por nível.")
        # Decide-se prosseguir sem filtro de nível ou retornar erro. Aqui, prosseguimos, mas o log alerta.
        
    exercises_for_lesson = []
    exercises_file_relative_path = current_course.get("exercises_file")
    if exercises_file_relative_path:
        all_exercises_for_course = exercise_mgr.load_exercises_from_file(exercises_file_relative_path)
        lesson_actual_id = current_lesson.get('id')
        if lesson_actual_id and all_exercises_for_course: # all_exercises_for_course pode ser []
            for ex_item in all_exercises_for_course: # Garante que ex_item é um dicionário
                if isinstance(ex_item, dict) and str(ex_item.get('lesson_id')) == str(lesson_actual_id) and (not expected_exercise_level or ex_item.get('level') == expected_exercise_level):
                    exercises_for_lesson.append(ex_item)
        logger.debug(f"Encontrados {len(exercises_for_lesson)} exercícios para a lição '{lesson_actual_id}'.")
    else:
        logger.warning(f"Nenhum 'exercises_file' definido para o curso {course_id}, não foi possível carregar exercícios.")

    next_lesson_obj = None
    if current_lesson_index != -1 and current_lesson_index < len(all_lessons_for_course) - 1:
        next_lesson_obj = all_lessons_for_course[current_lesson_index + 1]
    logger.debug(f"Próxima lição: {next_lesson_obj.get('id') if next_lesson_obj else 'Nenhuma'}")

    logger.info(f"Renderizando template 'lesson.html' para lição '{current_lesson.get('title')}' do curso '{current_course.get('name')}'.")
    return render_template('lesson.html',
                           course=current_course,
                           lesson=current_lesson,
                           exercises=exercises_for_lesson,
                           next_lesson=next_lesson_obj)


@app.route('/courses/<course_id>/exercises', methods=['GET'])
def get_exercises_for_course(course_id):
    logger.info(f"GET /courses/{course_id}/exercises - Solicitando exercícios para o curso ID: {course_id}")
    course = course_mgr.get_course_by_id(course_id)
    if not course:
        logger.warning(f"GET /courses/{course_id}/exercises - Curso não encontrado.")
        return jsonify({"error": "Curso não encontrado"}), 404

    exercises_file_relative_path = course.get("exercises_file")
    if not exercises_file_relative_path:
        logger.error(f"GET /courses/{course_id}/exercises - 'exercises_file' não definido para o curso.")
        return jsonify({"error": "Arquivo de exercícios não definido para este curso"}), 500

    exercises = exercise_mgr.load_exercises_from_file(exercises_file_relative_path)
    return jsonify(exercises)


@app.route('/courses/<course_id>/exercises/<exercise_id_str>', methods=['GET'])
def get_specific_exercise_details(course_id, exercise_id_str):
    logger.info(f"GET /courses/{course_id}/exercises/{exercise_id_str} - Solicitando exercício específico.")
    course = course_mgr.get_course_by_id(course_id)
    if not course:
        logger.warning(f"GET /courses/{course_id}/exercises/{exercise_id_str} - Curso não encontrado.")
        return jsonify({"error": "Curso não encontrado"}), 404

    exercises_file_relative_path = course.get("exercises_file")
    if not exercises_file_relative_path:
        logger.error(f"GET /courses/{course_id}/exercises/{exercise_id_str} - 'exercises_file' não definido.")
        return jsonify({"error": "Arquivo de exercícios não definido para este curso"}), 500

    course_level_from_course_json = course.get('level')
    expected_exercise_level = course_level_from_course_json.lower() if course_level_from_course_json else None
    if not expected_exercise_level:
        logger.warning(f"Nível do curso (level) não definido para o curso ID '{course_id}' ao buscar exercício específico. Não será possível validar o nível do exercício.")

    exercises = exercise_mgr.load_exercises_from_file(exercises_file_relative_path)
    # exercises pode ser [] se o arquivo estiver vazio ou não for encontrado/erro de parse.

    for exercise_item in exercises: # Se exercises for [], o loop não executa.
        if isinstance(exercise_item, dict) and str(exercise_item.get('id')) == exercise_id_str:
            if not expected_exercise_level or exercise_item.get('level') == expected_exercise_level:
                logger.info(f"Exercício {exercise_id_str} (nível: {exercise_item.get('level')}) encontrado para o curso {course_id} (nível esperado: {expected_exercise_level}).")
                return jsonify(exercise_item)
            else:
                logger.warning(f"Exercício {exercise_id_str} encontrado, mas seu nível '{exercise_item.get('level')}' não corresponde ao nível esperado do curso '{expected_exercise_level}'.")
                # Continua procurando caso haja outro exercício com mesmo ID mas nível correto (improvável, mas seguro)

    logger.warning(f"GET /courses/{course_id}/exercises/{exercise_id_str} - ID do exercício não encontrado ou arquivo de exercícios vazio/com problemas.")
    return jsonify({"error": "Exercício não encontrado"}), 404


@app.route('/courses/<course_id>/exercise/<exercise_id_str>/editor', methods=['GET'])
def exercise_code_editor(course_id, exercise_id_str):
    logger.info(f"GET /courses/{course_id}/exercise/{exercise_id_str}/editor - Acessando editor de código.")
    current_course = course_mgr.get_course_by_id(course_id)
    if not current_course:
        logger.warning(f"Editor: Curso {course_id} não encontrado.")
        return render_template('error.html', error_message="Curso não encontrado"), 404

    exercises_file_relative_path = current_course.get("exercises_file")
    if not exercises_file_relative_path:
        logger.error(f"Editor: 'exercises_file' não definido para o curso {course_id}.")
        return render_template('error.html', error_message="Arquivo de exercícios não definido para este curso"), 500

    course_level_from_course_json = current_course.get('level')
    expected_exercise_level = course_level_from_course_json.lower() if course_level_from_course_json else None
    if not expected_exercise_level:
        logger.warning(f"Editor: Nível do curso (level) não definido para o curso ID '{course_id}'. Não será possível validar o nível do exercício.")

    all_exercises_for_course = exercise_mgr.load_exercises_from_file(exercises_file_relative_path)
    current_exercise = None
    for ex_item in all_exercises_for_course: # Se all_exercises_for_course for [], o loop não executa.
        if isinstance(ex_item, dict) and str(ex_item.get('id')) == exercise_id_str:
            if not expected_exercise_level or ex_item.get('level') == expected_exercise_level:
                current_exercise = ex_item
                break
            else:
                logger.warning(f"Editor: Exercício {exercise_id_str} encontrado, mas seu nível '{ex_item.get('level')}' não corresponde ao nível esperado do curso '{expected_exercise_level}'.")

    if not current_exercise:
        logger.warning(f"Editor: Exercício ID '{exercise_id_str}' não encontrado no curso '{course_id}' ou nível incompatível.")
        return render_template('error.html', error_message="Exercício não encontrado"), 404

    logger.info(f"Renderizando 'code_editor.html' para o exercício '{current_exercise.get('title')}'.")
    return render_template('code_editor.html',
                           course=current_course,
                           exercise=current_exercise)

# --- NOVAS ROTAS PARA A API DO EDITOR DE CÓDIGO ---
@app.route('/editor', methods=['GET'])
def code_editor():
    """Renderiza a página do editor de código genérico."""
    logger.info("GET /editor - Acessando editor de código genérico.")
    # Renderiza o template code_editor.html sem passar dados de curso/exercício
    # O template deve ser capaz de lidar com 'course' e 'exercise' sendo None
    return render_template('code_editor.html', course=None, exercise=None)


@app.route('/api/execute-code', methods=['POST'])
def api_execute_code():
    """
    Endpoint para execução genérica de código Python.
    Recebe: JSON {"code": "seu código python"}
    Retorna: JSON {"success": bool, "output": "saída do código", "details": "detalhes/erro"}
    """
    logger.info("POST /api/execute-code - Recebida requisição para executar código.")
    data = request.get_json()
    if not data or 'code' not in data:
        logger.warning("POST /api/execute-code - Payload inválido ou 'code' ausente.")
        return jsonify({"success": False, "output": "", "details": "Payload inválido ou campo 'code' ausente."}), 400

    user_code = data['code']

    try:
        exec_result = code_executor.execute_code(user_code)
        success = exec_result["returncode"] == 0
        output = exec_result["stdout"]
        details = exec_result["stderr"]
        if not success and not details: # Caso de erro de sintaxe pego pelo exec, stderr pode estar vazio
            details = "Erro durante a execução do código (verifique a sintaxe)."

        logger.info(f"POST /api/execute-code - Execução: success={success}, output='{output[:100].replace('\n', ' ')}...', details='{details[:100].replace('\n', ' ')}...'")
        return jsonify({"success": success, "output": output, "details": details})
    except Exception as e:
        logger.error(f"POST /api/execute-code - Erro inesperado durante a execução: {e}", exc_info=True)
        return jsonify({"success": False, "output": "", "details": f"Erro interno do servidor: {str(e)}"}), 500


@app.route('/api/check-exercise', methods=['POST'])
def api_check_exercise():
    """
    Endpoint para verificar a solução de um exercício.
    Recebe: JSON {"course_id": "...", "exercise_id": "...", "code": "..."}
    Retorna: JSON {"success": bool, "output": "...", "details": "..."}
    """
    logger.info("POST /api/check-exercise - Recebida requisição para verificar exercício.")
    data = request.get_json()
    if not data or not all(k in data for k in ['course_id', 'exercise_id', 'code']):
        logger.warning("POST /api/check-exercise - Payload inválido ou campos ausentes.")
        return jsonify({"success": False, "output": "", "details": "Payload inválido. 'course_id', 'exercise_id', e 'code' são obrigatórios."}), 400

    course_id = data['course_id']
    exercise_id_str = str(data['exercise_id']) # Garante que seja string para comparação
    user_code = data['code']

    course = course_mgr.get_course_by_id(course_id)
    if not course:
        logger.warning(f"POST /api/check-exercise - Curso '{course_id}' não encontrado.")
        return jsonify({"success": False, "output": "", "details": f"Curso '{course_id}' não encontrado."}), 404

    exercises_file_relative_path = course.get("exercises_file")
    if not exercises_file_relative_path:
        logger.error(f"POST /api/check-exercise - 'exercises_file' não definido para o curso '{course_id}'.")
        return jsonify({"success": False, "output": "", "details": "Arquivo de exercícios não definido para este curso."}), 500

    course_level_from_course_json = course.get('level')
    expected_exercise_level = course_level_from_course_json.lower() if course_level_from_course_json else None
    if not expected_exercise_level:
        logger.warning(f"API Check: Nível do curso (level) não definido para o curso ID '{course_id}'. Não será possível validar o nível do exercício.")

    exercises = exercise_mgr.load_exercises_from_file(exercises_file_relative_path)
    exercise_details_to_check = None
    for ex_item in exercises: # Se exercises for [], o loop não executa.
        if isinstance(ex_item, dict) and str(ex_item.get('id')) == exercise_id_str:
            if not expected_exercise_level or ex_item.get('level') == expected_exercise_level:
                exercise_details_to_check = ex_item
                break
            # Não retorna erro aqui, pois pode haver outro exercício com mesmo ID e nível correto (improvável)

    if not exercise_details_to_check:
        logger.warning(f"POST /api/check-exercise - Exercício '{exercise_id_str}' não encontrado no curso '{course_id}'.")
        return jsonify({"success": False, "output": "", "details": f"Exercício '{exercise_id_str}' não encontrado no curso '{course_id}'."}), 404

    test_code = exercise_details_to_check.get("test_code", "")
    # Se não houver test_code, a verificação de sucesso dependerá apenas da execução do código do usuário.
    # O `code_executor.execute_code` já trata `AssertionError` como qualquer outra exceção,
    # então `success` será `False` se um `AssertionError` ocorrer no `test_code`.

    full_code_to_execute = user_code.rstrip() + "\n\n" + test_code

    try:
        exec_result = code_executor.execute_code(full_code_to_execute)
        success = exec_result["returncode"] == 0
        output = exec_result["stdout"]
        details = exec_result["stderr"]
        if not success and not details:
            details = "Erro durante a execução do código de verificação (verifique a sintaxe ou asserções)."

        # Se não há test_code, o "sucesso" é apenas se o código do usuário rodou sem erros.
        # Se há test_code, o "sucesso" implica que o código do usuário + test_code rodaram sem erros (incluindo asserções).
        if not test_code and success:
            details = "Código executado com sucesso (nenhum teste automático para este exercício)."
        elif not test_code and not success:
            details = f"Erro ao executar o código: {details}"


        logger.info(f"POST /api/check-exercise - Verificação: success={success}, output='{output[:100].replace('\n', ' ')}...', details='{details[:100].replace('\n', ' ')}...'")
        return jsonify({"success": success, "output": output, "details": details})
    except Exception as e:
        logger.error(f"POST /api/check-exercise - Erro inesperado durante a verificação: {e}", exc_info=True)
        return jsonify({"success": False, "output": "", "details": f"Erro interno do servidor ao verificar: {str(e)}"}), 500


# Rota original de submissão, pode ser mantida ou removida se /api/check-exercise a substitui completamente.
@app.route('/submit_exercise/<course_id>/<exercise_id_str>', methods=['POST'])
def submit_exercise_solution_legacy(course_id, exercise_id_str):
    logger.info(f"POST /submit_exercise/{course_id}/{exercise_id_str} (legacy) - Submetendo solução.")
    data = request.get_json() # Espera JSON
    if not data: # Se o corpo não for JSON ou estiver vazio
        # Tenta pegar de request.form se for um POST de formulário tradicional
        user_code_form = request.form.get('code')
        if not user_code_form:
            logger.warning("POST /submit_exercise (legacy) - Nenhum dado JSON ou 'code' no formulário recebido.")
            # A resposta aqui depende do que o cliente desta rota espera.
            # Se for para renderizar um template:
            # return render_template('error.html', message="Requisição inválida ou código ausente."), 400
            # Se for para API:
            return jsonify({"success": False, "output": "", "details": "Requisição inválida ou campo 'code' ausente."}), 400
        user_code = user_code_form
    else:
        user_code = data.get('code')

    if user_code is None: # Checa None explicitamente, pois string vazia pode ser válida
        logger.warning("POST /submit_exercise (legacy) - Campo 'code' ausente no payload.")
        return jsonify({"success": False, "output": "", "details": "O campo 'code' é obrigatório."}), 400

    logger.warning(f"A rota /submit_exercise/{course_id}/{exercise_id_str} foi chamada. "
                   f"Considere migrar para /api/check-exercise se for uma chamada de API.")

    course = course_mgr.get_course_by_id(course_id)
    if not course:
        return jsonify({"success": False, "output": "", "details": "Curso não encontrado"}), 404

    exercises_file = course.get("exercises_file")
    if not exercises_file:
        return jsonify({"success": False, "output": "", "details": "Arquivo de exercícios não definido"}), 500

    course_level_from_course_json = course.get('level')
    expected_exercise_level = course_level_from_course_json.lower() if course_level_from_course_json else None

    exercises = exercise_mgr.load_exercises_from_file(exercises_file)
    exercise_details = None
    for ex in exercises:
        if isinstance(ex, dict) and str(ex.get('id')) == exercise_id_str:
            if not expected_exercise_level or ex.get('level') == expected_exercise_level:
                exercise_details = ex
                break

    if not exercise_details:
        logger.warning(f"Submit Legacy: Exercício '{exercise_id_str}' não encontrado no curso '{course_id}' ou nível incompatível.")
        return jsonify({"success": False, "output": "", "details": "Exercício não encontrado"}), 404

    test_code = exercise_details.get("test_code", "")
    full_code = user_code.rstrip() + "\n\n" + test_code

    exec_result = code_executor.execute_code(full_code)
    success = exec_result["returncode"] == 0
    output = exec_result["stdout"]
    details = exec_result["stderr"]
    if not success and not details:
        details = "Erro durante a execução do código de verificação (verifique a sintaxe ou asserções)."

    # Se esta rota renderiza um template, a resposta JSON abaixo pode precisar ser adaptada.
    # Por exemplo, poderia renderizar 'code_editor.html' com os resultados.
    # return render_template('code_editor.html', course=course, exercise=exercise_details,
    #                        submission_result={"success": success, "output": output, "details": details},
    #                        user_code=user_code)

    return jsonify({
        "success": success,
        "output": output,
        "details": details
    })


    # Para desenvolvimento, debug=True é útil. Para produção, defina como False.
    # host='0.0.0.0' torna o servidor acessível externamente na rede.
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
