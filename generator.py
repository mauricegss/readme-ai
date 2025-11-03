import os
import google.generativeai as genai
from dotenv import load_dotenv
from pathlib import Path # Importa o pathlib

# Carrega as variáveis de ambiente (o arquivo .env)
load_dotenv()

def _configurar_ia():
    """
    Configura e retorna o modelo generativo do Gemini.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "Erro: GOOGLE_API_KEY não encontrada no arquivo .env. "
            "Por favor, crie um .env e adicione sua chave."
        )
        
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        return model
    except Exception as e:
        print(f"Erro ao configurar a API do Gemini: {e}")
        return None

def _get_comando_instalacao(stack_info: dict) -> str:
    """
    Helper para determinar o comando de instalação correto baseado na stack.
    """
    arquivo_stack = stack_info.get('arquivo')
    caminho_stack = stack_info.get('caminho', '.')
    
    if arquivo_stack == "package.json":
        return "`npm install`"
    elif arquivo_stack == "pyproject.toml":
        # Se estiver numa subpasta, 'pip install ./subpasta'
        return f"`pip install ./{caminho_stack}`"
    elif arquivo_stack == "requirements.txt":
        # Constrói o caminho relativo para o arquivo
        caminho_req = Path(caminho_stack) / arquivo_stack
        return f"`pip install -r {caminho_req.as_posix()}`" # as_posix() usa /
    elif arquivo_stack == "pom.xml":
        return "`mvn install`"
    elif arquivo_stack == "build.gradle":
        return "`./gradlew build`"
    return "Comando de instalação não determinado."


def _construir_prompt(contexto: dict) -> str:
    """
    Monta o "Prompt Mestre" (multi-stack) que será enviado para a IA.
    """
    print("Construindo prompt multi-stack para a IA...")
    
    # --- Persona e Regras (Sem mudança) ---
    prompt_lines = [
        "Você é um Engenheiro de Software Sênior e um excelente escritor técnico.",
        "Sua tarefa é gerar um README.md profissional para um novo projeto no GitHub, "
        "com base nas informações do repositório que eu coletei.",
        
        "\n**REGRAS (Foco no Mercado de Trabalho):**",
        "1.  **Linguagem:** Seja direto, claro e profissional (focado em recrutadores).",
        "2.  **Formato:** Use Markdown completo.",
        "3.  **Não invente:** Baseie-se **estritamente** nas informações fornecidas.",
        "4.  **SEM PREÂMBULO:** Comece a resposta **diretamente** com o Título do README.",
        
        "\n---",
        "**Informações Coletadas (Geral):**",
        f"- **URL:** {contexto['url_repo']}",
        f"- **Estrutura da Raiz:** {', '.join(contexto['estrutura_arquivos_raiz'])}",
        f"- **Stacks Encontradas:** {len(contexto['stacks'])} (Este é um projeto multi-stack, "
        "provavelmente com frontend e backend.)"
    ]

    # --- LÓGICA MULTI-STACK (A GRANDE MUDANÇA) ---
    # Itera por cada stack (ex: Frontend, Backend)
    for i, stack in enumerate(contexto['stacks'], 1):
        
        caminho_stack = stack['caminho']
        if caminho_stack == ".":
            nome_stack_display = "Raiz (Frontend)" # Suposição
        else:
            nome_stack_display = f"{caminho_stack.capitalize()} (Backend)" # Suposição

        prompt_lines.append(f"\n--- Detalhes da Stack {i} ({nome_stack_display}) ---")
        prompt_lines.append(f"- **Tecnologia:** {stack['tecnologia']}")
        
        # 1. Comando de Instalação
        comando_instalacao = _get_comando_instalacao(stack)
        prompt_lines.append(f"- **Comando de Instalação Sugerido:** {comando_instalacao}")

        # 2. Dependências
        if stack['dependencias']:
            deps_str = ", ".join(stack['dependencias'][:15]) # Limita a 15 por stack
            if len(stack['dependencias']) > 15:
                deps_str += ", ... (e mais)"
            prompt_lines.append(f"- **Principais Dependências:** {deps_str}")
        
        # 3. Código Principal
        if stack.get('codigo_principal'):
            arquivo_lido = stack['codigo_principal']['arquivo']
            conteudo_codigo = stack['codigo_principal']['conteudo']
            prompt_lines.append(
                f"\n- **Amostra do Código-Fonte (`{arquivo_lido}`):**\n"
                f"```\n{conteudo_codigo}\n```"
            )

    # --- Tarefa Final (Instruções Multi-Stack) ---
    prompt_lines.extend([
        "\n---",
        "**Sua Tarefa (Gerar o README):**",
        "Agora, gere o arquivo README.md completo. O README deve conter:",
        "1.  **Título do Projeto**",
        "2.  **Descrição Curta** (Descreva o projeto como um todo, mencionando o frontend e backend).",
        "3.  **Features** (Liste 3-5 funcionalidades principais baseadas no código).",
        "4.  **Stack de Tecnologias** (Crie subseções, ex: `### Frontend` e `### Backend`, "
        "e liste as 'Principais Dependências' de cada stack).",
        "5.  **Instalação** (Crie subseções, ex: `### Configurando o Frontend` e `### Configurando o Backend`. "
        "Use o 'Comando de Instalação Sugerido' para cada stack.)",
        "6.  **Como Usar** (Crie subseções, ex: `### Rodando o Frontend` e `### Rodando o Backend`. "
        "Tente inferir os comandos, como `npm run dev` ou `uvicorn app.main:api`).",
    ])
    
    return "\n".join(prompt_lines)

def gerar_readme(contexto: dict) -> str:
    """
    Função principal: configura a IA, constrói o prompt e gera o README.
    """
    model = _configurar_ia()
    if not model:
        return "Erro: Não foi possível configurar o modelo de IA."

    prompt_mestre = _construir_prompt(contexto)
    
    # Descomente para depurar o prompt gigante que estamos enviando
    # print("\n--- PROMPT ENVIADO À IA ---")
    # print(prompt_mestre)
    # print("----------------------------\n")
    
    print("Gerando README... (Isso pode levar alguns segundos)")
    
    try:
        response = model.generate_content(prompt_mestre)
        
        readme_texto = response.text.strip().removeprefix("```markdown").removesuffix("```").strip()
        
        return readme_texto
    
    except Exception as e:
        print(f"Erro ao gerar conteúdo pela IA: {e}")
        return f"# Erro ao gerar README\n\nInfelizmente, a API do Gemini falhou.\nDetalhe: {e}"