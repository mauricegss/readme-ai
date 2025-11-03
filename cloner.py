import os
import shutil
import stat  # Precisamos desta nova importação
from git import Repo

# Diretório local para onde os repositórios serão clonados
PASTA_CLONE = "cloned_repo"

def handle_remove_readonly(func, path, exc_info):
    """
    Manipulador de erros para shutil.rmtree.

    Se o erro for de permissão (comum no Windows),
    ele muda a permissão do arquivo para escrita e tenta novamente.
    """
    # Verifica se a exceção é um PermissionError
    exc_type, exc_value, tb = exc_info
    if exc_value and isinstance(exc_value, PermissionError):
        try:
            # Força a permissão de escrita
            os.chmod(path, stat.S_IWRITE)
            # Tenta a função original (ex: os.unlink) novamente
            func(path)
        except Exception as e:
            print(f"Falha ao tentar forçar remoção de {path}: {e}")
            # Se falhar de novo, levanta a exceção original
            raise exc_value
    else:
        # Se for outro erro, apenas levanta a exceção
        raise exc_value


def clonar_repositorio(repo_url: str) -> str | None:
    """
    Clona um repositório para a pasta local './cloned_repo'.
    Limpa a pasta se ela já existir, lidando com erros de permissão.
    """
    
    caminho_local = os.path.abspath(PASTA_CLONE)
    
    try:
        # Limpa o diretório de clone anterior, se existir
        if os.path.exists(caminho_local):
            print(f"Limpando pasta existente: {PASTA_CLONE}...")
            # Adicionamos o 'onerror' aqui
            shutil.rmtree(caminho_local, onerror=handle_remove_readonly)
        
        print(f"Clonando {repo_url}...")
        
        # Executa o clone
        Repo.clone_from(repo_url, caminho_local)
        
        print(f"Clone concluído com sucesso em: {caminho_local}")
        return caminho_local

    except Exception as e:
        print(f"Erro ao clonar o repositório: {e}")
        # Garante a limpeza em caso de falha (também com 'onerror')
        if os.path.exists(caminho_local):
            shutil.rmtree(caminho_local, onerror=handle_remove_readonly)
        return None
