# c:\Users\lucin\OneDrive\Dev_Python\Projetos Python\Curso-Interartivo-Python\run.py
import sys
from pathlib import Path
import logging

# Adiciona o diretório raiz do projeto ao sys.path
# Isso garante que o pacote 'projects' possa ser importado corretamente.
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Agora podemos importar o 'app' de 'projects.app'
from projects.app import app, logger as app_logger # Importa a instância do app e seu logger

if __name__ == '__main__':
    # Você pode configurar o nível de log aqui se desejar,
    # ou confiar na configuração dentro de projects/app.py
    # Exemplo: app_logger.setLevel(logging.DEBUG)
    
    app_logger.info("Iniciando servidor de desenvolvimento Flask a partir de run.py.")
    # As configurações de host, port e debug podem ser as mesmas que você tinha
    # no if __name__ == '__main__' do seu projects/app.py
    app.run(debug=True, host='0.0.0.0', port=5000)
