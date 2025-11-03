import os
import google.generativeai as genai
from dotenv import load_dotenv

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

def _construir_prompt(contexto: dict) -> str:
    """
    Monta o "Prompt Mestre" que será enviado para a IA.
    """
    print("Construindo prompt para a IA...")
    
    deps_str = ", ".join(contexto['dependencias'][:20])
    if len(contexto['dependencias']) > 20:
        deps_str += ", ... (e mais)"
        
    estrutura_str = "\n".join([f"- `{item}`" for item in contexto['estrutura_arquivos']])

    # --- LÓGICA DE INSTALAÇÃO (A GRANDE MUDANÇA) ---
    arquivo_stack = contexto.get('arquivo_stack')
    comando_instalacao_sugerido = "" # Padrão

    if arquivo_stack == "package.json":
        comando_instalacao_sugerido = "`npm install` (ou `yarn install`)"
    elif arquivo_stack == "pyproject.toml":
        # Instala o pacote definido no pyproject.toml
        comando_instalacao_sugerido = "`pip install .`"
    elif arquivo_stack == "requirements.txt":
        comando_instalacao_sugerido = f"`pip install -r {arquivo_stack}`"
    elif arquivo_stack == "pom.xml":
        comando_instalacao_sugerido = "`mvn install`"
    elif arquivo_stack == "build.gradle":
        comando_instalacao_sugerido = "`./gradlew build`"
    # --- FIM DA LÓGICA DE INSTALAÇÃO ---

    # Início do Prompt (A Persona e a Tarefa)
    prompt_lines = [
        "Você é um Engenheiro de Software Sênior e um excelente escritor técnico.",
        "Sua tarefa é gerar um README.md profissional para um novo projeto no GitHub, "
        "com base nas informações do repositório que eu coletei.",
        
        "\n**REGRAS (Foco no Mercado de Trabalho):**",
        "1.  **Linguagem:** Seja direto, claro e profissional (focado em recrutadores).",
        "2.  **Formato:** Use Markdown completo (títulos, listas, blocos de código).",
        "3.  **Descrição:** O foco deve ser 'O que este projeto faz?' e 'Como usá-lo?'.",
        "4.  **Não invente:** Baseie-se **estritamente** nas informações fornecidas.",
        "5.  **SEM PREÂMBULO:** Comece a resposta **diretamente** com o Título do README.",
        
        "\n---",
        "**Informações Coletadas do Repositório:**",
        f"- **URL:** {contexto['url_repo']}",
        f"- **Tecnologia Principal:** {contexto['tecnologia']}",
        f"- **Arquivo de Dependências:** `{arquivo_stack}`",
    ]

    # Adiciona o comando de instalação APENAS se tivermos um
    if comando_instalacao_sugerido:
        prompt_lines.append(f"- **Comando de Instalação Sugerido:** {comando_instalacao_sugerido}")

    if deps_str:
        prompt_lines.append(f"- **Principais Dependências:** {deps_str}")
        
    if estrutura_str:
        prompt_lines.append(f"- **Estrutura Principal do Projeto:**\n{estrutura_str}")

    if contexto.get('codigo_principal'):
        arquivo_lido = contexto['codigo_principal']['arquivo']
        conteudo_codigo = contexto['codigo_principal']['conteudo']
        prompt_lines.append(
            f"\n- **Amostra do Código-Fonte Principal (`{arquivo_lido}`):**\n"
            f"```\n{conteudo_codigo}\n```"
        )

    prompt_lines.extend([
        "\n---",
        "**Sua Tarefa (Gerar o README):**",
        "Agora, gere o arquivo README.md completo. O README deve conter:",
        "1.  **Título do Projeto**",
        "2.  **Descrição Curta**",
        "3.  **Features** (Liste 3-5 funcionalidades principais baseadas no código).",
        "4.  **Stack de Tecnologias** (Liste as 'Principais Dependências').",
        "5.  **Instalação** (Um bloco de código para clonar e instalar. **Use o 'Comando de Instalação Sugerido'** que forneci acima. NÃO use `pip install -r requirements.txt` a menos que seja o comando sugerido.)", # <-- A INSTRUÇÃO FINAL
        "6.  **Como Usar** (Um exemplo simples de como rodar o projeto).",
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
    
    print("Gerando README... (Isso pode levar alguns segundos)")
    
    try:
        response = model.generate_content(prompt_mestre)
        
        readme_texto = response.text.strip().removeprefix("```markdown").removesuffix("```").strip()
        
        return readme_texto
    
    except Exception as e:
        print(f"Erro ao gerar conteúdo pela IA: {e}")
        return f"# Erro ao gerar README\n\nInfelizmente, a API do Gemini falhou.\nDetalhe: {e}"