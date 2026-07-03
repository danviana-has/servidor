import os
import sys
import asyncio
import json
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
        try:
            url_completa = urljoin(url_base, url)
            parsed = urlparse(url_completa)
            if parsed.scheme in ['http', 'https'] and parsed.netloc:
                return url_completa
        except Exception:
            return None
        return None

    async def rastrear_pagina(self, session, url):
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

                titulo = soup.title.string.strip() if soup.title else "Sem título"
                # Salva o título associado à URL
                self.dados_indexados[url] = titulo

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
                url_atual = self.fila_links.pop(0)
                await self.rastrear_pagina(session, url_atual)
                await asyncio.sleep(0.5) # Pausa polida de requisições

        self._salvar_dados_em_disco()

    def _salvar_dados_em_disco(self):
        print("\n[MIGRATION] Compilando base de dados indexada para o Frontend...")
        try:
            # Exporta os resultados direto para o arquivo que a página web lê
            with open('resultados.json', 'w', encoding='utf-8') as f:
                json.dump(self.dados_indexados, f, indent=4, ensure_ascii=False)
            print("[SUCESSO] Arquivo resultados.json gerado com sucesso.")
        except Exception as e:
            print(f"[ERRO] Falha ao salvar arquivo em disco: {e}")
        print("========================================================\n")

if __name__ == "__main__":
    url_alvo = os.environ.get("URL_INICIAL", "https://example.com").strip()
    limite = int(os.environ.get("MAX_PAGINAS", "15"))

    crawler = GMSpiderCrawler(url_inicial=url_alvo, max_paginas=limite)
    asyncio.run(crawler.iniciar_varredura())
