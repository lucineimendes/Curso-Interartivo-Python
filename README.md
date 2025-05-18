# Curso Interativo Python

Uma plataforma de aprendizado interativo para Python, construída com Flask.

## Sumário

*   [Funcionalidades](#funcionalidades)
*   [Tecnologias Utilizadas](#tecnologias-utilizadas)
*   [Pré-requisitos](#pré-requisitos)
*   [Instalação](#instalação)
*   [Execução](#execução)
*   [Documentação da API](#documentação-da-api)
*   [Detalhes da Arquitetura e Implementação](#detalhes-da-arquitetura-e-implementação)
    *   [Visão Geral e Estrutura Principal](#visão-geral-e-estrutura-principal)
    *   [Gerenciamento de Dados (Managers)](#gerenciamento-de-dados-managers)
    *   [Execução Segura de Código do Usuário (`code_executor.py`)](#execução-segura-de-código-do-usuário-code_executorpy)
    *   Verificação de Exercícios (`api/check-exercise`)
    *   Estratégia de Testes Automáticos
    *   Outros Aspectos
    *   Considerações sobre Escalabilidade

## Funcionalidades

*   Visualização de cursos e suas respectivas lições.
*   Conteúdo de lições apresentado de forma clara.
*   Editor de código integrado para resolução de exercícios.
*   Execução de código Python submetido pelo usuário.
*   Verificação automática de exercícios com base em testes predefinidos.
*   Navegação intuitiva entre cursos, lições e exercícios.
*   API para interações programáticas (execução de código, verificação de exercícios).

## Tecnologias Utilizadas

*   **Backend:** Python, Flask
*   **Frontend:** HTML, CSS, JavaScript (implícito pelos templates Flask)
*   **Armazenamento de Dados:** Arquivos JSON
*   **Testes:** Pytest
*   **Outros:** `pathlib`, `logging`, `uuid`

## Pré-requisitos

*   Python 3.8 ou superior
*   pip (gerenciador de pacotes Python)

## Instalação

1.  Clone o repositório (ou baixe os arquivos do projeto).
2.  Navegue até o diretório raiz do projeto: `c:\Users\lucin\OneDrive\Dev_Python\Projetos Python\Curso-Interartivo-Python`
3.  Crie e ative um ambiente virtual (recomendado):
    ```bash
    python -m venv venv
    # Windows
    .\venv\Scripts\activate
    # macOS/Linux
    # source venv/bin/activate
    ```
4.  Instale as dependências (se você criar um `requirements.txt`):
    ```bash
    pip install Flask flask-cors pytest
    # Ou, se tiver um requirements.txt:
    # pip install -r requirements.txt
    ```
    *(Nota: O `setup.py` lista Flask, mas para desenvolvimento direto, instalar explicitamente ou via `requirements.txt` é comum.)*

## Execução

Para iniciar a aplicação em modo de desenvolvimento:

```bash
python projects/run.py
```

A aplicação estará disponível em `http://localhost:5000` (ou `http://0.0.0.0:5000`).

## Documentação da API

A documentação detalhada da API, gerada a partir das docstrings do código, pode ser encontrada em:
`docs_markdown/projects.md`

---

## Detalhes da Arquitetura e Implementação

Este documento detalha a estrutura e o funcionamento do projeto de sistema de curso interativo desenvolvido em Python, utilizando o framework Flask. O projeto foi concebido com foco em modularidade, separação de responsabilidades e uma estratégia robusta de testes automáticos.
**Visão Geral e Estrutura Principal:**
[![Estrutura do Projeto](\images\Estrutura_projeto.png)](\images\Estrutura_projeto.png)
*(Clique na imagem para ampliar)*

O projeto é um sistema de curso interativo que permite a apresentação de conteúdos de cursos e lições, e a execução e verificação de código Python submetido pelo usuário para exercícios práticos.

A arquitetura central é uma aplicação web Flask (`app.py`). Esta aplicação atua como o "centro nervoso", recebendo requisições e orquestrando as operações necessárias.

Existe uma **separação clara entre a interface de usuário (UI) e a API**:
*   **Rotas de UI:** Servem páginas HTML usando *template handlers* (como a página inicial, lista de cursos, e páginas de lições/exercícios).
*   **Rotas de API:** Começam com `/api` e retornam dados em formato JSON usando `jsonify`.
*   O CORS (Cross-Origin Resource Sharing) está habilitado globalmente usando `flask_cors.CORS` para permitir que frontends em domínios ou portas diferentes possam interagir com a API.

A aplicação Flask (`app.py`) delega o "trabalho pesado" relacionado ao gerenciamento de dados a módulos dedicados, os *managers*.

O projeto está organizado em módulos Python, com o código principal localizado na pasta `projects/`. A execução da aplicação para desenvolvimento é feita através de um script `run.py` na raiz do projeto, que adiciona o diretório `projects` ao `sys.path` e importa o aplicativo Flask.

**Gerenciamento de Dados (Managers):**

O projeto utiliza arquivos JSON na pasta `data/` para armazenar as informações de cursos, lições e exercícios. O gerenciamento desses dados é feito por classes específicas:
*   `CourseManager`: Lida com as informações dos cursos.
*   `LessonManager`: Gerencia as lições.
*   `ExerciseManager`: Cuida dos exercícios.

Uma prática adotada para otimizar o uso de memória é que `LessonManager` e `ExerciseManager` **não carregam todos os dados na inicialização**. Em vez disso, eles possuem funções como `load_lessons_from_file` e `load_exercises_from_file` que carregam os dados de um arquivo JSON específico *sob demanda*, apenas quando são necessários.

O uso da biblioteca `pathlib` nos managers ajuda a lidar com caminhos de arquivo de forma portátil, funcionando corretamente em diferentes sistemas operacionais.

**Execução Segura de Código do Usuário (`code_executor.py`):**

Um componente crucial do sistema é a execução de código Python submetido pelos usuários para os exercícios. Esta funcionalidade é implementada no módulo `code_executor.py`.

A execução é realizada usando a função `exec()` do Python, mas de forma controlada para garantir a segurança e capturar a saída.
*   As funções `execute_code` e `execute_test` utilizam `io.StringIO` e os *context managers* `contextlib.redirect_stdout` e `redirect_stderr` para **capturar qualquer coisa que o código do usuário imprima no `stdout` (saída padrão) ou `stderr` (saída de erro)**.
*   A saída e os erros capturados são retornados em um dicionário, juntamente com um código de retorno indicando sucesso (`0`) ou falha (`1`), e o tipo de erro, se aplicável.
*   Essa captura **impede que a saída ou erros do código do usuário apareçam no console do servidor** onde a aplicação Flask está rodando.

`execute_code` aceita um dicionário opcional `execution_globals` para definir o escopo global da execução. `execute_test` aceita um dicionário `namespace` para variáveis predefinidas.

**Verificação de Exercícios (`api/check-exercise`):**

A rota `/api/check-exercise` em `app.py` implementa a lógica para verificar se a solução de um exercício enviada pelo usuário está correta. O processo envolve:
1.  Obter o código enviado pelo usuário (`user_code`) e os detalhes do exercício, incluindo o `test_code` definido no JSON do exercício.
2.  Executar o `user_code` usando `code_executor.execute_code`, capturando sua saída (`user_stdout`) e erros (`user_stderr`).
3.  Se o `user_code` executou com sucesso (sem erros de sintaxe ou runtime) e o exercício possui um `test_code`, o `test_code` é executado usando `code_executor.execute_test`.
4.  **A chave para a verificação é que a saída do `user_code` (`user_stdout`) é passada como uma variável global chamada `output` para o ambiente de execução do `test_code`**.
5.  O `test_code` contido no JSON do exercício pode então **realizar asserções ou verificações programáticas na variável `output`** para determinar se a saída do usuário está correta. O `test_code` frequentemente imprime uma mensagem como "SUCCESS" em caso de sucesso.
6.  A API retorna um resultado JSON indicando `success` (se o código do usuário rodou e o `test_code` passou, ou se não havia `test_code`), a `output` combinada (saída do usuário + saída do teste), e `details` (erros ou mensagens do teste).

**Estratégia de Testes Automáticos:**

O projeto possui uma estratégia de testes automáticos **robusta** utilizando a biblioteca `pytest`.

Componentes e práticas de teste notáveis:
*   **`conftest.py`:** Este arquivo é fundamental no sistema de testes. Ele define *fixtures* que preparam o ambiente para os testes.
*   **Fixtures de Aplicação e Cliente:** As fixtures `app` e `client` fornecem, respectivamente, uma instância do aplicativo Flask no modo de teste (`app.config['TESTING'] is True`) e um cliente de teste (`FlaskClient`) para simular requisições HTTP às rotas da aplicação.
*   **`app_test_data` Fixture:** Esta fixture é configurada como `autouse`, o que significa que ela é executada automaticamente antes de cada teste que a solicita (ou implicitamente, se ela for declarada como `autouse=True` ou se outra fixture que a solicite for autoused). Sua função principal é **criar um conjunto de arquivos JSON temporários** para os dados de cursos, lições e exercícios.
*   **`monkeypatch`:** A fixture `app_test_data` utiliza a técnica de `monkeypatch` para modificar o comportamento dos managers durante os testes. Ela faz com que `LessonManager` e `ExerciseManager` (e potencialmente `CourseManager`) leiam e escrevam nos arquivos JSON *temporários* criados pela fixture, **isolando completamente os testes dos arquivos de dados reais**. Isso garante que os testes não modifiquem os dados de produção.
*   **`test_app.py`:** Contém testes que utilizam o cliente Flask para testar as rotas da UI e da API, como `test_index_route`, `test_course_list_route`, `test_execute_code_api`, e `test_check_exercise_api`, verificando respostas HTTP, status codes e conteúdo JSON.
*   **`test_meta_exercise.py` (Meta-teste):** Este é um nível de teste inovador. Em vez de escrever um teste manual para cada exercício individualmente, este script **varre a pasta de dados em busca de *todos* os arquivos JSON de exercícios**. Para cada exercício encontrado, ele **gera um teste automaticamente**. Este teste gerado executa o `solution_code` (código de exemplo de solução) do exercício e então executa o `test_code` correspondente, **validando que a solução funciona conforme o esperado pelo teste definido**. Esta abordagem **garante a qualidade de todo o conteúdo dos exercícios** de forma altamente eficiente, sem a necessidade de escrever testes específicos para cada um. Ele verifica a presença de `solution_code` e `test_code` para cada exercício e lida com a possibilidade de exceções esperadas no `solution_code`.

A estratégia de testes demonstra um **cuidado grande com a automação e a confiabilidade**.

**Outros Aspectos:**

*   O projeto utiliza a biblioteca padrão `logging` do Python para registrar eventos e erros na aplicação.
*   O arquivo `setup.py` define o pacote `curso_interativo_python`, lista o Flask como dependência, e configura um *entry point* `curso-run` para executar a aplicação via linha de comando.

**Considerações sobre Escalabilidade:**

Embora a estrutura baseada em arquivos JSON e o carregamento sob demanda funcionem bem para o tamanho atual do projeto, vale a pena considerar a reflexão sobre a **escalabilidade**. Se o projeto crescesse para muitos cursos, milhões de usuários e submissões constantes, os arquivos JSON poderiam se tornar um **gargalo** devido a desafios de gerenciamento e concorrência. Nesse cenário, uma possível evolução seria a migração para um banco de dados (relacional ou NoSQL).

Em resumo, o projeto apresenta uma **arquitetura bem modular e com foco em qualidade**, aplicando diversas boas práticas de desenvolvimento Python e web, especialmente na separação UI/API, gerenciamento de dados com otimização de memória, execução segura de código externo e uma estratégia de testes abrangente e automatizada.
