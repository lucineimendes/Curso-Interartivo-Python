# -*- coding: utf-8 -*-
import json
import logging
from pathlib import Path
import uuid # Para gerar IDs únicos para novos cursos

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CourseManager:
    def __init__(self, data_dir_path_str="data"):
        """
        Inicializa o CourseManager.
        Args:
            data_dir_path_str (str): O nome do diretório de dados, relativo ao diretório deste script.
                                     Padrão é "data".
        """
        # Define o diretório base como o diretório onde este arquivo (course_manager.py) está localizado.
        self.base_dir = Path(__file__).resolve().parent
        # Define o diretório de dados completo.
        self.data_dir = self.base_dir / data_dir_path_str
        # Define o caminho completo para o arquivo principal de cursos.
        self.courses_file = self.data_dir / 'courses.json'
        
        self._ensure_data_files_exist()
        self.courses = self._load_courses()
        logger.info(f"CourseManager inicializado. Dados carregados de: {self.courses_file}")

    def _ensure_data_files_exist(self):
        """Garante que o diretório de dados e o arquivo principal de cursos existam."""
        try:
            if not self.data_dir.exists():
                self.data_dir.mkdir(parents=True, exist_ok=True)
                logger.info(f"Diretório de dados criado em: {self.data_dir}")
            
            if not self.courses_file.exists():
                with open(self.courses_file, 'w', encoding='utf-8') as f:
                    json.dump([], f, ensure_ascii=False, indent=4) # Cria um arquivo JSON com uma lista vazia
                logger.info(f"Arquivo de cursos principal criado em: {self.courses_file}")
        except OSError as e:
            logger.error(f"Erro ao garantir a existência dos arquivos/diretórios de dados: {e}", exc_info=True)
            # Considerar levantar uma exceção aqui se a criação falhar e for crítica.

    def _load_courses(self):
        """Carrega os cursos do arquivo JSON principal."""
        if not self.courses_file.exists():
            logger.warning(f"Arquivo de cursos não encontrado em {self.courses_file} ao tentar carregar. Retornando lista vazia.")
            return []
        try:
            with open(self.courses_file, 'r', encoding='utf-8') as f:
                courses_data = json.load(f)
                if not isinstance(courses_data, list):
                    logger.error(f"Formato inválido em {self.courses_file}. Esperava uma lista, obteve {type(courses_data)}. Retornando lista vazia.")
                    return []
                logger.debug(f"{len(courses_data)} cursos carregados de {self.courses_file}")
                return courses_data
        except json.JSONDecodeError:
            logger.error(f"Erro ao decodificar JSON do arquivo de cursos: {self.courses_file}. Verifique a formatação. Retornando lista vazia.", exc_info=True)
            return []
        except IOError as e:
            logger.error(f"Erro de I/O ao ler o arquivo de cursos {self.courses_file}: {e}. Retornando lista vazia.", exc_info=True)
            return []

    def _save_courses(self):
        """Salva a lista atual de cursos no arquivo JSON principal."""
        try:
            with open(self.courses_file, 'w', encoding='utf-8') as f:
                json.dump(self.courses, f, indent=4, ensure_ascii=False)
            logger.info(f"Cursos salvos com sucesso em {self.courses_file}")
        except IOError as e:
            logger.error(f"Erro de I/O ao salvar cursos em {self.courses_file}: {e}", exc_info=True)
            # Considerar levantar uma exceção aqui ou ter um mecanismo de retry/backup.
        except TypeError as e:
            logger.error(f"Erro de tipo ao tentar serializar cursos para JSON: {e}. Verifique os dados dos cursos.", exc_info=True)


    def get_courses(self): # Renomeado de get_all_courses para corresponder ao uso em app.py
        """Retorna todos os cursos carregados."""
        return self.courses

    def get_course_by_id(self, course_id):
        """Retorna um curso específico pelo seu ID."""
        if not course_id:
            logger.warning("CourseManager.get_course_by_id: Tentativa de buscar curso com ID nulo ou vazio.")
            return None
        
        logger.debug(f"CourseManager.get_course_by_id: Buscando ID '{course_id}'. Total de cursos em self.courses: {len(self.courses)}")
        # Log para inspecionar o primeiro curso, se houver, para verificar sua estrutura durante os testes.
        if self.courses and isinstance(self.courses, list) and len(self.courses) > 0 and isinstance(self.courses[0], dict):
            logger.debug(f"CourseManager.get_course_by_id: Primeiro curso em self.courses: {self.courses[0]}")
        else:
            logger.debug(f"CourseManager.get_course_by_id: self.courses está vazio ou não é uma lista de dicionários.")
            
        for course in self.courses:
            if course.get('id') == str(course_id): # Garante comparação de strings
                logger.debug(f"CourseManager.get_course_by_id: Curso encontrado: {course}")
                return course
        logger.warning(f"CourseManager.get_course_by_id: Curso com ID '{course_id}' não encontrado na lista.")
        return None

    def add_course(self, new_course_data):
        """
        Adiciona um novo curso.
        Gera um ID se não fornecido.
        Cria automaticamente o subdiretório do curso e arquivos JSON vazios para lições e exercícios.
        """
        if not isinstance(new_course_data, dict):
            logger.error(f"Tentativa de adicionar curso com dados inválidos (não é um dicionário): {new_course_data}")
            return None # Ou levantar ValueError

        course_id = new_course_data.get('id')
        if not course_id:
            course_id = str(uuid.uuid4())
            new_course_data['id'] = course_id
        else:
            course_id = str(course_id) # Garante que seja string
            new_course_data['id'] = course_id


        if self.get_course_by_id(course_id):
            logger.error(f"Falha ao adicionar: Curso com ID '{course_id}' já existe.")
            return None # Ou levantar ValueError

        # Define os caminhos para os arquivos de lições e exercícios relativos ao data_dir
        # e usando o ID do curso como nome do subdiretório.
        course_subdir_name = course_id # Usar o ID do curso para o nome do subdiretório
        new_course_data.setdefault('lessons_file', f"{course_subdir_name}/lessons.json")
        new_course_data.setdefault('exercises_file', f"{course_subdir_name}/exercises.json")

        # Cria o subdiretório para o curso e os arquivos JSON vazios
        course_specific_data_path = self.data_dir / course_subdir_name
        try:
            course_specific_data_path.mkdir(parents=True, exist_ok=True)

            lessons_path = course_specific_data_path / "lessons.json"
            exercises_path = course_specific_data_path / "exercises.json"

            for file_path, content in [(lessons_path, []), (exercises_path, [])]:
                if not file_path.exists():
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(content, f, ensure_ascii=False, indent=4)
                    logger.info(f"Arquivo JSON criado: {file_path}")
        except OSError as e:
            logger.error(f"Erro ao criar diretório/arquivos para o novo curso '{course_id}': {e}", exc_info=True)
            # Considerar se deve prosseguir ou retornar erro
            return None


        self.courses.append(new_course_data)
        self._save_courses()
        logger.info(f"Curso '{new_course_data.get('name', 'Sem Nome')}' adicionado com ID '{course_id}'.")
        return new_course_data

    def update_course(self, course_id, updated_data):
        """Atualiza um curso existente. O ID do curso não pode ser alterado."""
        if not course_id or not isinstance(updated_data, dict):
            logger.error(f"Tentativa de atualizar curso com ID ou dados inválidos. ID: {course_id}, Dados: {updated_data}")
            return None # Ou levantar ValueError

        course_id_str = str(course_id)
        course_to_update = None
        course_index = -1

        for i, course in enumerate(self.courses):
            if course.get('id') == course_id_str:
                course_to_update = course
                course_index = i
                break
        
        if course_to_update:
            # Impede a alteração do ID do curso através dos dados atualizados
            if 'id' in updated_data and str(updated_data['id']) != course_id_str:
                logger.warning(f"Tentativa de alterar ID do curso '{course_id_str}' para '{updated_data['id']}' durante atualização. IDs não podem ser alterados. A chave 'id' nos dados de atualização será ignorada.")
                updated_data.pop('id', None) # Remove a tentativa de mudança de ID
            
            # Atualiza os campos do curso
            # Garante que os caminhos dos arquivos de lições/exercícios não sejam removidos acidentalmente
            # se não estiverem presentes em updated_data.
            original_lessons_file = course_to_update.get('lessons_file')
            original_exercises_file = course_to_update.get('exercises_file')

            self.courses[course_index].update(updated_data)

            # Restaura caminhos se foram removidos e não explicitamente alterados
            if 'lessons_file' not in updated_data and original_lessons_file:
                 self.courses[course_index]['lessons_file'] = original_lessons_file
            if 'exercises_file' not in updated_data and original_exercises_file:
                 self.courses[course_index]['exercises_file'] = original_exercises_file


            self._save_courses()
            logger.info(f"Curso '{course_id_str}' atualizado com sucesso.")
            return self.courses[course_index]
        
        logger.warning(f"Falha ao atualizar: Curso com ID '{course_id_str}' não encontrado.")
        return None # Ou levantar ValueError

    def delete_course(self, course_id):
        """
        Deleta um curso pelo seu ID.
        Opcionalmente, pode-se adicionar a remoção do diretório de dados do curso.
        """
        if not course_id:
            logger.warning("Tentativa de deletar curso com ID nulo ou vazio.")
            return False

        course_id_str = str(course_id)
        original_len = len(self.courses)
        
        course_to_delete = self.get_course_by_id(course_id_str) # Para obter o nome para logging
        if not course_to_delete:
            logger.warning(f"Falha ao deletar: Curso com ID '{course_id_str}' não encontrado.")
            return False

        self.courses = [c for c in self.courses if c.get('id') != course_id_str]
        
        if len(self.courses) < original_len:
            self._save_courses()
            logger.info(f"Curso '{course_to_delete.get('name', 'ID: '+course_id_str)}' deletado com sucesso.")
            
            # Opcional: remover o diretório de dados do curso e seus arquivos
            # course_specific_data_path = self.data_dir / course_id_str
            # if course_specific_data_path.exists() and course_specific_data_path.is_dir():
            #     try:
            #         import shutil
            #         shutil.rmtree(course_specific_data_path)
            #         logger.info(f"Diretório de dados do curso '{course_id_str}' removido: {course_specific_data_path}")
            #     except OSError as e:
            #         logger.error(f"Erro ao remover o diretório de dados do curso '{course_id_str}': {e}", exc_info=True)
            return True
        
        # Este caso não deveria acontecer se get_course_by_id encontrou o curso, mas é uma salvaguarda.
        logger.warning(f"Falha ao deletar: Curso com ID '{course_id_str}' não foi removido da lista, embora possa ter sido encontrado.")
        return False

# Exemplo de uso (opcional, para teste direto do módulo)
if __name__ == '__main__':
    logger.info("Testando CourseManager diretamente...")
    # Assume que este script está em 'projects/', e 'data/' está em 'projects/data/'
    # Se 'data' estiver um nível acima (Curso-Interartivo-Python/data), use:
    # course_manager_instance = CourseManager(data_dir_path_str="../data") 
    course_manager_instance = CourseManager()

    # Listar cursos
    print("\nCursos existentes:")
    for course_item in course_manager_instance.get_courses():
        print(f"- ID: {course_item.get('id')}, Nome: {course_item.get('name')}")

    # Adicionar um novo curso (exemplo)
    # new_course_details = {
    #     "name": "Python Avançado",
    #     "description": "Tópicos avançados em Python.",
    #     # "id": "advanced-python" # Opcional, será gerado se não fornecido
    # }
    # added_course = course_manager_instance.add_course(new_course_details)
    # if added_course:
    #     print(f"\nCurso adicionado: {added_course.get('name')} com ID {added_course.get('id')}")
    #     print(f"  Arquivo de lições: {added_course.get('lessons_file')}")
    #     print(f"  Arquivo de exercícios: {added_course.get('exercises_file')}")

    #     # Tentar adicionar o mesmo curso novamente (deve falhar se o ID for o mesmo)
    #     # course_manager_instance.add_course(new_course_details)


    # # Atualizar um curso (exemplo - use um ID existente)
    # course_id_to_update = "basic" # Substitua por um ID válido do seu courses.json
    # if course_manager_instance.get_course_by_id(course_id_to_update):
    #     updated_info = {"description": "Uma descrição atualizada para o curso Básico."}
    #     updated_c = course_manager_instance.update_course(course_id_to_update, updated_info)
    #     if updated_c:
    #         print(f"\nCurso '{course_id_to_update}' atualizado: Nova descrição - '{updated_c.get('description')}'")
    # else:
    #     print(f"\nCurso com ID '{course_id_to_update}' não encontrado para atualização.")

    # # Deletar um curso (exemplo - use um ID existente que você quer deletar)
    # course_id_to_delete = "advanced-python" # Substitua por um ID válido
    # if course_manager_instance.get_course_by_id(course_id_to_delete):
    #     if course_manager_instance.delete_course(course_id_to_delete):
    #         print(f"\nCurso '{course_id_to_delete}' deletado.")
    #     else:
    #         print(f"\nFalha ao deletar o curso '{course_id_to_delete}'.")
    # else:
    #      print(f"\nCurso com ID '{course_id_to_delete}' não encontrado para deleção.")

    print("\nLista de cursos após operações:")
    for course_item in course_manager_instance.get_courses():
        print(f"- ID: {course_item.get('id')}, Nome: {course_item.get('name')}")
