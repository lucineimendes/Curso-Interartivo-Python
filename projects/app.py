# -*- coding: utf-8 -*-
import logging
from flask import Flask, jsonify, request, render_template, abort
from flask_cors import CORS
# Assume que estes módulos estão no mesmo diretório (projects/)
# Corrigido para import relativo consistente
from .course_manager import CourseManager
from .lesson_manager import LessonManager
from .exercise_manager import ExerciseManager
from . import code_executor

# Configuração básica de logging
# Idealmente, esta configuração pode ser mais elaborada e centralizada
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app) # Habilita CORS para todas as rotas

# Instancia os managers
# Os managers agora carregam dados sob demanda ou na inicialização, conforme suas implementações.
course_mgr = CourseManager()
lesson_mgr = LessonManager()
exercise_mgr = ExerciseManager()

# --- Rotas de Apresentação (HTML) ---

@app.route('/')
def home():
    logger.info("Rota raiz '/' acessada.")
    all_courses = course_mgr.get_courses()
    # Passa apenas os 3 primeiros cursos para a seção "Cursos em Destaque",
    # ou uma lista vazia se não houver cursos.
    courses_for_index = all_courses[:3] if all_courses else []
    return render_template('index.html', courses=courses_for_index, title="Bem-vindo")

@app.route('/courses', methods=['GET'])
def list_courses_page(): # Renomeado para clareza (página vs API)
    logger.info("GET /courses - Solicitando página de listagem de cursos.")
    courses = course_mgr.get_courses()
    return render_template('course_list.html', courses=courses, title="Cursos Disponíveis")

@app.route('/courses/<string:course_id>', methods=['GET'])
def course_detail_page(course_id): # Renomeado para clareza
    logger.info(f"GET /courses/{course_id} - Solicitando página de detalhes para o curso ID: {course_id}")
    course = course_mgr.get_course_by_id(course_id)
    if not course:
        logger.warning(f"GET /courses/{course_id} - Curso não encontrado.")
        abort(404) # Usa abort para tratamento de erro padrão do Flask

    # As lições são carregadas aqui para serem passadas ao template
    # O frontend não precisará fazer uma chamada API separada para as lições nesta página.
    lessons_file_relative_path = course.get("lessons_file")
    lessons_for_course = []
    if lessons_file_relative_path:
        lessons_for_course = lesson_mgr.load_lessons_from_file(lessons_file_relative_path)
    else:
        logger.warning(f"Curso '{course_id}' não possui 'lessons_file' definido.")

    return render_template('course_detail.html', course=course, lessons=lessons_for_course, title=course.get('name', 'Detalhes do Curso'))

@app.route('/courses/<string:course_id>/lessons/<string:lesson_id_str>', methods=['GET'])
def lesson_detail_page(course_id, lesson_id_str): # Renomeado para clareza
    logger.info(f"GET /courses/{course_id}/lessons/{lesson_id_str} - Solicitando página da lição.")
    current_course = course_mgr.get_course_by_id(course_id)
    if not current_course:
        logger.warning(f"Curso '{course_id}' não encontrado ao tentar obter lição '{lesson_id_str}'.")
        abort(404)

    lessons_file_relative_path = current_course.get("lessons_file")
    if not lessons_file_relative_path:
        logger.error(f"'lessons_file' não definido para o curso '{course_id}'.")
        abort(500, description="Configuração de lições ausente para este curso.")

    all_lessons_for_course = lesson_mgr.load_lessons_from_file(lessons_file_relative_path)
    
    current_lesson = None
    current_lesson_index = -1
    for i, lesson_item_loop in enumerate(all_lessons_for_course):
        if isinstance(lesson_item_loop, dict) and str(lesson_item_loop.get('id')) == lesson_id_str:
            current_lesson = lesson_item_loop
            current_lesson_index = i
            break

    if not current_lesson:
        logger.warning(f"Lição com ID '{lesson_id_str}' não encontrada no curso '{course_id}'.")
        abort(404)
    
    course_level_from_course_json = current_course.get('level')
    expected_exercise_level = course_level_from_course_json.lower() if course_level_from_course_json else None
        
    exercises_for_lesson = []
    exercises_file_relative_path = current_course.get("exercises_file")
    if exercises_file_relative_path:
        all_exercises_for_course = exercise_mgr.load_exercises_from_file(exercises_file_relative_path)
        lesson_actual_id = current_lesson.get('id') # ID da lição atual
        if lesson_actual_id and all_exercises_for_course:
            for ex_item in all_exercises_for_course:
                # Log para depuração
                logger.debug(f"Verificando exercício: ID='{ex_item.get('id')}', "
                             f"LessonID_Ex='{ex_item.get('lesson_id')}', LessonID_Atual='{lesson_actual_id}', "
                             f"Level_Ex='{ex_item.get('level', '').lower()}', Level_Esperado='{expected_exercise_level}'")
                
                # Verifica se o exercício pertence à lição atual E ao nível esperado do curso
                if isinstance(ex_item, dict) and \
                   str(ex_item.get('lesson_id')) == str(lesson_actual_id) and \
                   (not expected_exercise_level or ex_item.get('level', '').lower() == expected_exercise_level):
                    exercises_for_lesson.append(ex_item)
        logger.debug(f"Encontrados {len(exercises_for_lesson)} exercícios para a lição '{lesson_actual_id}'.")
    else:
        logger.warning(f"Nenhum 'exercises_file' definido para o curso '{course_id}'.")

    next_lesson_obj = None
    if current_lesson_index != -1 and current_lesson_index < len(all_lessons_for_course) - 1:
        next_lesson_obj = all_lessons_for_course[current_lesson_index + 1]

    return render_template('lesson_detail.html', # Assumindo que o template se chama lesson_detail.html
                           course=current_course,
                           lesson=current_lesson,
                           exercises=exercises_for_lesson,
                           next_lesson=next_lesson_obj,
                           title=current_lesson.get('title', 'Lição'))

@app.route('/courses/<string:course_id>/exercise/<string:exercise_id_str>/editor', methods=['GET'])
def exercise_code_editor_page(course_id, exercise_id_str): # Renomeado para clareza
    logger.info(f"GET /courses/{course_id}/exercise/{exercise_id_str}/editor - Acessando editor de código.")
    current_course = course_mgr.get_course_by_id(course_id)
    if not current_course:
        logger.warning(f"Editor: Curso '{course_id}' não encontrado.")
        abort(404)

    exercises_file_relative_path = current_course.get("exercises_file")
    if not exercises_file_relative_path:
        logger.error(f"Editor: 'exercises_file' não definido para o curso '{course_id}'.")
        abort(500, description="Configuração de exercícios ausente para este curso.")

    course_level_from_course_json = current_course.get('level')
    expected_exercise_level = course_level_from_course_json.lower() if course_level_from_course_json else None

    all_exercises_for_course = exercise_mgr.load_exercises_from_file(exercises_file_relative_path)
    current_exercise = None
    for ex_item in all_exercises_for_course:
        if isinstance(ex_item, dict) and str(ex_item.get('id')) == exercise_id_str:
            if not expected_exercise_level or ex_item.get('level', '').lower() == expected_exercise_level:
                current_exercise = ex_item
                break
            else:
                logger.warning(f"Editor: Exercício '{exercise_id_str}' encontrado, mas seu nível '{ex_item.get('level')}' não corresponde ao nível esperado do curso '{expected_exercise_level}'.")

    if not current_exercise:
        logger.warning(f"Editor: Exercício ID '{exercise_id_str}' não encontrado no curso '{course_id}' ou nível incompatível.")
        abort(404)

    return render_template('code_editor.html',
                           course=current_course,
                           exercise=current_exercise,
                           title=f"Editor: {current_exercise.get('title', 'Exercício')}")

@app.route('/editor', methods=['GET'])
def generic_code_editor_page():
    logger.info("GET /editor - Acessando editor de código genérico.")
    return render_template('code_editor.html', course=None, exercise=None, title="Editor de Código")

# --- Rotas de API (JSON) ---

@app.route('/api/courses/<string:course_id>/lessons', methods=['GET'])
def api_get_lessons_for_course(course_id):
    logger.info(f"API GET /courses/{course_id}/lessons - Solicitando lições para o curso ID: {course_id}")
    course = course_mgr.get_course_by_id(course_id)
    if not course:
        logger.warning(f"API GET /courses/{course_id}/lessons - Curso não encontrado.")
        return jsonify({"error": "Curso não encontrado"}), 404

    lessons_file_relative_path = course.get("lessons_file")
    if not lessons_file_relative_path:
        logger.error(f"API GET /courses/{course_id}/lessons - 'lessons_file' não definido para este curso.")
        return jsonify({"error": "Arquivo de lições não definido para este curso"}), 500

    lessons = lesson_mgr.load_lessons_from_file(lessons_file_relative_path)
    return jsonify(lessons)

@app.route('/api/courses/<string:course_id>/exercises', methods=['GET'])
def api_get_exercises_for_course(course_id):
    logger.info(f"API GET /courses/{course_id}/exercises - Solicitando exercícios para o curso ID: {course_id}")
    course = course_mgr.get_course_by_id(course_id)
    if not course:
        logger.warning(f"API GET /courses/{course_id}/exercises - Curso não encontrado.")
        return jsonify({"error": "Curso não encontrado"}), 404

    exercises_file_relative_path = course.get("exercises_file")
    if not exercises_file_relative_path:
        logger.error(f"API GET /courses/{course_id}/exercises - 'exercises_file' não definido para o curso.")
        return jsonify({"error": "Arquivo de exercícios não definido para este curso"}), 500

    exercises = exercise_mgr.load_exercises_from_file(exercises_file_relative_path)
    return jsonify(exercises)

@app.route('/api/execute-code', methods=['POST'])
def api_execute_code():
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
        if not success and not details and exec_result.get("error_type") == "SyntaxError":
            details = "Erro de sintaxe no código."
        elif not success and not details:
            details = "Erro durante a execução do código."

        logger.info(f"POST /api/execute-code - Execução: success={success}")
        return jsonify({"success": success, "output": output, "details": details})
    except Exception as e:
        logger.error(f"POST /api/execute-code - Erro inesperado: {e}", exc_info=True)
        return jsonify({"success": False, "output": "", "details": f"Erro interno do servidor: {str(e)}"}), 500

@app.route('/api/check-exercise', methods=['POST'])
def api_check_exercise():
    logger.info("POST /api/check-exercise - Recebida requisição para verificar exercício.")
    data = request.get_json()
    if not data or not all(k in data for k in ['course_id', 'exercise_id', 'code']):
        logger.warning("POST /api/check-exercise - Payload inválido ou campos ausentes.")
        return jsonify({"success": False, "output": "", "details": "Payload inválido. 'course_id', 'exercise_id', e 'code' são obrigatórios."}), 400

    course_id = data['course_id']
    exercise_id_str = str(data['exercise_id'])
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

    exercises = exercise_mgr.load_exercises_from_file(exercises_file_relative_path)
    exercise_details_to_check = None
    for ex_item in exercises:
        if isinstance(ex_item, dict) and str(ex_item.get('id')) == exercise_id_str:
            if not expected_exercise_level or ex_item.get('level', '').lower() == expected_exercise_level:
                exercise_details_to_check = ex_item
                break

    if not exercise_details_to_check:
        logger.warning(f"POST /api/check-exercise - Exercício '{exercise_id_str}' não encontrado no curso '{course_id}' ou nível incompatível.")
        return jsonify({"success": False, "output": "", "details": f"Exercício '{exercise_id_str}' não encontrado no curso '{course_id}'."}), 404

    test_code = exercise_details_to_check.get("test_code", "")
    full_code_to_execute = user_code.rstrip() + "\n\n" + test_code

    try:
        exec_result = code_executor.execute_code(full_code_to_execute)
        success = exec_result["returncode"] == 0
        output = exec_result["stdout"]
        details = exec_result["stderr"]
        
        if not success and not details and exec_result.get("error_type") == "SyntaxError":
            details = "Erro de sintaxe no código ou nos testes."
        elif not success and not details and exec_result.get("error_type") == "AssertionError":
            details = "Falha na asserção do teste." # Mensagem mais específica para AssertionError
        elif not success and not details:
            details = "Erro durante a execução do código de verificação."

        if not test_code and success:
            details = "Código executado com sucesso (nenhum teste automático para este exercício)."
        elif not test_code and not success:
            details = f"Erro ao executar o código: {details if details else 'Erro desconhecido'}"
        
        logger.info(f"POST /api/check-exercise - Verificação: success={success}")
        return jsonify({"success": success, "output": output, "details": details})
    except Exception as e:
        logger.error(f"POST /api/check-exercise - Erro inesperado: {e}", exc_info=True)
        return jsonify({"success": False, "output": "", "details": f"Erro interno do servidor ao verificar: {str(e)}"}), 500

# --- Rota Legada (Manter por compatibilidade ou remover se não for mais usada) ---
@app.route('/submit_exercise/<string:course_id>/<string:exercise_id_str>', methods=['POST'])
def submit_exercise_solution_legacy(course_id, exercise_id_str):
    logger.info(f"POST /submit_exercise/{course_id}/{exercise_id_str} (legacy) - Submetendo solução.")
    # Esta rota agora redireciona sua lógica para a nova API /api/check-exercise
    # para evitar duplicação de código.
    
    data_from_request = request.get_json()
    user_code = None
    if data_from_request and 'code' in data_from_request:
        user_code = data_from_request['code']
    elif request.form and 'code' in request.form: # Tenta pegar de formulário se não for JSON
        user_code = request.form['code']

    if user_code is None:
        logger.warning("POST /submit_exercise (legacy) - 'code' ausente no payload.")
        return jsonify({"success": False, "output": "", "details": "O campo 'code' é obrigatório."}), 400

    logger.warning(f"A rota LEGADA /submit_exercise/{course_id}/{exercise_id_str} foi chamada. "
                   f"Redirecionando internamente para a lógica de /api/check-exercise.")

    # Simula o payload para a nova API
    api_payload = {
        "course_id": course_id,
        "exercise_id": exercise_id_str,
        "code": user_code
    }
    
    # Chama a lógica da nova API internamente.
    # Isso requer que o contexto da aplicação Flask esteja disponível.
    # Uma forma mais limpa seria extrair a lógica de `api_check_exercise` para uma função helper.
    # Por simplicidade aqui, vamos assumir que podemos chamar a função diretamente se ela for refatorada.
    # Para este exemplo, vamos apenas logar e retornar um aviso,
    # pois chamar outra rota internamente pode ser complexo sem refatoração.
    
    # --- Início da lógica duplicada (idealmente refatorar para uma função helper) ---
    course = course_mgr.get_course_by_id(course_id)
    if not course:
        return jsonify({"success": False, "output": "", "details": f"Curso '{course_id}' não encontrado."}), 404

    exercises_file_relative_path = course.get("exercises_file")
    if not exercises_file_relative_path:
        return jsonify({"success": False, "output": "", "details": "Arquivo de exercícios não definido para este curso."}), 500
    
    course_level_from_course_json = course.get('level')
    expected_exercise_level = course_level_from_course_json.lower() if course_level_from_course_json else None

    exercises = exercise_mgr.load_exercises_from_file(exercises_file_relative_path)
    exercise_details_to_check = None
    for ex_item in exercises:
        if isinstance(ex_item, dict) and str(ex_item.get('id')) == exercise_id_str:
            if not expected_exercise_level or ex_item.get('level', '').lower() == expected_exercise_level:
                exercise_details_to_check = ex_item
                break
    
    if not exercise_details_to_check:
        return jsonify({"success": False, "output": "", "details": f"Exercício '{exercise_id_str}' não encontrado."}), 404

    test_code = exercise_details_to_check.get("test_code", "")
    full_code_to_execute = user_code.rstrip() + "\n\n" + test_code
    try:
        exec_result = code_executor.execute_code(full_code_to_execute)
        success = exec_result["returncode"] == 0
        output = exec_result["stdout"]
        details = exec_result["stderr"]
        if not success and not details and exec_result.get("error_type") == "SyntaxError":
            details = "Erro de sintaxe no código ou nos testes."
        elif not success and not details and exec_result.get("error_type") == "AssertionError":
            details = "Falha na asserção do teste."
        elif not success and not details:
            details = "Erro durante a execução do código de verificação."
        
        if not test_code and success:
            details = "Código executado com sucesso (nenhum teste automático)."
        elif not test_code and not success:
            details = f"Erro ao executar o código: {details if details else 'Erro desconhecido'}"

        return jsonify({"success": success, "output": output, "details": details})
    except Exception as e:
        logger.error(f"POST /submit_exercise (legacy) - Erro inesperado: {e}", exc_info=True)
        return jsonify({"success": False, "output": "", "details": f"Erro interno: {str(e)}"}), 500
    # --- Fim da lógica duplicada ---

# --- Tratador de Erros Padrão ---
@app.errorhandler(404)
def page_not_found(e):
    logger.warning(f"Erro 404 - Página não encontrada: {request.path} (Descrição: {e.description})")
    # Verifica se a requisição espera JSON ou HTML
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        return jsonify(error=str(e.description or "Recurso não encontrado")), 404
    return render_template('404.html', title="Página Não Encontrada", error_message=e.description), 404

@app.errorhandler(500)
def internal_server_error(e):
    logger.error(f"Erro 500 - Erro interno do servidor: {request.path} (Descrição: {e.description or str(e.original_exception or e)})", exc_info=True)
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        return jsonify(error=str(e.description or "Erro interno do servidor")), 500
    return render_template('500.html', title="Erro Interno", error_message=e.description or "Ocorreu um erro inesperado."), 500


if __name__ == '__main__':
    # Para desenvolvimento, debug=True é útil. Para produção, defina como False.
    # host='0.0.0.0' torna o servidor acessível externamente na rede.
    # A porta pode ser alterada se necessário.
    logger.info("Iniciando servidor Flask para desenvolvimento...")
    app.run(host='0.0.0.0', port=5000, debug=True)
