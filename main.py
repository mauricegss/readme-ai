import argparse
import os
import cloner          # Importa nosso módulo
import analyzer        # Importa nosso módulo

def run_analysis(repo_url: str):
    """
    Orquestra o processo completo: clonar, analisar stack e dependências.
    """
    print(f"--- Iniciando análise para: {repo_url} ---")
    
    # 1. Clonar
    caminho_local = cloner.clonar_repositorio(repo_url)
    
    if not caminho_local:
        print("Falha no clone. Abortando.")
        return

    # 2. Analisar Stack
    stack_info = analyzer.identificar_stack(caminho_local)
    
    # Este dicionário irá guardar todo o contexto para a IA
    contexto_para_ia = {
        "url_repo": repo_url,
        "tecnologia": stack_info['tecnologia'],
        "arquivo_stack": stack_info['arquivo'],
        "dependencias": [],
        "estrutura_arquivos": [],
        "codigo_principal": None  # Novo campo
    }

    # 3. Extrair Dependências
    if stack_info['arquivo']:
        deps = analyzer.extrair_dependencias(caminho_local, stack_info['arquivo'])
        contexto_para_ia["dependencias"] = deps
            
    # 4. Mapear Estrutura
    estrutura = analyzer.mapear_estrutura(caminho_local)
    contexto_para_ia["estrutura_arquivos"] = estrutura
    
    # 5. Ler Código Principal (NOVO PASSO)
    if stack_info['tecnologia'] != "Desconhecida":
        codigo_info = analyzer.ler_codigo_principal(caminho_local, stack_info['tecnologia'])
        if codigo_info:
            contexto_para_ia["codigo_principal"] = codigo_info
    
    print("\n--- Análise Concluída ---")
    
    # Imprime um resumo limpo do contexto coletado
    print("\nContexto final coletado:")
    print("-" * 30)
    print(f"  URL: {contexto_para_ia['url_repo']}")
    print(f"  Tecnologia: {contexto_para_ia['tecnologia']}")
    print(f"  Dependências: {len(contexto_para_ia['dependencias'])} encontradas")
    print(f"  Estrutura: {len(contexto_para_ia['estrutura_arquivos'])} itens encontrados")
    
    if contexto_para_ia.get('codigo_principal'):
        arquivo_lido = contexto_para_ia['codigo_principal']['arquivo']
        print(f"  Código Principal: Lido de '{arquivo_lido}'")
    else:
        print("  Código Principal: Não encontrado")
    print("-" * 30)
    
    # (No futuro, este dicionário 'contexto_para_ia' será enviado para o Gemini)
    # print(contexto_para_ia) # Descomente se quiser ver o dicionário completo


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="README-AI: Analisador de Repositórios GitHub.")
    parser.add_argument("url", type=str, help="A URL (https) do repositório GitHub a ser analisado.")
    args = parser.parse_args()
    
    run_analysis(args.url)