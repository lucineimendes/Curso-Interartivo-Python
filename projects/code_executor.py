# -*- coding: utf-8 -*-
"""
Módulo para execução controlada de código Python.

Este módulo fornece funcionalidades para executar strings de código Python
de forma isolada, capturando suas saídas padrão (stdout) e de erro (stderr),
bem como informações sobre exceções que possam ocorrer durante a execução.

É projetado para ser usado em ambientes onde código fornecido pelo usuário
precisa ser executado de forma segura, como em plataformas de aprendizado
interativo de programação ou sistemas de avaliação automática de código.
"""
import sys
import io
import logging
from contextlib import redirect_stdout, redirect_stderr

logger = logging.getLogger(__name__)

def execute_code(code_string, execution_globals=None):
    """
    Executa uma string de código Python em um ambiente controlado e captura sua saída.

    Redireciona stdout e stderr para capturar a saída do código executado.
    Utiliza `exec()` para executar o código. Se `execution_globals` for fornecido,
    o código será executado nesse escopo; caso contrário, um novo escopo é criado.
    Garante que `__name__` seja definido como `__executor__` no escopo de execução
    se não for fornecido de outra forma.

    Args:
        code_string (str): O código Python a ser executado.
        execution_globals (dict, optional): Um dicionário para usar como o escopo global
                                            para a execução. Defaults to None, que cria
                                            um novo dicionário vazio.

    Returns:
        dict: Um dicionário contendo os resultados da execução:
            - "returncode" (int): 0 se a execução foi bem-sucedida (sem exceções),
                                  1 se ocorreu uma exceção durante a execução.
            - "stdout" (str): Saída capturada do stdout.
            - "stderr" (str): Saída capturada do stderr (mensagens de erro).
            - "error_type" (str | None): O nome da classe da exceção (ex: "SyntaxError",
                                         "ValueError"), ou None se não houve erro.
    """
    if execution_globals is None:
        execution_globals = {}
    # Garante que __name__ está presente, se não for passado
    execution_globals.setdefault('__name__', '__executor__')

    try:
        stdout_buffer = io.StringIO()
        stderr_buffer = io.StringIO()
        with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
            exec(code_string, execution_globals)
        stdout = stdout_buffer.getvalue()
        stderr = stderr_buffer.getvalue()
        return {"returncode": 0, "stdout": stdout, "stderr": stderr, "error_type": None}
    except Exception as e:
        error_type_name = type(e).__name__
        return {"returncode": 1, "stdout": "", "stderr": f"{error_type_name}: {str(e)}", "error_type": error_type_name}

def execute_test(test_code, namespace=None):
    """
    Executa um bloco de código de teste Python em um ambiente controlado.

    Similar a `execute_code`, mas projetado especificamente para executar
    código de teste. O `namespace` fornecido é atualizado com `__builtins__`,
    `__name__` (definido como `__main__`), `__doc__`, e `__package__` para
    simular um ambiente de execução de script mais comum.
    Captura stdout e stderr. Trata `AssertionError` especificamente para
    indicar falha no teste.

    Args:
        test_code (str): A string contendo o código de teste Python a ser executado.
        namespace (dict, optional): Um dicionário para ser usado como o escopo global
                                    durante a execução do código de teste.
                                    Defaults to None, que cria um novo dicionário vazio.

    Returns:
        dict: Um dicionário contendo os resultados da execução do teste:
            - "returncode" (int): 0 para sucesso, 1 para falha (incluindo AssertionError).
            - "stdout" (str): Saída capturada do stdout.
            - "stderr" (str): Saída capturada do stderr. Em caso de AssertionError,
                              contém uma mensagem formatada "Teste falhou: <mensagem da asserção>".
    """
    stdout_buffer = io.StringIO()
    stderr_buffer = io.StringIO()
    
    if namespace is None:
        namespace = {}
    
    # Adicionar builtins necessários
    namespace.update({
        '__builtins__': __builtins__,
        '__name__': '__main__',
        '__doc__': None,
        '__package__': None
    })
    
    try:
        with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
            exec(test_code, namespace)

        return {
            "returncode": 0,
            "stdout": stdout_buffer.getvalue(),
            "stderr": ""
        }

    except AssertionError as e:
        return {
            "returncode": 1, # Indica falha
            "stdout": stdout_buffer.getvalue(),
            "stderr": f"Teste falhou: {str(e)}"
        }

    except Exception as e:
        logger.error(f"Erro ao executar teste: {e}")
        return {
            "returncode": 1, # Indica falha
            "stdout": stdout_buffer.getvalue(),
            "stderr": f"Erro ao executar teste: {str(e)}"
        }