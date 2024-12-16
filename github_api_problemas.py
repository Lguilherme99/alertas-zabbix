import os
import subprocess
from datetime import datetime
import shutil

# Configuração
REPO_DIR = "/opt/API/alertas-zabbix"  # Caminho onde o repositório será clonado localmente
ZABBIX_ALERTS_FILE = "/opt/API/Historico_triggers.txt"  # Caminho do arquivo de alertas do Zabbix
REMOTE_REPO = "git@github.com:Lguilherme99/alertas-zabbix.git"  # URL SSH do seu repositório no GitHub

# Clone o repositório se ele não existir localmente
if not os.path.exists(REPO_DIR):
    subprocess.run(["git", "clone", REMOTE_REPO, REPO_DIR])

# Copie o arquivo de alertas para o repositório local
shutil.copy(ZABBIX_ALERTS_FILE, os.path.join(REPO_DIR, "problemas.txt"))

# Navegue para o diretório do repositório
os.chdir(REPO_DIR)

# Adicione e commite as alterações
subprocess.run(["git", "add", "problemas.txt"])
commit_message = f"Atualização do histórico de alertas em {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
subprocess.run(["git", "commit", "-m", commit_message])

# Envie as alterações para o repositório remoto
subprocess.run(["git", "push"])
