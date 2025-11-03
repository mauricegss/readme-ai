import os
import json
import tomli  # pip install tomli

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

# Mapeamento de tecnologias para seus arquivos de entry point mais comuns
ARQUIVOS_PRINCIPAIS = {
    "Python": ["main.py", "app.py", "run.py", "__init__.py"],
    "JavaScript (Node.js)": ["index.js", "server.js", "app.js", "main.js"]
    # Podemos adicionar mais para Java, Go, etc. depois
}

# Pastas comuns onde o código-fonte principal pode estar
PASTAS_BUSCA = ["", "src", "app", "lib", "cmd"] # "" significa a raiz

def identificar_stack(repo_path: str) -> dict:
    """
    Varre a raiz do repositório em busca de arquivos de stack conhecidos.
    """
    print(f"Analisando stack em: {repo_path}...")
    tecnologias_encontradas = {}

    for nome_arquivo in os.listdir(repo_path):
        if nome_arquivo in ARQUIVOS_CHAVE:
            tecnologia = ARQUIVOS_CHAVE[nome_arquivo]
            tecnologias_encontradas[tecnologia] = nome_arquivo
        
        if nome_arquivo.endswith((".csproj", ".sln")):
            tecnologia = ARQUIVOS_CHAVE[".csproj"]
            tecnologias_encontradas[tecnologia] = nome_arquivo

    if not tecnologias_encontradas:
        print("Nenhuma stack de tecnologia conhecida foi encontrada.")
        return {"tecnologia": "Desconhecida", "arquivo": None}

    primeira_tec = list(tecnologias_encontradas.keys())[0]
    primeiro_arq = tecnologias_encontradas[primeira_tec]
    
    return {"tecnologia": primeira_tec, "arquivo": primeiro_arq}

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
    IGNORAR_LISTA = [
        '.git', '.github', '.vscode', 'node_modules', 
        '__pycache__', '.DS_Store', 'venv', '.env',
    ]
    estrutura = []
    
    try:
        for item in os.listdir(repo_path):
            if item in IGNORAR_LISTA:
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

    for pasta in PASTAS_BUSCA:
        for arquivo in arquivos_alvo:
            # Cria o caminho relativo (ex: 'src/main.py')
            caminho_relativo = os.path.join(pasta, arquivo)
            # Cria o caminho absoluto para verificar se existe
            caminho_abs = os.path.join(repo_path, caminho_relativo)

            if os.path.exists(caminho_abs):
                print(f"Lendo código principal de: {caminho_relativo}")
                try:
                    with open(caminho_abs, 'r', encoding='utf-8') as f:
                        # Lê os primeiros 4000 caracteres (~1000 tokens)
                        # Isso evita exceder o limite de contexto da IA
                        conteudo = f.read(4000)
                        
                        # Adiciona um aviso se o arquivo for maior
                        if len(conteudo) == 4000:
                            conteudo += "\n\n... (arquivo truncado para análise)"
                            
                        return {"arquivo": caminho_relativo, "conteudo": conteudo}
                except Exception as e:
                    print(f"Erro ao ler {caminho_abs}: {e}")
                    # Continua tentando outros arquivos se este falhar a leitura

    print("Nenhum arquivo de código principal (main.py, index.js, etc.) foi encontrado.")
    return None