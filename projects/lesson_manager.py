import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)
# Assume que este manager está em Curso-Interartivo-Python/projects/
# DATA_DIR apontará para Curso-Interartivo-Python/projects/data/
DATA_DIR = Path(__file__).resolve().parent / 'data'

class LessonManager:
    def __init__(self):
        """
        Inicializa o LessonManager.
        Não carrega mais todas as lições na inicialização.
        """
        pass # Nenhuma ação de carregamento na inicialização

    def load_lessons_from_file(self, lessons_file_path_relative):
        """
        Carrega lições de um arquivo JSON específico, relativo à pasta 'data' do projeto.
        Ex: lessons_file_path_relative pode ser "basic/lessons.json"
        Retorna uma lista de lições ou uma lista vazia em caso de erro ou arquivo não encontrado.
        """
        if not lessons_file_path_relative:
            logger.warning("load_lessons_from_file_called_with_empty_path")
            return []

        # Constrói o caminho completo para o arquivo de lições
        # lessons_file_path_relative é algo como "basic/lessons.json"
        full_file_path = DATA_DIR / lessons_file_path_relative
        
        logger.debug(f"Tentando carregar lições de: {full_file_path}")
        
        if full_file_path.exists() and full_file_path.is_file():
            try:
                with open(full_file_path, 'r', encoding='utf-8') as f:
                    lessons_data = json.load(f)
                    logger.info(f"Sucesso ao carregar {len(lessons_data)} lições de {full_file_path}")
                    return lessons_data
            except json.JSONDecodeError as e:
                logger.error(f"Erro de decodificação JSON ao carregar lições de {full_file_path}: {e}")
            except Exception as e:
                logger.error(f"Erro inesperado ao carregar lições de {full_file_path}: {e}")
        else:
            logger.warning(f"Arquivo de lições não encontrado ou não é um arquivo: {full_file_path}")
            
        return [] # Retorna lista vazia se o arquivo não existe ou em caso de erro

    # Métodos antigos como get_lesson ou get_lessons_by_course (se existiam e dependiam de dados pré-carregados)
    # foram removidos. A lógica de encontrar uma lição específica agora reside em app.py,
    # após carregar a lista de lições do arquivo apropriado.
