from yt_dlp import YoutubeDL

# Links fornecidos
youtube_links = [
    "https://www.youtube.com/@recordnews",
    "https://www.youtube.com/@recordnews/live",
    "https://www.youtube.com/watch?v=bZ9m-IWd4lk&pp=ygULcmVjb3JkIG5ld3M%3D",
    "https://www.youtube.com/@NBCNews/live",
    "https://www.youtube.com/@TimesNow/live",
    "https://www.youtube.com/@Firstpost/live"
]

# Opções do yt-dlp para extrair somente o link de streaming (formato m3u8)
ydl_opts = {
    'quiet': True,
    'skip_download': True,
    'force_generic_extractor': False,
    'format': 'best[ext=m3u8]/best',
}

playlist = ['#EXTM3U']

with YoutubeDL(ydl_opts) as ydl:
    for url in youtube_links:
        try:
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'YouTube Live')
            stream_url = info['url']

            playlist.append(f'#EXTINF:-1 tvg-logo="https://i.imgur.com/sG1rF1v.png",{title}')
            playlist.append(stream_url)
        except Exception as e:
            print(f"Erro ao processar {url}: {e}")

# Salvar no arquivo LISTA2.m3u
with open("LISTA2.m3u", "w", encoding='utf-8') as f:
    for line in playlist:
        f.write(f"{line}\n")

print("LISTA2.m3u criada com sucesso!")
