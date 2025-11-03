import os
import json
import tomli  # pip install tomli
from pathlib import Path # Usaremos pathlib para lidar com caminhos

# --- CONSTANTES GLOBAIS ---

# Mapeamento de arquivos de definição de projeto para suas tecnologias
ARQUIVOS_CHAVE = {
    # Python
    "requirements.txt": "Python",
    "pyproject.toml": "Python",
    "Pipfile": "Python",
    # JavaScript
    "package.json": "JavaScript (Node.js)",
    # Java
    "pom.xml": "Java (Maven)",
    "build.gradle": "Java (Gradle)",
    # Ruby
    "Gemfile": "Ruby",
    # Go
    "go.mod": "Go",
    # C#
    ".csproj": "C# (.NET)",
    ".sln": "C# (.NET)",
}

# Ordem de prioridade para desambiguação no *mesmo* diretório
# Se encontrar 'pyproject.toml' E 'requirements.txt' na raiz, o 'pyproject.toml' vence.
LISTA_PRIORIDADE = [
    "pyproject.toml", "Pipfile", "package.json", 
    "requirements.txt", "pom.xml", "build.gradle",
    "go.mod", "Gemfile", ".csproj", ".sln",
]

# Mapeamento de tecnologias para seus arquivos de entry point
ARQUIVOS_PRINCIPAIS = {
    "Python": ["main.py", "app.py", "run.py", "__init__.py"],
    "JavaScript (Node.js)": [
        "index.js", "server.js", "app.js", "main.js",
        "index.ts", "server.ts", "app.ts", "main.ts",
        "main.tsx", "index.tsx"
    ]
}

# Pastas que devem ser ignoradas pela varredura do os.walk()
IGNORAR_DIRETORIOS = {
    '.git', '.github', '.vscode', 'node_modules', 
    '__pycache__', '.DS_Store', 'venv', '.env',
    'docs', 'tests', 'test', 'examples', 'scripts',
    'dist', 'build', 'site',
}

# --- FUNÇÕES ---

def identificar_todas_stacks(repo_path: str) -> list[dict]:
    """
    Varre o repositório inteiro (incluindo subpastas) em busca de stacks.
    Retorna uma lista de todas as stacks encontradas.
    """
    print("Analisando todas as stacks no repositório...")
    stacks_encontradas = []
    
    # Converte o repo_path para um objeto Path para facilitar
    repo_path_obj = Path(repo_path)

    # os.walk() varre o diretório de cima para baixo
    for dirpath, dirnames, filenames in os.walk(repo_path, topdown=True):
        
        # --- Lógica para Ignorar Pastas ---
        # Modifica dirnames IN-PLACE para que os.walk() não entre nelas
        dirnames[:] = [d for d in dirnames if d not in IGNORAR_DIRETORIOS]
        
        # Converte o caminho atual para um objeto Path
        dirpath_obj = Path(dirpath)
        
        # Encontra o melhor arquivo de stack *neste diretório*
        melhor_arquivo_stack_neste_dir = None
        
        arquivos_stack_neste_dir = set(filenames) & set(LISTA_PRIORIDADE)
        
        if not arquivos_stack_neste_dir:
            continue # Nenhuma stack neste diretório, continua para o próximo
            
        # Aplica a lógica de prioridade
        for arquivo_prioritario in LISTA_PRIORIDADE:
            if arquivo_prioritario in arquivos_stack_neste_dir:
                melhor_arquivo_stack_neste_dir = arquivo_prioritario
                break # Achamos o melhor para este diretório
        
        if melhor_arquivo_stack_neste_dir:
            # Calcula o caminho relativo (ex: 'backend' ou '.')
            caminho_relativo = dirpath_obj.relative_to(repo_path_obj)
            
            # Converte para string ('.' para raiz, 'backend' para subpasta)
            caminho_str = str(caminho_relativo)
            
            stack_info = {
                "tecnologia": ARQUIVOS_CHAVE[melhor_arquivo_stack_neste_dir],
                "arquivo": melhor_arquivo_stack_neste_dir,
                "caminho": caminho_str
            }
            
            print(f"Stack encontrada: {stack_info['tecnologia']} em ./{caminho_str}")
            stacks_encontradas.append(stack_info)

    if not stacks_encontradas:
        print("Nenhuma stack de tecnologia conhecida foi encontrada.")
        
    return stacks_encontradas

def extrair_dependencias(repo_path: str, stack_info: dict) -> list:
    """
    Extrai a lista de dependências com base na stack_info (que inclui o caminho).
    """
    arquivo_stack = stack_info['arquivo']
    caminho_stack = stack_info['caminho']
    
    # Monta o caminho completo (ex: /caminho/clone/backend/requirements.txt)
    caminho_arquivo_abs = Path(repo_path) / caminho_stack / arquivo_stack
    
    dependencias = []

    print(f"Extraindo dependências de: {caminho_arquivo_abs.relative_to(repo_path)}")

    try:
        if arquivo_stack == "requirements.txt":
            with open(caminho_arquivo_abs, 'r', encoding='utf-8') as f:
                linhas = f.readlines()
                for linha in linhas:
                    linha = linha.strip()
                    if linha and not linha.startswith(('#', '-')):
                        dependencias.append(linha.split('==')[0].split('>=')[0].strip())

        elif arquivo_stack == "package.json":
            with open(caminho_arquivo_abs, 'r', encoding='utf-8') as f:
                dados = json.load(f)
                deps = dados.get("dependencies", {})
                dev_deps = dados.get("devDependencies", {})
                dependencias = list(deps.keys()) + list(dev_deps.keys())

        elif arquivo_stack == "pyproject.toml":
            with open(caminho_arquivo_abs, 'rb') as f:
                dados = tomli.load(f)
                deps = dados.get("project", {}).get("dependencies", [])
                if not deps:
                    poetry_deps = dados.get("tool", {}).get("poetry", {}).get("dependencies", {})
                    if isinstance(poetry_deps, dict):
                        deps = list(poetry_deps.keys())
                        deps = [d for d in deps if d.lower() != 'python']
                dependencias = [d.split('==')[0].split('>=')[0].split('<=')[0].strip() for d in deps]

        print(f"Encontradas {len(dependencias)} dependências para {caminho_stack}")
        return dependencias
    
    except Exception as e:
        print(f"Erro ao ler {caminho_arquivo_abs}: {e}")
        return []

def mapear_estrutura(repo_path: str) -> list[str]:
    """
    Lista os principais arquivos e diretórios na raiz do repositório.
    (Esta função permanece focada na *raiz* para simplicidade)
    """
    print("Mapeando estrutura de arquivos (raiz)...")
    estrutura = []
    
    try:
        for item in os.listdir(repo_path):
            if item in IGNORAR_DIRETORIOS or item.startswith('.'):
                continue
            
            caminho_item = os.path.join(repo_path, item)
            if os.path.isdir(caminho_item):
                estrutura.append(f"{item}/")
            else:
                if not item.lower().startswith('readme') and \
                   not item.endswith(('.md', '.lock', '.log', '.gitignore')):
                    estrutura.append(item)
                    
        print(f"Estrutura mapeada (raiz): {len(estrutura)} itens principais.")
        return estrutura
    except Exception as e:
        print(f"Erro ao mapear estrutura: {e}")
        return []

def ler_codigo_principal(repo_path: str, stack_info: dict) -> dict | None:
    """
    Procura e lê o conteúdo de arquivos de código-fonte principais
    RELATIVO ao caminho da stack.
    """
    tecnologia = stack_info['tecnologia']
    caminho_stack = stack_info['caminho']
    
    print(f"Procurando código-fonte principal para {tecnologia} em ./{caminho_stack}...")
    
    arquivos_alvo = ARQUIVOS_PRINCIPAIS.get(tecnologia, [])
    if not arquivos_alvo:
        print(f"Nenhum arquivo principal definido para a tecnologia: {tecnologia}")
        return None

    # Pastas de busca RELATIVAS ao caminho da stack
    pastas_busca_relativas = ["", "src", "app", "lib", "cmd"]
    
    # Caminho absoluto da stack (ex: /caminho/clone/backend)
    caminho_stack_abs = Path(repo_path) / caminho_stack
    
    # Adiciona subpastas dinâmicas (ex: backend/app)
    try:
        for item in os.listdir(caminho_stack_abs):
            caminho_item_abs = caminho_stack_abs / item
            if os.path.isdir(caminho_item_abs) and \
               item not in IGNORAR_DIRETORIOS and \
               not item.startswith('.'):
                pastas_busca_relativas.append(item)
    except Exception:
        pass 
    
    pastas_busca_relativas = list(dict.fromkeys(pastas_busca_relativas)) 
    
    for pasta_rel in pastas_busca_relativas:
        for arquivo in arquivos_alvo:
            # Caminho relativo ao repo (ex: backend/app/main.py)
            caminho_relativo_ao_repo = Path(caminho_stack) / pasta_rel / arquivo
            # Caminho absoluto (ex: /caminho/clone/backend/app/main.py)
            caminho_abs = Path(repo_path) / caminho_relativo_ao_repo

            if os.path.exists(caminho_abs):
                print(f"Lendo código principal de: {caminho_relativo_ao_repo}")
                try:
                    with open(caminho_abs, 'r', encoding='utf-8') as f:
                        conteudo = f.read(4000)
                        if len(conteudo) == 4000:
                            conteudo += "\n\n... (arquivo truncado para análise)"
                        
                        return {
                            "arquivo": str(caminho_relativo_ao_repo), 
                            "conteudo": conteudo
                        }
                except Exception as e:
                    print(f"Erro ao ler {caminho_abs}: {e}")

    print(f"Nenhum arquivo de código principal foi encontrado para {tecnologia} em ./{caminho_stack}")
    return None