import requests
import subprocess
import json
import os
import re

# URLs dos arquivos de entrada
CHANNELS_URL = "https://github.com/strikeinthehouse/JCTN/raw/refs/heads/main/channel_argentina.txt"
COOKIES_URL = "https://github.com/Zsobix/YouTube_to_m3u/raw/refs/heads/main/cookies.firefox-private.txt"
OUTPUT_FILENAME = "ARGENTINA.m3u"
COOKIES_FILENAME = "cookies.txt"  # Nome do arquivo temporário para os cookies

def fetch_content(url):
    """Busca o conteúdo de uma URL."""
    print(f"Buscando conteúdo de: {url}")
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def parse_channel_entry(descriptive_line, youtube_url_line):
    """
    Analisa a linha descritiva e a linha da URL do YouTube.
    Esperado:
        <nome do canal> | <grupo> | <logo> | <tvg-id>
        https://www.youtube.com/...
    """
    parts = [p.strip() for p in descriptive_line.split('|')]

    channel_name = parts[0] if len(parts) > 0 else "Unknown Channel"
    group_name = parts[1] if len(parts) > 1 else "General"
    logo_url = parts[2] if len(parts) > 2 else ""
    tvg_id = parts[3] if len(parts) > 3 else channel_name

    # Regex corrigida
    youtube_url_pattern = re.compile(
        r'https?://(?:www\.)?(youtube\.com/(?:channel|user|c)/[a-zA-Z0-9_-]+/live|youtube\.com/watch\?v=[\w-]+|youtu\.be/[\w-]+)'
    )
    if not youtube_url_pattern.match(youtube_url_line):
        print(f"A URL do YouTube não é válida ou não corresponde ao padrão esperado: {youtube_url_line}")
        return None

    return {
        "name": channel_name,
        "group": group_name,
        "logo": logo_url,
        "tvg_id": tvg_id,
        "youtube_url": youtube_url_line
    }

def main():
    """Função principal para gerar a playlist M3U."""
    print("Iniciando a geração da playlist IPTV...")

    # 1. Buscar a lista de canais
    try:
        channels_content = fetch_content(CHANNELS_URL)
        raw_channel_lines = [line.strip() for line in channels_content.splitlines() if line.strip()]

        parsed_channels = []
        i = 0
        while i < len(raw_channel_lines):
            line = raw_channel_lines[i]
            if line.startswith("~~"):
                i += 1
                continue

            if '|' in line:
                if i + 1 < len(raw_channel_lines):
                    youtube_url_line = raw_channel_lines[i + 1]
                    channel_info = parse_channel_entry(line, youtube_url_line)
                    if channel_info:
                        parsed_channels.append(channel_info)
                    i += 2
                else:
                    print(f"Linha descritiva sem URL do YouTube subsequente: {line}")
                    i += 1
            else:
                print(f"Linha ignorada (formato inesperado ou URL standalone sem descrição): {line}")
                i += 1

        if not parsed_channels:
            print("Nenhuma entrada de canal válida encontrada no arquivo.")
            return
        print(f"Encontradas {len(parsed_channels)} entradas de canais válidas para processar.")
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
    for channel_info in parsed_channels:
        url = channel_info["youtube_url"]
        print(f"Processando URL: {url} para canal: {channel_info['name']}")
        try:
            command = [
                "yt-dlp",
                "--dump-json",
                "--skip-download",
                "--cookies", COOKIES_FILENAME,
                "--no-warnings",
                "--quiet",
                "--force-ipv4",
                "--live-from-start",
                url
            ]

            process = subprocess.run(command, capture_output=True, text=True, check=True, encoding="utf-8")
            info = json.loads(process.stdout)

            title = channel_info["name"]
            stream_url = info.get("url")

            if stream_url:
                sanitized_tvg_id = "".join(c for c in channel_info["tvg_id"] if c.isalnum() or c in " -_").strip()
                sanitized_tvg_name = "".join(c for c in channel_info["name"] if c.isalnum() or c in " -_").strip()

                logo_to_use = channel_info["logo"]
                if not logo_to_use:
                    thumbnails = info.get("thumbnails", [])
                    if thumbnails:
                        thumbnails.sort(key=lambda x: x.get("width", 0), reverse=True)
                        logo_to_use = thumbnails[0].get("url", "")

                m3u_lines.append(f'#EXTINF:-1 tvg-id="{sanitized_tvg_id}" tvg-name="{sanitized_tvg_name}" tvg-logo="{logo_to_use}" group-title="{channel_info["group"]}",{title}')
                m3u_lines.append(stream_url)
                print(f"Adicionado: {title}")
            else:
                print(f"Não foi possível obter a URL do stream para: {url}")

        except subprocess.CalledProcessError as e:
            print(f"Erro ao processar {url} com yt-dlp: {e}")
            print(f"Stderr do yt-dlp: {e.stderr}")
            if "The channel is not currently live" in e.stderr or "This channel does not have a Live tab" in e.stderr:
                print(f"Canal {channel_info['name']} ({url}) não está ao vivo ou não tem aba ao vivo. Ignorando.")
            else:
                print(f"Erro inesperado do yt-dlp para {channel_info['name']} ({url}). Verifique o log.")
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
