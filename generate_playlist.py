# generate_playlist.py
import requests
import subprocess
import json
import os

# URLs dos arquivos de entrada
CHANNELS_URL = "https://github.com/strikeinthehouse/JCTN/raw/refs/heads/main/channel_argentina.txt"
COOKIES_URL = "https://github.com/Zsobix/YouTube_to_m3u/raw/refs/heads/main/cookies.firefox-private.txt"
OUTPUT_FILENAME = "ARGENTINA.m3u"
COOKIES_FILENAME = "cookies.txt" # Nome do arquivo temporário para os cookies

def fetch_content(url ):
    """Busca o conteúdo de uma URL."""
    print(f"Buscando conteúdo de: {url}")
    response = requests.get(url)
    response.raise_for_status() # Levanta uma exceção para erros HTTP
    return response.text

def main():
    """Função principal para gerar a playlist M3U."""
    print("Iniciando a geração da playlist IPTV...")

    # 1. Buscar a lista de canais
    try:
        channels_content = fetch_content(CHANNELS_URL)
        channel_urls = [line.strip() for line in channels_content.splitlines() if line.strip()]
        if not channel_urls:
            print("Nenhuma URL de canal encontrada no arquivo.")
            return
        print(f"Encontradas {len(channel_urls)} URLs de canais.")
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar a lista de canais: {e}")
        return

    # 2. Buscar e salvar o arquivo de cookies temporariamente
    try:
        cookies_content = fetch_content(COOKIES_URL)
        with open(COOKIES_FILENAME, "w", encoding="utf-8") as f:
            f.write(cookies_content)
        print(f"Cookies salvos em {COOKIES_FILENAME}")
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar o arquivo de cookies: {e}")
        return

    m3u_lines = ["#EXTM3U"]

    print("Processando canais do YouTube com yt-dlp...")
    for url in channel_urls:
        print(f"Processando URL: {url}")
        try:
            # Comando yt-dlp para obter informações do stream sem baixar o vídeo
            # --dump-json: imprime todos os metadados extraídos como JSON
            # --skip-download: não baixa o vídeo
            # --cookies: caminho para o arquivo de cookies
            # --no-warnings: suprime avisos
            # --quiet: suprime mensagens não-erro
            # --force-ipv4: pode ajudar com problemas de conectividade
            # --format best: tenta obter o melhor formato disponível (geralmente o stream direto)
            command = [
                "yt-dlp",
                "--dump-json",
                "--skip-download",
                "--cookies", COOKIES_FILENAME,
                "--no-warnings",
                "--quiet",
                "--force-ipv4",
                url
            ]
            
            process = subprocess.run(command, capture_output=True, text=True, check=True, encoding="utf-8")
            info = json.loads(process.stdout)

            # Extrair informações necessárias para o M3U
            title = info.get("fulltitle") or info.get("title", "Canal Desconhecido")
            stream_url = info.get("url") # Esta é a URL direta do stream

            if stream_url:
                # Sanitizar o título para tvg-id e tvg-name (remover caracteres especiais)
                sanitized_title = "".join(c for c in title if c.isalnum() or c in " -_").strip()
                
                # Tentar obter uma URL de logo/miniatura de alta qualidade
                thumbnails = info.get("thumbnails", [])
                logo_url = ""
                if thumbnails:
                    # Ordenar por largura para pegar a miniatura de maior resolução
                    thumbnails.sort(key=lambda x: x.get("width", 0), reverse=True)
                    logo_url = thumbnails[0].get("url", "")

                m3u_lines.append(f'#EXTINF:-1 tvg-id="{sanitized_title}" tvg-name="{sanitized_title}" tvg-logo="{logo_url}",{title}')
                m3u_lines.append(stream_url)
                print(f"Adicionado: {title}")
            else:
                print(f"Não foi possível obter a URL do stream para: {url}")

        except subprocess.CalledProcessError as e:
            print(f"Erro ao processar {url} com yt-dlp: {e}")
            print(f"Stderr do yt-dlp: {e.stderr}")
        except json.JSONDecodeError:
            print(f"Erro ao decodificar JSON para {url}. Saída do yt-dlp: {process.stdout}")
        except Exception as e:
            print(f"Ocorreu um erro inesperado ao processar {url}: {e}")

    # 3. Escrever o arquivo M3U
    print(f"Escrevendo o arquivo {OUTPUT_FILENAME}...")
    try:
        with open(OUTPUT_FILENAME, "w", encoding="utf-8") as f:
            f.write("\n".join(m3u_lines))
        print(f"Playlist {OUTPUT_FILENAME} gerada com sucesso!")
    except IOError as e:
        print(f"Erro ao escrever o arquivo M3U: {e}")

    # 4. Limpar o arquivo de cookies temporário
    if os.path.exists(COOKIES_FILENAME):
        os.remove(COOKIES_FILENAME)
        print(f"Arquivo de cookies temporário {COOKIES_FILENAME} removido.")
    
    print("Processo concluído.")

if __name__ == "__main__":
    main()

