# -*- coding: utf-8 -*-
"""
Módulo para gerenciamento de dados de lições.

Este módulo define a classe `LessonManager`, responsável por carregar
informações sobre as lições de arquivos JSON específicos associados a um curso.
"""
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)
# Assume que este manager está em Curso-Interartivo-Python/projects/
# DATA_DIR apontará para Curso-Interartivo-Python/projects/data/
DATA_DIR = Path(__file__).resolve().parent / 'data'

class LessonManager:
    """
    Gerencia o carregamento de dados de lições a partir de arquivos JSON.

    As lições são carregadas sob demanda de arquivos especificados, geralmente
    referenciados nos dados de um curso.
    """
    def __init__(self):
        """
        Inicializa o LessonManager.

        Atualmente, nenhuma ação de carregamento de dados é realizada
        durante a inicialização. As lições são carregadas sob demanda.
        """
        pass # Nenhuma ação de carregamento na inicialização

    def load_lessons_from_file(self, lessons_file_path_relative: str) -> list:
        """
        Carrega lições de um arquivo JSON específico, relativo à pasta 'data' do projeto.

        O caminho fornecido é combinado com o `DATA_DIR` do módulo para formar
        o caminho absoluto para o arquivo de lições.

        Args:
            lessons_file_path_relative (str): O caminho relativo para o arquivo JSON
                de lições, a partir do diretório 'data'.
                Exemplo: "nome_do_curso/lessons.json".

        Returns:
            list: Uma lista de dicionários, onde cada dicionário representa uma lição.
                  Retorna uma lista vazia se o caminho do arquivo não for fornecido,
                  o arquivo não for encontrado, ocorrer um erro de decodificação JSON,
                  ou qualquer outro erro de I/O.
        """
        if not lessons_file_path_relative:
            logger.warning("load_lessons_from_file chamado com caminho relativo vazio.")
            return []

        # Constrói o caminho completo para o arquivo de lições
        # lessons_file_path_relative é algo como "basic/lessons.json"
        full_file_path = DATA_DIR / lessons_file_path_relative
        
        logger.debug(f"Tentando carregar lições de: {full_file_path}")
        
        if full_file_path.exists() and full_file_path.is_file():
            try:
                with open(full_file_path, 'r', encoding='utf-8') as f:
                    lessons_data = json.load(f)
                    if not isinstance(lessons_data, list):
                        logger.error(f"Formato inválido em {full_file_path}. Esperava uma lista, obteve {type(lessons_data)}. Retornando lista vazia.")
                        return []
                    logger.info(f"Sucesso ao carregar {len(lessons_data)} lições de {full_file_path}")
                    return lessons_data
            except json.JSONDecodeError as e:
                logger.error(f"Erro de decodificação JSON ao carregar lições de {full_file_path}: {e}", exc_info=True)
            except IOError as e: # Captura erros de I/O mais genéricos
                logger.error(f"Erro de I/O ao carregar lições de {full_file_path}: {e}", exc_info=True)
            except Exception as e: # Captura qualquer outra exceção inesperada
                logger.error(f"Erro inesperado ao carregar lições de {full_file_path}: {e}", exc_info=True)
        else:
            logger.warning(f"Arquivo de lições não encontrado ou não é um arquivo: {full_file_path}")
            
        return [] # Retorna lista vazia se o arquivo não existe ou em caso de erro

    
