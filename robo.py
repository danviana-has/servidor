import os
import sys
import math
import re

DATASET = {
    "doc1": "Engenharia e Automação diretamente de Recife. Sistemas de tecnologia operativa corporativos.",
    "doc2": "Desenvolvimento de inteligência artificial estreita baseada em machine learning e redes neurais.",
    "doc3": "Como configurar subdomínios e servidores locais no Registro br usando CNAME e chaves SSH.",
    "doc4": "Treinamento de Small Language Models e arquiteturas GPT2 com datasets customizados do zero.",
    "doc5": "Sistema de gestão de dados e logs corporativos rodando em servidores Linux Ubuntu estáveis."
}

STOPWORDS = {"o", "a", "os", "as", "de", "do", "da", "em", "para", "com", "e", "um", "uma", "que", "no", "na"}

def tokenizar(texto):
    texto_limpo = re.sub(r'[^\w\s]', '', texto.lower())
    palavras = texto_limpo.split()
    return [p for p in palavras if p not in STOPWORDS]

def calcular_tf(termo, documento_tokenizado):
    if not documento_tokenizado:
        return 0
    return documento_tokenizado.count(termo) / len(documento_tokenizado)

def calcular_idf(termo, todos_documentos_tokenizados):
    quantidade_docs_com_termo = sum(1 for doc in todos_documentos_tokenizados if termo in doc)
    if quantidade_docs_com_termo == 0:
        return 0
    return math.log(len(todos_documentos_tokenizados) / quantidade_docs_com_termo)

def pesquisar(termo_busca, base_dados):
    termos_busca = tokenizar(termo_busca)
    if not termos_busca:
        return []
    docs_tokenizados = {id_doc: tokenizar(conteudo) for id_doc, conteudo in base_dados.items()}
    lista_docs_tokenizados = list(docs_tokenizados.values())
    scores_documentos = {}
    for id_doc, doc_tokens in docs_tokenizados.items():
        score_total = 0
        for termo in termos_busca:
            tf = calcular_tf(termo, doc_tokens)
            idf = calcular_idf(termo, lista_docs_tokenizados)
            score_total += tf * idf
        if score_total > 0:
            scores_documentos[id_doc] = score_total
    return sorted(scores_documentos.items(), key=lambda x: x[1], reverse=True)

def executar_esteira_busca():
    print("==================================================")
    print("   SISTEMA GM ONLINE - INICIALIZANDO ROBÔ DE BUSCA ")
    print("==================================================")
    
    # Captura o termo digitado sob demanda na interface do GitHub
    termo_pesquisa = os.environ.get("TERMO_PESQUISA", "").strip()
    
    if not termo_pesquisa:
        print("[ERRO] Nenhum termo foi fornecido na requisição sob demanda.")
        sys.exit(1)
        
    print(f"[ENGINE] Termo sob demanda recebido: '{termo_pesquisa}'")
    print(f"[DATASET] Total de documentos indexados: {len(DATASET)}")
    
    resultados = pesquisar(termo_pesquisa, DATASET)
    
    print("\n---------------- REQUISIÇÃO CONCLUÍDA ----------------")
    if resultados:
        print(f"Encontrado(s) {len(resultados)} resultado(s):\n")
        for rank, (id_doc, score) in enumerate(resultados, 1):
            print(f"{rank}º Lugar: Documento [{id_doc}] (Score: {score:.4f})")
            print(f"   -> \"{DATASET[id_doc]}\"\n")
    else:
        print(f"[AVISO] Nenhum documento correspondeu à busca por '{termo_pesquisa}'.")
    print("------------------------------------------------------")
    print("[SUCESSO] Varredura sob demanda concluída com sucesso.")
    print("==================================================")

if __name__ == "__main__":
    executar_esteira_busca()
