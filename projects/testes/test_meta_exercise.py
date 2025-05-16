import pytest
import json
import io
import contextlib
import sys
import traceback
import builtins # Para mockar input
import os # Para construção robusta de caminhos
import logging

logger = logging.getLogger(__name__)

# Caminho para o diretório de dados e o arquivo principal de cursos
PROJECT_ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # Vai para 'projects'
DATA_DIR = os.path.join(PROJECT_ROOT_DIR, 'data')
COURSES_FILE_PATH = os.path.join(DATA_DIR, 'courses.json')

# Teste simples para verificar se o Pytest está funcionando e logando
def test_pytest_is_working():
    logger.info("Este é um log do test_pytest_is_working.")
    assert True


# Variáveis globais para mock de input (similar ao seu script original)
_original_input = builtins.input
_mock_input_values = []
_mock_input_index = 0

def mock_input_function(prompt=""):
    global _mock_input_index, _mock_input_values
    if _mock_input_index < len(_mock_input_values):
        value = _mock_input_values[_mock_input_index]
        _mock_input_index += 1
        return value
    return _original_input(prompt)

def execute_code(code_string, execution_globals=None, input_prompts_and_values=None):
    global _mock_input_values, _mock_input_index, _original_input
    
    if execution_globals is None:
        execution_globals = {}
    execution_globals['__name__'] = 'solution_module' # Tenta fornecer um __name__ mais razoável para Flask

    # Tenta importar módulos comuns e adicioná-los ao escopo de execução
    # para que os solution_code que os utilizam possam encontrá-los.
    common_imports = {
        "numpy": "np",
        "pandas": "pd",
        "matplotlib.pyplot": "plt",
        "flask": "Flask", # Apenas o objeto Flask, não a instância app
        "sqlalchemy": "sqlalchemy", # O módulo em si
        "django.db.models": "models", # Exemplo para models do Django
        "sklearn.linear_model": "LinearRegression", # Exemplo
        "sklearn.tree": "DecisionTreeClassifier" # Exemplo
    }

    for module_name, alias in common_imports.items():
        try:
            module = __import__(module_name, fromlist=[alias if '.' not in module_name else module_name.split('.')[-1]])
            if alias == module_name.split('.')[-1] or alias == module_name: # Se o alias é o nome do módulo ou submodulo
                execution_globals[alias] = module
            else: # Se é um alias customizado como 'np' para 'numpy'
                execution_globals[alias] = module
        except ImportError:
            logger.debug(f"Módulo {module_name} não encontrado para adicionar ao escopo de exec().")

    if 'ast' not in execution_globals:
        import ast
        execution_globals['ast'] = ast

    if input_prompts_and_values:
        _mock_input_values = [val for _, val in input_prompts_and_values]
        _mock_input_index = 0
        builtins.input = mock_input_function
    else:
        builtins.input = _original_input

    stdout_capture = io.StringIO()
    exception_info = None
    
    try:
        with contextlib.redirect_stdout(stdout_capture):
            exec(code_string, execution_globals)
    except Exception:
        exception_info = traceback.format_exc()
    finally:
        builtins.input = _original_input
        _mock_input_values = []
        _mock_input_index = 0

    return stdout_capture.getvalue(), exception_info

def load_json_file(file_path, error_message_prefix=""):
    if not os.path.exists(file_path):
        print(f"AVISO: {error_message_prefix}Arquivo não encontrado em {file_path}.")
        return []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        pytest.fail(f"{error_message_prefix}Falha ao decodificar o JSON do arquivo {file_path}")
    return []

# Gera os parâmetros para o teste, usando o ID do exercício para melhor feedback no pytest
def generate_exercise_test_cases():
    all_exercises = []
    courses = load_json_file(COURSES_FILE_PATH, "Arquivo principal de cursos: ")

    if not courses:
        print(f"AVISO: Nenhum curso encontrado em {COURSES_FILE_PATH} ou arquivo vazio. Nenhum meta-teste de exercício será executado.")
        return [pytest.param({}, id="no_courses_found", marks=pytest.mark.skip(reason="Nenhum curso encontrado."))]

    for course_data in courses:
        course_id = course_data.get("id")
        course_name = course_data.get("name", "Curso Desconhecido")
        exercises_file_relative = course_data.get("exercises_file")

        if not course_id or not exercises_file_relative:
            print(f"AVISO: Curso '{course_name}' (ID: {course_id}) não possui 'id' ou 'exercises_file' definido em {COURSES_FILE_PATH}. Pulando.")
            continue

        # exercises_file_relative é algo como "nome_do_curso/exercises.json"
        # Precisamos construir o caminho absoluto a partir de DATA_DIR
        specific_exercises_file_path = os.path.join(DATA_DIR, exercises_file_relative)
        
        course_exercises = load_json_file(specific_exercises_file_path, f"Arquivo de exercícios para o curso '{course_name}': ")
        
        for ex_data in course_exercises:
            # Adiciona informações do curso ao exercício para melhor identificação no teste
            ex_data["_course_id"] = course_id 
            ex_data["_course_name"] = course_name
            all_exercises.append(ex_data)

    if not all_exercises:
        # Retorna um caso de teste "dummy" que será pulado, para evitar erro de parametrização vazia.
        return [pytest.param({}, id="no_exercises_found_or_file_empty", marks=pytest.mark.skip(reason="Nenhum exercício encontrado ou arquivo de exercícios vazio."))]

    test_cases = []
    for ex_idx, ex_data in enumerate(all_exercises):
        # Usa o ID do exercício se disponível, senão um ID gerado.
        exercise_id = ex_data.get("id", f"exercise_index_{ex_idx}")
        course_id_for_test_name = ex_data.get("_course_id", "unknown_course")
        exercise_id_for_test_name = f"{course_id_for_test_name}_{exercise_id}"
        test_cases.append(pytest.param(ex_data, id=exercise_id_for_test_name))
    return test_cases

@pytest.mark.parametrize("exercise_data", generate_exercise_test_cases())
def test_single_exercise_logic(exercise_data):
    # Se for o caso dummy de "no_exercises_found", exercise_data estará vazio.
    if not exercise_data.get("id"): # Checa se temos um exercício real
         pytest.skip("Dados do exercício vazios ou caso dummy, pulando.")

    exercise_id = exercise_data.get("id", "ID Desconhecido")
    course_id = exercise_data.get("_course_id", "Curso Desconhecido")
    test_identifier = f"Curso '{course_id}', Exercício '{exercise_id}'"

    solution_code = exercise_data.get("solution_code", "")
    test_code = exercise_data.get("test_code", "")

    assert solution_code, f"{test_identifier}: Sem solution_code para testar."
    assert test_code, f"{test_identifier}: Sem test_code para validar a solução."

    mock_inputs_for_solution = None
    # Adapte esta lógica se você tiver inputs específicos por exercício
    if course_id == "python-basico" and exercise_id == "ex-estruturas-3":
         mock_inputs_for_solution = [("Adivinhe o número: ", "7")] 

    # 1. Executar solution_code
    solution_globals = {} 
    solution_output, solution_exception = execute_code(solution_code, solution_globals, mock_inputs_for_solution)

    expected_exception_type_str = exercise_data.get("expected_exception")
    expected_exception_message_contains = exercise_data.get("expected_exception_message_contains")

    if expected_exception_type_str:
        assert solution_exception is not None, \
            f"{test_identifier}: ERRO na solution_code: Esperava uma exceção do tipo '{expected_exception_type_str}', mas nenhuma foi levantada."
        
        # Tenta verificar o tipo da exceção. Isso é um pouco complexo porque solution_exception é uma string de traceback.
        # Uma verificação simples é ver se o nome do tipo da exceção está na string.
        assert expected_exception_type_str in solution_exception, \
            f"{test_identifier}: ERRO na solution_code: Esperava uma exceção do tipo '{expected_exception_type_str}', mas obteve uma exceção diferente ou o traceback não a menciona claramente.\nTraceback: {solution_exception}"
        
        if expected_exception_message_contains:
            assert expected_exception_message_contains in solution_exception, \
                f"{test_identifier}: ERRO na solution_code: A mensagem da exceção esperada ('{expected_exception_message_contains}') não foi encontrada no traceback.\nTraceback: {solution_exception}"
        
        # Se a exceção esperada ocorreu, consideramos que o solution_code passou nesta fase.
        # Podemos pular a execução do test_code, ou o test_code para esses casos deve ser vazio ou verificar algo específico.
        logger.info(f"{test_identifier}: Exceção esperada '{expected_exception_type_str}' foi corretamente levantada pelo solution_code.")
        return # Pula a execução do test_code se a exceção esperada ocorreu
    else:
        assert not solution_exception, \
            f"{test_identifier}: ERRO na solution_code:\n{solution_exception}"

    # 2. Executar test_code
    test_globals = solution_globals.copy() # Copia todos os globais da execução da solução
    test_globals['output'] = solution_output # Adiciona a saída capturada
    
    is_detailed_feedback_test = "print(f\"SUCESSO:" in test_code or "print(f'SUCESSO:" in test_code

    test_output_from_test_code, test_exception = execute_code(test_code, test_globals)

    if test_exception:
        
        # Se o test_code (que geralmente é um assert) levanta uma exceção,
        # o Pytest já a reporta bem (especialmente AssertionError).
        # Para outras exceções, é um erro no próprio test_code.
        pytest.fail(f"{test_identifier}: Exceção durante a execução do test_code:\n{test_exception}")
    else:
        # test_code executado sem exceções Python.
        if is_detailed_feedback_test:
            assert "SUCESSO" in test_output_from_test_code, \
                f"{test_identifier}: test_code (detalhado) executado, mas 'SUCESSO' não encontrado na saída.\nSaída do test_code: {test_output_from_test_code.strip()}"
        # Se não for um teste de feedback detalhado e não houve exceção,
        # o assert implícito no test_code passou. Não é necessário um assert explícito aqui.
        # Se o test_code fosse, por exemplo, "assert output == 'esperado'", e falhasse,
        # 'test_exception' conteria o AssertionError.
