import requests
import subprocess
import json
import os
import re

# URLs dos arquivos de entrada
CHANNELS_URL = "https://github.com/strikeinthehouse/JCTN/raw/refs/heads/main/channel_argentina.txt"
COOKIES_URL = "https://github.com/Zsobix/YouTube_to_m3u/raw/refs/heads/main/cookies.firefox-private.txt"
OUTPUT_FILENAME = "ARGENTINA.m3u"
COOKIES_FILENAME = "cookies.txt"

def fetch_content(url):
    print(f"Buscando conteúdo de: {url}")
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def parse_channel_entry(descriptive_line, youtube_url_line):
    parts = [p.strip() for p in descriptive_line.split('|')]
    channel_name = parts[0] if len(parts) > 0 else "Unknown Channel"
    group_name = parts[1] if len(parts) > 1 else "General"
    logo_url = parts[2] if len(parts) > 2 else ""
    tvg_id = parts[3] if len(parts) > 3 else channel_name

    youtube_url_pattern = re.compile(
        r'https?://(?:www\.)?youtube\.com/(?:channel|user|c|@|watch\?v=)[\w\-/?=&#]+'
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

def resolve_live_redirect(url):
    """
    Resolve a URL de /live para a URL real do vídeo ao vivo, usando scraping HTML e yt-dlp como fallback.
    """
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        resp = requests.get(url, headers=headers, timeout=10)
        match = re.search(r'"canonicalUrl":"(/watch\?v=[\w-]+)"', resp.text)
        if match:
            resolved = f"https://www.youtube.com{match.group(1)}"
            print(f"[✓] HTML-resolved: {url} -> {resolved}")
            return resolved
    except Exception as e:
        print(f"[✗] Erro HTML-resolve: {url} -> {e}")

    # Fallback: usar yt-dlp diretamente
    try:
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
        process = subprocess.run(command, capture_output=True, text=True, timeout=15)

        if process.returncode == 0 and process.stdout.strip():
            info = json.loads(process.stdout)
            if 'url' in info:
                print(f"[✓] yt-dlp-resolved direto de: {url}")
                return url
            else:
                print(f"[✗] yt-dlp executado, mas sem campo 'url'.")
        else:
            print(f"[✗] yt-dlp falhou ({process.returncode}) para {url}")
    except Exception as e:
        print(f"[✗] yt-dlp erro: {e}")

    print(f"[Live] Nenhuma URL de stream detectada para: {url}")
    return None

def main():
    print("Iniciando a geração da playlist IPTV...")

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
                    print(f"Linha descritiva sem URL subsequente: {line}")
                    i += 1
            else:
                print(f"Linha ignorada (formato inesperado): {line}")
                i += 1

        if not parsed_channels:
            print("Nenhum canal válido encontrado.")
            return
        print(f"Total de canais para processar: {len(parsed_channels)}")
    except requests.exceptions.RequestException as e:
        print(f"Erro ao baixar canais: {e}")
        return

    try:
        cookies_content = fetch_content(COOKIES_URL)
        with open(COOKIES_FILENAME, "w", encoding="utf-8") as f:
            f.write(cookies_content)
        print(f"Cookies salvos em: {COOKIES_FILENAME}")
    except requests.exceptions.RequestException as e:
        print(f"Erro ao baixar cookies: {e}")
        return

    m3u_lines = ["#EXTM3U"]

    for channel_info in parsed_channels:
        original_url = channel_info["youtube_url"]
        if "/live" in original_url:
            resolved_url = resolve_live_redirect(original_url)
            if not resolved_url:
                print(f"[Live] Nenhum vídeo ao vivo detectado em {original_url}")
                continue
            url = resolved_url
        else:
            url = original_url

        print(f"▶ Processando canal: {channel_info['name']} ({url})")

        try:
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
            process = subprocess.run(command, capture_output=True, text=True, timeout=20)

            if process.returncode != 0 or not process.stdout.strip():
                print(f"[yt-dlp ERRO] {channel_info['name']} ({url}):\n{process.stderr.strip()}")
                continue

            try:
                info = json.loads(process.stdout)
            except json.JSONDecodeError:
                print(f"[JSON ERRO] Canal: {channel_info['name']}. Saída inválida:\n{process.stdout}")
                continue

            stream_url = info.get("url")
            if stream_url:
                tvg_id = "".join(c for c in channel_info["tvg_id"] if c.isalnum() or c in " -_").strip()
                tvg_name = "".join(c for c in channel_info["name"] if c.isalnum() or c in " -_").strip()
                logo = channel_info["logo"]
                if not logo:
                    thumbs = info.get("thumbnails", [])
                    if thumbs:
                        thumbs.sort(key=lambda x: x.get("width", 0), reverse=True)
                        logo = thumbs[0].get("url", "")
                m3u_lines.append(f'#EXTINF:-1 tvg-id="{tvg_id}" tvg-name="{tvg_name}" tvg-logo="{logo}" group-title="{channel_info["group"]}",{channel_info["name"]}')
                m3u_lines.append(stream_url)
                print(f"[✓] Adicionado: {channel_info['name']}")
            else:
                print(f"[✗] Sem URL de stream para: {channel_info['name']}")
        except Exception as e:
            print(f"[Erro inesperado] {channel_info['name']}: {e}")

    print(f"📝 Escrevendo arquivo M3U: {OUTPUT_FILENAME}")
    try:
        with open(OUTPUT_FILENAME, "w", encoding="utf-8") as f:
            f.write("\n".join(m3u_lines))
        print(f"✅ Playlist gerada: {OUTPUT_FILENAME}")
    except IOError as e:
        print(f"Erro ao salvar M3U: {e}")

    if os.path.exists(COOKIES_FILENAME):
        os.remove(COOKIES_FILENAME)
        print(f"🧹 Cookies temporários removidos.")

    print("✅ Processo finalizado.")

if __name__ == "__main__":
    main()
