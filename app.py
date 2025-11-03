import streamlit as st
import cloner
import analyzer
import generator
import time
from pathlib import Path

# --- 1. Configuração da Página ---
st.set_page_config(
    page_title="Readme-AI 🤖",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Readme-AI")
st.caption("Gere READMEs profissionais para seus repositórios GitHub usando IA.")

# --- 2. Interface do Usuário (Inputs) ---
repo_url_input = st.text_input(
    "URL do Repositório GitHub",
    placeholder="Ex: github.com/mauricegss/travel-booking-app" 
)
gerar_btn = st.button("Gerar README")

# Inicializa os estados da sessão
if "readme_gerado" not in st.session_state:
    st.session_state.readme_gerado = ""
if "editor_content" not in st.session_state:
    st.session_state.editor_content = ""

# --- 3. Lógica Principal (Quando o botão é clicado) ---
if gerar_btn:
    
    # Limpa o editor antigo antes de gerar
    st.session_state.editor_content = ""
    st.session_state.readme_gerado = ""
    
    repo_url = repo_url_input.strip()
    if not repo_url:
        st.error("Por favor, insira uma URL do GitHub.")
        st.stop()
    if repo_url.startswith("github.com"):
        repo_url = f"https://{repo_url}"
    elif repo_url.startswith("http://github.com"):
        repo_url = repo_url.replace("http://", "https://")
    if not repo_url.startswith("https://github.com/"):
        st.error("URL inválida. Deve começar com 'https://github.com/...' ou 'github.com/...'")
        st.stop()

    try:
        with st.spinner("Analisando repositório (modo multi-stack)..."):
            
            # --- FASE 1: COLETA (Multi-Stack) ---
            caminho_local = cloner.clonar_repositorio(repo_url)
            if not caminho_local:
                st.error("Falha ao clonar o repositório. Verifique a URL.")
                st.stop() 

            stacks_encontradas = analyzer.identificar_todas_stacks(caminho_local)
            
            if not stacks_encontradas:
                st.error("Nenhuma stack de tecnologia conhecida foi encontrada.")
                st.stop()

            contexto_para_ia = {
                "url_repo": repo_url,
                "estrutura_arquivos_raiz": analyzer.mapear_estrutura(caminho_local),
                "stacks": [] 
            }

            st.write(f"Encontradas {len(stacks_encontradas)} stacks:")
            
            for stack_info in stacks_encontradas:
                stack_caminho = stack_info['caminho']
                st.write(f"- **{stack_info['tecnologia']}** em `./{stack_caminho}`")
                
                deps = analyzer.extrair_dependencias(caminho_local, stack_info)
                codigo = analyzer.ler_codigo_principal(caminho_local, stack_info)
                
                stack_contexto_completo = {**stack_info, "dependencias": deps, "codigo_principal": codigo}
                contexto_para_ia["stacks"].append(stack_contexto_completo)
            
            st.success("Análise multi-stack concluída!")

        # --- FASE 2: GERAÇÃO ---
        with st.spinner("IA está escrevendo o README (modo multi-stack)..."):
            time.sleep(2)
            readme_texto = generator.gerar_readme(contexto_para_ia)
            
            # ATUALIZA OS DOIS ESTADOS: O original e o de edição
            st.session_state.readme_gerado = readme_texto
            st.session_state.editor_content = readme_texto
            
            st.success("README gerado!")
            st.balloons() 

    except Exception as e:
        st.error(f"Ocorreu um erro inesperado: {e}")
        import traceback
        traceback.print_exc()

# --- 4. Exibição dos Resultados (Versão Simples) ---
if st.session_state.editor_content:
    
    st.divider()
    
    col_esquerda, col_direita = st.columns(2)
    
    with col_esquerda:
        st.subheader("Editor Markdown")
        
        # Botão de Download
        st.download_button(
            label="Baixar README.md",
            data=st.session_state.editor_content, # Usa o conteúdo do editor
            file_name="README.md",
            mime="text/markdown",
        )
        
        # Editor de Texto Nativo
        st.text_area(
            "Edite o Markdown aqui. Ctrl+Z funciona.", 
            key="editor_content", # O 'key' ainda faz o live-edit
            height=800,
            label_visibility="collapsed"
        )

    with col_direita:
        st.subheader("Visualização (Preview)")
        
        # O preview lê o estado e atualiza ao vivo
        st.markdown(st.session_state.editor_content)