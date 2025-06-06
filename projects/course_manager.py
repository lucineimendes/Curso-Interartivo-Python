# -*- coding: utf-8 -*-
"""
Módulo para gerenciamento de dados de cursos.

Este módulo define a classe `CourseManager`, responsável por carregar,
salvar, e manipular informações sobre os cursos disponíveis na aplicação.
Os dados dos cursos são armazenados em formato JSON.
"""
import json
import logging
from pathlib import Path
import uuid # Para gerar IDs únicos para novos cursos

# Configuração de logging movida para app.py ou um módulo de configuração central.
# Se este módulo for executado diretamente, o logging básico pode ser configurado no if __name__ == '__main__':
logger = logging.getLogger(__name__)

class CourseManager:
    """
    Gerencia o carregamento, salvamento e manipulação de dados de cursos.

    Os cursos são armazenados em um arquivo JSON principal (`courses.json`)
    localizado no diretório de dados. Cada curso pode ter arquivos associados
    para lições e exercícios, cujos caminhos são referenciados nos dados do curso.

    Attributes:
        base_dir (Path): O diretório base onde este script está localizado (pasta 'projects').
        data_dir (Path): O caminho completo para o diretório 'data' dentro de 'projects'.
        courses_file (Path): O caminho completo para o arquivo 'courses.json'.
        courses (list): Uma lista de dicionários, onde cada dicionário representa um curso.
    """
    # data_dir_path_str é relativo ao diretório do script (projects/)
    def __init__(self, data_dir_path_str="data"):
        """
        Inicializa o CourseManager, configurando os caminhos e carregando os cursos.

        Args:
            data_dir_path_str (str): O nome do subdiretório de dados (relativo à pasta 'projects').
                                     Padrão é "data".
        """
        # base_dir é a pasta 'projects'
        self.base_dir = Path(__file__).resolve().parent
        self.data_dir = self.base_dir / data_dir_path_str
        # courses_file é projects/data/courses.json
        self.courses_file = self.data_dir / 'courses.json'
        
        self._ensure_data_files_exist()
        self.courses = self._load_courses()
        logger.info(f"CourseManager inicializado. Dados carregados de: {self.courses_file}")

    def _ensure_data_files_exist(self):
        """
        Garante que o diretório de dados e o arquivo JSON principal de cursos existam.

        Cria o diretório de dados e o arquivo `courses.json` (com uma lista vazia)
        se eles não existirem.
        """
        try:
            if not self.data_dir.exists():
                self.data_dir.mkdir(parents=True, exist_ok=True)
                logger.info(f"Diretório de dados '{self.data_dir}' criado.")
            
            if not self.courses_file.exists():
                with open(self.courses_file, 'w', encoding='utf-8') as f:
                    json.dump([], f, ensure_ascii=False, indent=4)
                logger.info(f"Arquivo de cursos principal criado em: {self.courses_file}")
        except OSError as e:
            logger.error(f"Erro ao garantir a existência dos arquivos/diretórios de dados: {e}", exc_info=True)
            # Considerar levantar uma exceção aqui se a criação falhar e for crítica.

    def _load_courses(self):
        """
        Carrega os dados dos cursos a partir do arquivo JSON principal (`courses.json`).

        Returns:
            list: Uma lista de dicionários representando os cursos. Retorna uma lista
                  vazia se o arquivo não existir, estiver mal formatado, ou ocorrer
                  um erro de I/O.
        """
        if not self.courses_file.exists():
            logger.warning(f"Arquivo de cursos '{self.courses_file}' não encontrado. Retornando lista vazia.")
            return []
        try:
            with open(self.courses_file, 'r', encoding='utf-8') as f:
                courses_data = json.load(f)
                if not isinstance(courses_data, list):
                    logger.error(f"Formato inválido em {self.courses_file}. Esperava uma lista, obteve {type(courses_data)}. Retornando lista vazia.")
                    return []
                logger.info(f"{len(courses_data)} cursos carregados de {self.courses_file}")
                return courses_data
        except json.JSONDecodeError:
            logger.error(f"Erro ao decodificar JSON de '{self.courses_file}'. Verifique a formatação. Retornando lista vazia.", exc_info=True)
            return []
        except IOError as e:
            logger.error(f"Erro de I/O ao ler '{self.courses_file}': {e}. Retornando lista vazia.", exc_info=True)
            return []

    def _save_courses(self):
        """
        Salva a lista atual de cursos (atributo `self.courses`) no arquivo JSON principal.

        Os dados são serializados para JSON com indentação para melhor legibilidade.
        """
        try:
            with open(self.courses_file, 'w', encoding='utf-8') as f:
                json.dump(self.courses, f, indent=4, ensure_ascii=False)
            logger.info(f"Cursos salvos em {self.courses_file}")
        except IOError as e:
            logger.error(f"Erro de I/O ao salvar cursos em '{self.courses_file}': {e}", exc_info=True)
        except TypeError as e:
            logger.error(f"Erro de tipo ao serializar cursos para JSON: {e}. Verifique os dados.", exc_info=True)


    def get_courses(self):
        """
        Retorna uma lista de todos os cursos carregados.

        Returns:
            list: A lista de dicionários de cursos.
        """
        return self.courses

    def get_course_by_id(self, course_id):
        """
        Retorna um curso específico pelo seu ID.

        Args:
            course_id (str): O ID do curso a ser procurado.
        Returns:
            dict | None: O dicionário do curso se encontrado, caso contrário None.
        """
        if not course_id:
            logger.warning("get_course_by_id: Tentativa de buscar curso com ID nulo ou vazio.")
            return None
        
        logger.debug(f"Buscando curso com ID '{course_id}'. Total de cursos: {len(self.courses)}")
        if self.courses and isinstance(self.courses, list) and len(self.courses) > 0 and isinstance(self.courses[0], dict):
            logger.debug(f"Primeiro curso na lista: {self.courses[0].get('id')}")
        else:
            logger.debug("Lista de cursos está vazia ou não é uma lista de dicionários.")
            
        for course in self.courses:
            if str(course.get('id')) == str(course_id): # Garante comparação de strings
                logger.debug(f"Curso encontrado: ID '{course.get('id')}'")
                return course
        logger.warning(f"Curso com ID '{course_id}' não encontrado.")
        return None

    def add_course(self, new_course_data):
        """
        Adiciona um novo curso à lista de cursos e salva as alterações.

        Se um ID não for fornecido em `new_course_data`, um UUID é gerado.
        Cria automaticamente o subdiretório do curso e arquivos JSON vazios para lições e exercícios.
        Os caminhos para `lessons_file` e `exercises_file` são padronizados se não fornecidos.

        Args:
            new_course_data (dict): Um dicionário contendo os dados do novo curso.
                                    Campos esperados incluem 'name', 'level', etc.
                                    'id', 'lessons_file', 'exercises_file' podem ser
                                    gerados/padronizados.
        Returns:
            dict | None: O dicionário do curso adicionado (com ID e caminhos de arquivo
                         atualizados) se bem-sucedido, caso contrário None.
        """
        if not isinstance(new_course_data, dict):
            logger.error(f"Dados inválidos para adicionar curso (não é um dicionário): {new_course_data}")
            return None

        course_id = new_course_data.get('id')
        if not course_id:
            course_id = str(uuid.uuid4())
            new_course_data['id'] = course_id
            logger.info(f"Novo ID de curso gerado: {course_id}")
        else:
            course_id = str(course_id) 
            new_course_data['id'] = course_id

        if self.get_course_by_id(course_id):
            logger.error(f"Falha ao adicionar curso: ID '{course_id}' já existe.")
            return None

        course_subdir_name = course_id 
        new_course_data.setdefault('lessons_file', f"{course_subdir_name}/lessons.json")
        new_course_data.setdefault('exercises_file', f"{course_subdir_name}/exercises.json")

        course_dir = self.data_dir / course_subdir_name
        try:
            course_dir.mkdir(parents=True, exist_ok=True)
            for key, content in [('lessons_file', []), ('exercises_file', [])]:
                file_path = self.data_dir / new_course_data[key]
                if not file_path.exists():
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(content, f, ensure_ascii=False, indent=4)
                    logger.info(f"Arquivo JSON '{file_path.name}' criado para o curso '{course_id}'.")
        except OSError as e:
            logger.error(f"Erro ao criar diretório/arquivos para o novo curso '{course_id}': {e}", exc_info=True)
            return None

        self.courses.append(new_course_data)
        self._save_courses()
        logger.info(f"Curso '{new_course_data.get('name', 'Sem Nome')}' adicionado com ID '{course_id}'.")
        return new_course_data

    def update_course(self, course_id, updated_data):
        """
        Atualiza os dados de um curso existente e salva as alterações.

        O ID do curso não pode ser alterado através deste método. Se `updated_data`
        contiver uma chave 'id' diferente do `course_id` fornecido, ela será ignorada.

        Args:
            course_id (str): O ID do curso a ser atualizado.
            updated_data (dict): Um dicionário contendo os campos a serem atualizados.
        Returns:
            dict | None: O dicionário do curso atualizado se encontrado e atualizado,
                         caso contrário None.
        """
        if not course_id or not isinstance(updated_data, dict):
            logger.error(f"ID ou dados inválidos para atualizar curso. ID: {course_id}, Dados: {updated_data}")
            return None

        course_id_str = str(course_id)
        course_to_update = None
        course_index = -1

        for i, course in enumerate(self.courses):
            if str(course.get('id')) == course_id_str:
                course_to_update = course
                course_index = i
                break
        
        if course_to_update:
            if 'id' in updated_data and str(updated_data['id']) != course_id_str:
                logger.warning(f"Tentativa de alterar ID do curso '{course_id_str}' para '{updated_data['id']}'. IDs não podem ser alterados. Chave 'id' ignorada.")
                updated_data.pop('id', None) 
            
            original_lessons_file = course_to_update.get('lessons_file')
            original_exercises_file = course_to_update.get('exercises_file')

            course_to_update.update(updated_data)
            self.courses[course_index] = course_to_update # Garante que a referência na lista seja atualizada

            # Se os caminhos dos arquivos não foram fornecidos na atualização, mantenha os originais
            if 'lessons_file' not in updated_data and original_lessons_file:
                 self.courses[course_index]['lessons_file'] = original_lessons_file
            if 'exercises_file' not in updated_data and original_exercises_file:
                  self.courses[course_index]['exercises_file'] = original_exercises_file

            self._save_courses()
            logger.info(f"Curso '{course_id_str}' atualizado com sucesso.")
            return self.courses[course_index]
        
        logger.warning(f"Falha ao atualizar curso: ID '{course_id_str}' não encontrado.")
        return None

    def delete_course(self, course_id):
        """
        Deleta um curso da lista de cursos pelo seu ID e salva as alterações.

        Nota: Esta função atualmente não deleta o subdiretório de dados associado
        ao curso (contendo lições e exercícios).

        Args:
            course_id (str): O ID do curso a ser deletado.
        Returns:
            bool: True se o curso foi deletado com sucesso, False caso contrário.
        """
        if not course_id:
            logger.warning("delete_course: Tentativa de deletar curso com ID nulo ou vazio.")
            return False
        
        course_id_str = str(course_id)
        
        course_to_delete = self.get_course_by_id(course_id_str) 
        if not course_to_delete:
            logger.warning(f"Falha ao deletar curso: ID '{course_id_str}' não encontrado.")
            return False

        self.courses = [c for c in self.courses if str(c.get('id')) != course_id_str]
        self._save_courses()
        
        # Opcional: deletar o diretório de dados do curso
        # course_dir_to_delete = self.data_dir / course_id_str
        # if course_dir_to_delete.exists() and course_dir_to_delete.is_dir():
        #     try:
        #         import shutil
        #         shutil.rmtree(course_dir_to_delete)
        #         logger.info(f"Diretório de dados do curso '{course_id_str}' deletado de {course_dir_to_delete}.")
        #     except OSError as e:
        #         logger.error(f"Erro ao deletar o diretório de dados do curso '{course_id_str}': {e}", exc_info=True)

        logger.info(f"Curso '{course_to_delete.get('name', course_id_str)}' (ID: {course_id_str}) deletado.")
        return True

# Exemplo de uso (opcional, para teste direto do módulo)
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger.info("Testando CourseManager diretamente...")
    
    # course_manager_instance = CourseManager()
    # print("Cursos carregados:", course_manager_instance.get_courses())
    # Adicione mais testes aqui se necessário
