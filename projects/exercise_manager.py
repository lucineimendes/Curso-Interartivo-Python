# -*- coding: utf-8 -*-
"""
Módulo para gerenciamento de dados de exercícios.

Este módulo define a classe `ExerciseManager`, responsável por carregar
informações sobre os exercícios de arquivos JSON específicos associados a um curso.
Também fornece uma função utilitária para buscar um exercício por ID dentro de um curso.
"""
import json
import logging
from pathlib import Path

# Import CourseManager para obter o caminho do arquivo de exercícios
# Isso cria uma dependência, mas alinha com a lógica de app.py
# from .course_manager import CourseManager # Removido, pois get_exercise_by_id não usa mais CourseManager diretamente

logger = logging.getLogger(__name__)
# Assume que este manager está em Curso-Interartivo-Python/projects/
# DATA_DIR apontará para Curso-Interartivo-Python/projects/data/
DATA_DIR = Path(__file__).resolve().parent / 'data'

class ExerciseManager:
    """
    Gerencia o carregamento de dados de exercícios a partir de arquivos JSON.

    Os exercícios são carregados sob demanda de arquivos especificados, geralmente
    referenciados nos dados de um curso.
    """
    def __init__(self):
        """
        Inicializa o ExerciseManager.

        Nenhuma ação de carregamento de dados é realizada durante a inicialização.
        Os exercícios são carregados sob demanda.
        """
        pass # Nenhuma ação de carregamento na inicialização

    def load_exercises_from_file(self, exercises_file_path_relative: str) -> list:
        """
        Carrega exercícios de um arquivo JSON específico, relativo à pasta 'data' do projeto.

        O caminho fornecido é combinado com o `DATA_DIR` do módulo para formar
        o caminho absoluto para o arquivo de exercícios.

        Args:
            exercises_file_path_relative (str): O caminho relativo para o arquivo JSON
                de exercícios, a partir do diretório 'data'.
                Exemplo: "nome_do_curso/exercises.json".

        Returns:
            list: Uma lista de dicionários, onde cada dicionário representa um exercício.
                  Retorna uma lista vazia se o caminho do arquivo não for fornecido,
                  o arquivo não for encontrado, ocorrer um erro de decodificação JSON,
                  ou qualquer outro erro de I/O.
        """
        if not exercises_file_path_relative:
            logger.warning("load_exercises_from_file chamado com caminho relativo vazio.")
            return []

        # Constrói o caminho completo para o arquivo de exercícios
        full_file_path = DATA_DIR / exercises_file_path_relative
        
        logger.debug(f"Tentando carregar exercícios de: {full_file_path}")
        
        if full_file_path.exists() and full_file_path.is_file():
            try:
                with open(full_file_path, 'r', encoding='utf-8') as f:
                    exercises_data = json.load(f)
                    if not isinstance(exercises_data, list):
                        logger.error(f"Formato inválido em {full_file_path}. Esperava uma lista, obteve {type(exercises_data)}. Retornando lista vazia.")
                        return []
                    logger.info(f"Sucesso ao carregar {len(exercises_data)} exercícios de {full_file_path}")
                    return exercises_data
            except json.JSONDecodeError as e:
                logger.error(f"Erro de decodificação JSON ao carregar exercícios de {full_file_path}: {e}", exc_info=True)
            except IOError as e: # Captura erros de I/O mais genéricos
                logger.error(f"Erro de I/O ao carregar exercícios de {full_file_path}: {e}", exc_info=True)
            except Exception as e: # Captura qualquer outra exceção inesperada
                logger.error(f"Erro inesperado ao carregar exercícios de {full_file_path}: {e}", exc_info=True)
        else:
            logger.warning(f"Arquivo de exercícios não encontrado ou não é um arquivo: {full_file_path}")
            
        return [] # Retorna lista vazia se o arquivo não existe ou em caso de erro

# Função para ser importada pelos testes e outras partes da aplicação
def get_exercise_by_id(exercise_id: str, course_id: str) -> dict | None:
    """
    Busca um exercício específico pelo seu ID dentro de um curso.

    Esta função carrega os exercícios do arquivo JSON associado ao `course_id`
    e procura pelo `exercise_id` fornecido.

    Args:
        exercise_id (str): O ID do exercício a ser encontrado.
        course_id (str): O ID do curso ao qual o exercício pertence. Este ID é usado
                         para construir o caminho relativo para o arquivo de exercícios
                         (ex: "{course_id}/exercises.json").

    Returns:
        dict | None: O dicionário do exercício se encontrado, caso contrário None.
                     Retorna None também se `course_id` não for fornecido ou se
                     o arquivo de exercícios não for encontrado ou estiver mal formatado.
    """
    if not course_id:
        logger.warning("get_exercise_by_id chamado sem course_id.")
        return None

    # Constrói o caminho relativo para o arquivo de exercícios baseado no course_id.
    # Esta é uma convenção assumida: os exercícios de um curso estão em 'data/{course_id}/exercises.json'.
    # Se a estrutura de arquivos for diferente, esta lógica precisará ser ajustada.
    exercises_file_relative_path = f"{course_id}/exercises.json"

    mgr = ExerciseManager() # Cria uma instância para usar o método de carregamento
    all_exercises_for_course = mgr.load_exercises_from_file(exercises_file_relative_path)

    if not all_exercises_for_course: # Se a lista estiver vazia (arquivo não encontrado, erro de parse, etc.)
        logger.warning(f"Nenhum exercício carregado para o curso '{course_id}' a partir de '{exercises_file_relative_path}'.")
        return None

    for exercise in all_exercises_for_course:
        if isinstance(exercise, dict) and str(exercise.get("id")) == str(exercise_id):
            logger.debug(f"Exercício ID '{exercise_id}' encontrado no curso '{course_id}'.")
            return exercise
            
    logger.warning(f"Exercício com ID '{exercise_id}' não encontrado no arquivo '{exercises_file_relative_path}' para o curso '{course_id}'.")
    return None

    
