import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)
# Assume que este manager está em Curso-Interartivo-Python/projects/
# DATA_DIR apontará para Curso-Interartivo-Python/projects/data/
DATA_DIR = Path(__file__).resolve().parent / 'data'

class ExerciseManager:
    def __init__(self):
        """
        Inicializa o ExerciseManager.
        Não carrega mais todos os exercícios na inicialização.
        """
        pass # Nenhuma ação de carregamento na inicialização

    def load_exercises_from_file(self, exercises_file_path_relative):
        """
        Carrega exercícios de um arquivo JSON específico, relativo à pasta 'data' do projeto.
        Ex: exercises_file_path_relative pode ser "basic/exercises.json"
        Retorna uma lista de exercícios ou uma lista vazia em caso de erro ou arquivo não encontrado.
        """
        if not exercises_file_path_relative:
            logger.warning("load_exercises_from_file_called_with_empty_path")
            return []

        # Constrói o caminho completo para o arquivo de exercícios
        full_file_path = DATA_DIR / exercises_file_path_relative
        
        logger.debug(f"Tentando carregar exercícios de: {full_file_path}")
        
        if full_file_path.exists() and full_file_path.is_file():
            try:
                with open(full_file_path, 'r', encoding='utf-8') as f:
                    exercises_data = json.load(f)
                    logger.info(f"Sucesso ao carregar {len(exercises_data)} exercícios de {full_file_path}")
                    return exercises_data
            except json.JSONDecodeError as e:
                logger.error(f"Erro de decodificação JSON ao carregar exercícios de {full_file_path}: {e}")
            except Exception as e:
                logger.error(f"Erro inesperado ao carregar exercícios de {full_file_path}: {e}")
        else:
            logger.warning(f"Arquivo de exercícios não encontrado ou não é um arquivo: {full_file_path}")
            
        return [] # Retorna lista vazia se o arquivo não existe ou em caso de erro

    # A lógica de `get_exercise` e `check_exercise` foi movida ou adaptada em `app.py`.
    # `app.py` agora carrega a lista de exercícios e encontra o específico por ID.
    # A execução do código de exercício (check_exercise) é feita em `app.py` usando `code_executor`.
    # Se você tinha uma lógica complexa em `check_exercise` aqui, ela precisaria ser
    # invocada por `app.py` após obter os detalhes do exercício.
    # Por simplicidade e seguindo o padrão do diff, este manager foca apenas no carregamento.
