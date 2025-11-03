import streamlit as st
import cloner
import analyzer
import generator
import time

# --- 1. Configuração da Página ---
st.set_page_config(
    page_title="Readme-AI 🤖",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Readme-AI")
st.caption("Gere READMEs profissionais para seus repositórios GitHub usando IA.")

# --- 2. Interface do Usuário (Inputs) ---
# Renomeei para 'repo_url_input' para diferenciar da URL limpa
repo_url_input = st.text_input(
    "URL do Repositório GitHub",
    placeholder="Ex: github.com/fastapi/fastapi" # Placeholder atualizado
)
gerar_btn = st.button("Gerar README")

if "readme_gerado" not in st.session_state:
    st.session_state.readme_gerado = ""

# --- 3. Lógica Principal (Quando o botão é clicado) ---
if gerar_btn:
    
    # --- NOVA LÓGICA DE VALIDAÇÃO DE URL ---
    repo_url = repo_url_input.strip() # Remove espaços
    
    if not repo_url:
        st.error("Por favor, insira uma URL do GitHub.")
        st.stop() # Para a execução

    # Se começar só com 'github.com', adiciona 'https://'
    if repo_url.startswith("github.com"):
        repo_url = f"https://{repo_url}"
    
    # Se for 'http', força 'https'
    elif repo_url.startswith("http://github.com"):
        repo_url = repo_url.replace("http://", "https://")

    # Se, depois das correções, ainda não for uma URL válida, mostra erro
    if not repo_url.startswith("https://github.com/"):
        st.error("URL inválida. Deve começar com 'https://github.com/...' ou 'github.com/...'")
        st.stop() # Para a execução
    # --- FIM DA NOVA LÓGICA ---

    try:
        # Mostra um "loading"
        with st.spinner("Analisando repositório... Isso pode levar um minuto..."):
            
            # --- FASE 1: COLETA (Usa a 'repo_url' limpa) ---
            caminho_local = cloner.clonar_repositorio(repo_url)
            if not caminho_local:
                st.error("Falha ao clonar o repositório. Verifique se a URL está correta e o repositório é público.")
                st.stop() 

            stack_info = analyzer.identificar_stack(caminho_local)
            
            contexto_para_ia = {
                "url_repo": repo_url, # Passa a URL limpa
                "tecnologia": stack_info['tecnologia'],
                "arquivo_stack": stack_info['arquivo'],
                "dependencias": [],
                "estrutura_arquivos": [],
                "codigo_principal": None 
            }

            if stack_info['arquivo']:
                contexto_para_ia["dependencias"] = analyzer.extrair_dependencias(caminho_local, stack_info['arquivo'])
            
            contexto_para_ia["estrutura_arquivos"] = analyzer.mapear_estrutura(caminho_local)
            
            if stack_info['tecnologia'] != "Desconhecida":
                contexto_para_ia["codigo_principal"] = analyzer.ler_codigo_principal(caminho_local, stack_info['tecnologia'])
            
            st.success(f"Análise concluída! Stack: {stack_info['tecnologia']}")

        # --- FASE 2: GERAÇÃO ---
        with st.spinner("IA está escrevendo o README..."):
            time.sleep(2)
            readme_texto = generator.gerar_readme(contexto_para_ia)
            st.session_state.readme_gerado = readme_texto
            st.success("README gerado!")

    except Exception as e:
        st.error(f"Ocorreu um erro inesperado: {e}")

# --- 4. Exibição dos Resultados ---
if st.session_state.readme_gerado:
    
    st.divider()
    
    col_esquerda, col_direita = st.columns(2)
    
    with col_esquerda:
        st.subheader("Código Markdown (MD)")
        st.text_area(
            "Markdown", 
            st.session_state.readme_gerado, 
            height=800,
            label_visibility="collapsed"
        )

    with col_direita:
        st.subheader("Visualização (Preview)")
        st.markdown(st.session_state.readme_gerado)