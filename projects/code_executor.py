# -*- coding: utf-8 -*-
import sys
import io
import logging
from contextlib import redirect_stdout, redirect_stderr

logger = logging.getLogger(__name__)

def execute_code(code):
    try:
        # Capturar a saída padrão e de erro
        stdout_buffer = io.StringIO()
        stderr_buffer = io.StringIO()

        # Executar o código no namespace global
        with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
            exec(code, globals())

        # Obter a saída e erros
        stdout = stdout_buffer.getvalue()
        stderr = stderr_buffer.getvalue()

        return {"returncode": 0, "stdout": stdout, "stderr": stderr}
    except Exception as e:
        return {"returncode": 1, "stdout": "", "stderr": str(e)}

def execute_test(test_code, namespace=None):
    """
    Executa código de teste em um ambiente controlado.
    
    Args:
        test_code (str): Código de teste para executar
        namespace (dict): Namespace opcional com variáveis predefinidas
        
    Returns:
        dict: Resultado da execução dos testes
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