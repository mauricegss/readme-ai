import argparse
import os
import cloner          
import analyzer        
import generator

NOME_ARQUIVO_SAIDA = "README_NEW.md"

def run_analysis(repo_url: str):
    
    print(f"--- Iniciando análise para: {repo_url} ---")
    
    # --- FASE 1: COLETA DE DADOS ---
    
    # 1. Clonar
    caminho_local = cloner.clonar_repositorio(repo_url)
    
    if not caminho_local:
        print("Falha no clone. Abortando.")
        return

    # 2. Analisar Stack
    stack_info = analyzer.identificar_stack(caminho_local)
    
    contexto_para_ia = {
        "url_repo": repo_url,
        "tecnologia": stack_info['tecnologia'],
        "arquivo_stack": stack_info['arquivo'],
        "dependencias": [],
        "estrutura_arquivos": [],
        "codigo_principal": None 
    }

    # 3. Extrair Dependências
    if stack_info['arquivo']:
        deps = analyzer.extrair_dependencias(caminho_local, stack_info['arquivo'])
        contexto_para_ia["dependencias"] = deps
            
    # 4. Mapear Estrutura
    estrutura = analyzer.mapear_estrutura(caminho_local)
    contexto_para_ia["estrutura_arquivos"] = estrutura
    
    # 5. Ler Código Principal
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
        print(f"  Código Principal: Lido de '{contexto_para_ia['codigo_principal']['arquivo']}'")
    else:
        print("  Código Principal: Não encontrado")
    print("-" * 30)
    
    # --- FASE 2: GERAÇÃO COM IA ---
    # (Este é o novo bloco de código)
    
    print("\n--- Iniciando Geração com IA ---")
    # 6. Chamar o gerador
    readme_texto = generator.gerar_readme(contexto_para_ia)
    print("IA concluiu a geração.")
    
    # 7. Salvar o resultado
    try:
        with open(NOME_ARQUIVO_SAIDA, "w", encoding="utf-8") as f:
            f.write(readme_texto)
        print(f"\n🎉 Sucesso! Seu README foi salvo em: {NOME_ARQUIVO_SAIDA}")
    except Exception as e:
        print(f"\nErro ao salvar o arquivo README: {e}")
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="README-AI: Gerador de README com IA.")
    parser.add_argument("url", type=str, help="A URL (https) do repositório GitHub a ser analisado.")
    args = parser.parse_args()
    
    run_analysis(args.url)