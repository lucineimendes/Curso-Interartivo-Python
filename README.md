# Curso Interativo de Python

Bem-vindo ao Curso Interativo de Python! Este projeto visa criar uma plataforma web para o aprendizado da linguagem Python de forma prática e interativa. Os usuários poderão navegar por diferentes níveis de conteúdo, acessar lições teóricas e resolver exercícios diretamente no navegador, com execução de código em tempo real.

## Principais Funcionalidades (Planejadas/Implementadas)

*   **Conteúdo Estruturado:** Lições e exercícios organizados por níveis de dificuldade (Básico, Intermediário, Avançado).
*   **Interface Web Intuitiva:** Navegação fácil entre cursos, lições e exercícios.
*   **Editor de Código Embutido:** Permite que os usuários escrevam e testem código Python diretamente na plataforma.
*   **Execução de Código no Servidor:** O código submetido pelos usuários é executado no backend para validação e feedback.
*   **Gerenciamento de Conteúdo via JSON:** Facilita a adição e modificação de lições e exercícios.
*   **Testes Automatizados:** Garantia de qualidade e robustez da aplicação através de testes unitários.

## Tecnologias Utilizadas (Principais)

*   **Backend:** Python com um framework web Flask para a API.
*   **Frontend:** HTML, CSS, JavaScript
*   **Armazenamento de Dados do Curso:** Arquivos JSON
*   **Testes:** Pytest

## Estrutura Detalhada do Projeto:

A seguir, uma visualização da organização das pastas e arquivos principais do projeto:

## Estrutura do Projeto:

```
Curso-Interartivo-Python/
├───images
│   └───banner.png
├───projects
│   ├───data
│   │   ├───advanced
│   │   │   ├───exercises.json
│   │   │   └───lessons.json
│   │   ├───basic
│   │   │   ├───exercises.json
│   │   │   └───lessons.json
│   │   └───intermediate
│   │       ├───exercises.json
│   │       └───lessons.json
│   ├───static
│   │   ├───css
│   │   │   └───style.css
│   │   └───js
│   │       ├───editor.js
│   │       ├───exercise_handler.js
│   │       └───main.js
│   ├───templates
│   │   ├───404.html
│   │   ├───base.html
│   │   ├───code_editor.html
│   │   ├───courses.html
│   │   ├───course_detail.html
│   │   ├───course_details.html
│   │   ├───course_list.html
│   │   ├───exercise.html
│   │   ├───index.html
│   │   ├───lesson.html
│   │   └───lesson_detail.html
│   ├───testes
│   │   ├───conftest.py
│   │   ├───test_app.py
│   │   ├───test_exercise_manager.py
│   │   ├───test_lesson_manager.py
│   │   └───test_meta_exercise.py
│   ├───app.py
│   ├───code_executor.py
│   ├───course_manager.py
│   ├───exercise_manager.py
│   ├───lesson_manager.py
│   ├───run.py
│   └───__init__.py
├───.gitignore
├───LICENSE.md
├───pytest.ini
├───README.md
├───requirements.txt
└───test_run.log
```

### Descrição dos Componentes Principais:

*   **`projects/`**: Contém o núcleo da aplicação web.
    *   **`app.py`**: Ponto de entrada principal da aplicação web, gerenciando rotas e lógica de negócios.
    *   **`run.py`**: Script para iniciar o servidor de desenvolvimento.
    *   **`*_manager.py` (ex: `course_manager.py`)**: Módulos responsáveis por gerenciar diferentes aspectos do conteúdo do curso (cursos, lições, exercícios).
    *   **`code_executor.py`**: Módulo crucial para executar o código Python submetido pelos usuários de forma segura.
    *   **`data/`**: Armazena os dados do curso (lições, exercícios) em formato JSON, organizado por níveis.
    *   **`static/`**: Contém arquivos estáticos como CSS e JavaScript para o frontend.
    *   **`templates/`**: Arquivos HTML que compõem a interface do usuário.
    *   **`testes/`**: Suíte de testes automatizados para garantir a qualidade da aplicação.
*   **`images/`**: Recursos visuais utilizados no projeto.
*   **`.gitignore`**: Especifica arquivos e pastas a serem ignorados pelo Git.
*   **`LICENSE.md`**: Contém as informações sobre a licença de uso do projeto (MIT License).
*   **`README.md`**: Este arquivo, fornecendo uma visão geral do projeto.
*   **`requirements.txt`**: Lista as dependências Python do projeto, para serem instaladas com `pip install -r requirements.txt`.
*   **`pytest.ini`**: Arquivo de configuração para o framework de testes Pytest.
