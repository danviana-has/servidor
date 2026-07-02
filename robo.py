import os
import sys
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

class GMSpiderCrawler:
    def __init__(self, url_inicial, max_paginas=15):
        self.url_inicial = url_inicial
        self.max_paginas = max_paginas
        self.paginas_visitadas = set()
        self.fila_links = [url_inicial]
        self.dados_indexados = {}

    def _limpar_e_validar_url(self, url, url_base):
        """Resolve links relativos e valida se a estrutura da URL é correta."""
        try:
            url_completa = urljoin(url_base, url)
            parsed = urlparse(url_completa)
            # Filtra apenas protocolos web reais
            if parsed.scheme in ['http', 'https'] and parsed.netloc:
                return url_completa
        except Exception:
            return None
        return None

    async def rastrear_pagina(self, session, url):
        """Baixa o HTML da página, extrai o conteúdo e descobre novos caminhos."""
        if url in self.paginas_visitadas:
            return

        print(f"[CRAWLING] Baixando: {url}")
        self.paginas_visitadas.add(url)

        headers = {'User-Agent': 'GM-Spider-Corporate-Crawler/1.0'}
        try:
            async with session.get(url, headers=headers, timeout=10) as response:
                if response.status != 200:
                    print(f"[AVISO] Código HTTP {response.status} para {url}")
                    return

                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')

                # Captura dados simples para indexação (Título e Texto limpo)
                titulo = soup.title.string.strip() if soup.title else "Sem título"
                self.dados_indexados[url] = titulo

                # Varre todas as tags de link <a> da página
                for tag_a in soup.find_all('a', href=True):
                    novo_link = self._limpar_e_validar_url(tag_a['href'], url)
                    if novo_link and novo_link not in self.paginas_visitadas and novo_link not in self.fila_links:
                        self.fila_links.append(novo_link)

        except Exception as e:
            print(f"[ERRO] Falha ao ler {url}: {e}")

    async def iniciar_varredura(self):
        print("==================================================")
        print("   SISTEMA GM ONLINE - SPIDER CRAWLER ATIVADO     ")
        print("==================================================")
        print(f"[CONFIG] Alvo Inicial: {self.url_inicial}")
        print(f"[CONFIG] Teto Máximo de Páginas: {self.max_paginas}\n")

        async with aiohttp.ClientSession() as session:
            while self.fila_links and len(self.paginas_visitadas) < self.max_paginas:
                # Retira o próximo link da fila (estratégia de Breadth-First Search)
                url_atual = self.fila_links.pop(0)
                await self.rastrear_pagina(session, url_atual)
                # Pequena pausa de engenharia de 0.5s para não sobrecarregar os alvos
                await asyncio.sleep(0.5)

        self._exibir_relatorio_final()

    def _exibir_relatorio_final(self):
        print("\n================ RELATÓRIO DE INDEXAÇÃO ================")
        print(f"Varredura concluída. Total de páginas mineradas: {len(self.paginas_visitadas)}")
        print(f"Links restantes descobertos na fila: {len(self.fila_links)}")
        print("--------------------------------------------------------")
        for idx, (url, titulo) in enumerate(self.dados_indexados.items(), 1):
            print(f"{idx}. [{titulo}] -> {url}")
        print("========================================================\n")

if __name__ == "__main__":
    # Captura os parâmetros inseridos sob demanda na interface do GitHub
    url_alvo = os.environ.get("URL_INICIAL", "https://example.com").strip()
    limite = int(os.environ.get("MAX_PAGINAS", "15"))

    crawler = GMSpiderCrawler(url_inicial=url_alvo, max_paginas=limite)
    
    # Roda o loop assíncrono do robô
    asyncio.run(crawler.iniciar_varredura())
