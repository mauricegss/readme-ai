import os
import json
import tomli  # pip install tomli

# --- CONSTANTES GLOBAIS ---

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

LISTA_PRIORIDADE = [
    "pyproject.toml", "Pipfile", "package.json", 
    "requirements.txt", "pom.xml", "build.gradle",
    "go.mod", "Gemfile", ".csproj", ".sln",
]

# --- MUDANÇA AQUI ---
# Adicionamos os arquivos .ts (TypeScript) e .tsx (React TypeScript)
ARQUIVOS_PRINCIPAIS = {
    "Python": ["main.py", "app.py", "run.py", "__init__.py"],
    "JavaScript (Node.js)": [
        "index.js", "server.js", "app.js", "main.js",
        "index.ts", "server.ts", "app.ts", "main.ts", # <-- Novo
        "main.tsx", "index.tsx" # <-- Novo
    ]
}
# --- FIM DA MUDANÇA ---

IGNORAR_LISTA_GERAL = [
    '.git', '.github', '.vscode', 'node_modules', 
    '__pycache__', '.DS_Store', 'venv', '.env',
    'docs', 'tests', 'test', 'examples', 'scripts',
    'dist', 'build', 'site',
]

# --- FUNÇÕES ---

def identificar_stack(repo_path: str) -> dict:
    """
    Varre a raiz do repositório em busca de arquivos de stack, 
    usando uma ordem de prioridade.
    """
    print(f"Analisando stack em: {repo_path}...")
    
    try:
        files_na_raiz = set(os.listdir(repo_path))
    except Exception as e:
        print(f"Erro ao listar arquivos do repositório: {e}")
        return {"tecnologia": "Desconhecida", "arquivo": None}

    for arquivo_prioritario in LISTA_PRIORIDADE:
        if arquivo_prioritario.startswith('.'):
            for f in files_na_raiz:
                if f.endswith(arquivo_prioritario):
                    tecnologia = ARQUIVOS_CHAVE[arquivo_prioritario]
                    print(f"Tecnologia encontrada (por prioridade): {tecnologia} ({f})")
                    return {"tecnologia": tecnologia, "arquivo": f}
        
        if arquivo_prioritario in files_na_raiz:
            tecnologia = ARQUIVOS_CHAVE[arquivo_prioritario]
            print(f"Tecnologia encontrada (por prioridade): {tecnologia} ({arquivo_prioritario})")
            return {"tecnologia": tecnologia, "arquivo": arquivo_prioritario}

    print("Nenhuma stack de tecnologia conhecida foi encontrada.")
    return {"tecnologia": "Desconhecida", "arquivo": None}

def extrair_dependencias(repo_path: str, arquivo_stack: str) -> list:
    """
    Extrai a lista de dependências com base no arquivo de stack.
    """
    caminho_arquivo = os.path.join(repo_path, arquivo_stack)
    dependencias = []

    print(f"Extraindo dependências de: {arquivo_stack}...")

    try:
        if arquivo_stack == "requirements.txt":
            with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                linhas = f.readlines()
                for linha in linhas:
                    linha = linha.strip()
                    if linha and not linha.startswith(('#', '-')):
                        dependencias.append(linha.split('==')[0].split('>=')[0].strip())

        elif arquivo_stack == "package.json":
            with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                dados = json.load(f)
                deps = dados.get("dependencies", {})
                dev_deps = dados.get("devDependencies", {})
                dependencias = list(deps.keys()) + list(dev_deps.keys())

        elif arquivo_stack == "pyproject.toml":
            with open(caminho_arquivo, 'rb') as f:
                dados = tomli.load(f)
                deps = dados.get("project", {}).get("dependencies", [])
                if not deps:
                    poetry_deps = dados.get("tool", {}).get("poetry", {}).get("dependencies", {})
                    if isinstance(poetry_deps, dict):
                        deps = list(poetry_deps.keys())
                        deps = [d for d in deps if d.lower() != 'python']
                dependencias = [d.split('==')[0].split('>=')[0].split('<=')[0].strip() for d in deps]

        print(f"Encontradas {len(dependencias)} dependências.")
        return dependencias
    
    except Exception as e:
        print(f"Erro ao ler {arquivo_stack}: {e}")
        return []

def mapear_estrutura(repo_path: str) -> list[str]:
    """
    Lista os principais arquivos e diretórios na raiz do repositório.
    """
    print("Mapeando estrutura de arquivos...")
    estrutura = []
    
    try:
        for item in os.listdir(repo_path):
            if item in IGNORAR_LISTA_GERAL:
                continue
            
            caminho_item = os.path.join(repo_path, item)
            if os.path.isdir(caminho_item):
                estrutura.append(f"{item}/")
            else:
                if not item.startswith('.') and \
                   not item.lower().startswith('readme') and \
                   not item.endswith(('.md', '.lock', '.log', '.gitignore')):
                    estrutura.append(item)
                    
        print(f"Estrutura mapeada: {len(estrutura)} itens principais encontrados.")
        return estrutura
    except Exception as e:
        print(f"Erro ao mapear estrutura: {e}")
        return []

def ler_codigo_principal(repo_path: str, tecnologia: str) -> dict | None:
    """
    Procura e lê o conteúdo de arquivos de código-fonte principais.
    """
    print("Procurando código-fonte principal...")
    
    arquivos_alvo = ARQUIVOS_PRINCIPAIS.get(tecnologia, [])
    if not arquivos_alvo:
        print(f"Nenhum arquivo principal definido para a tecnologia: {tecnologia}")
        return None

    pastas_busca = ["", "src", "app", "lib", "cmd"]
    
    try:
        for item in os.listdir(repo_path):
            caminho_item = os.path.join(repo_path, item)
            if os.path.isdir(caminho_item) and \
               item not in IGNORAR_LISTA_GERAL and \
               not item.startswith('.'):
                pastas_busca.append(item)
    except Exception:
        pass 
    
    pastas_busca = list(dict.fromkeys(pastas_busca)) 
    print(f"Pastas de busca de código: {pastas_busca}")

    for pasta in pastas_busca:
        for arquivo in arquivos_alvo:
            caminho_relativo = os.path.join(pasta, arquivo)
            caminho_abs = os.path.join(repo_path, caminho_relativo)

            if os.path.exists(caminho_abs):
                print(f"Lendo código principal de: {caminho_relativo}")
                try:
                    with open(caminho_abs, 'r', encoding='utf-8') as f:
                        conteudo = f.read(4000)
                        if len(conteudo) == 4000:
                            conteudo += "\n\n... (arquivo truncado para análise)"
                        return {"arquivo": caminho_relativo, "conteudo": conteudo}
                except Exception as e:
                    print(f"Erro ao ler {caminho_abs}: {e}")

    print("Nenhum arquivo de código principal foi encontrado.")
    return None