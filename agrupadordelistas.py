import yt_dlp

# Função para extrair o link de vídeo do YouTube com uma configuração mais direta
def get_video_url(youtube_url):
    # Configuração do yt-dlp para extrair um formato com vídeo e áudio
    ydl_opts = {
        'format': 'best',  # Selecionar o melhor formato (vídeo + áudio)
        'quiet': False,  # Modo verboso para ver detalhes do processo de download
        'verbose': True,  # Ativa o modo de debug para mostrar mais detalhes
        'extractor_args': {
            'youtube': 'formats=mp4'  # Forçar o uso de MP4
        }
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            # Extrair informações do vídeo
            info_dict = ydl.extract_info(youtube_url, download=False)
            video_url = info_dict.get("url", None)  # URL do vídeo
            title = info_dict.get("title", "Unknown Title")  # Título do vídeo
            thumbnail = info_dict.get("thumbnail", "")  # Link da imagem miniatura (para tvg-logo, se necessário)
            
            if video_url is None:
                raise ValueError("Não foi possível extrair o link do vídeo.")
            
            return video_url, title, thumbnail
        
        except Exception as e:
            print(f"Erro ao extrair informações: {e}")
            return None, None, None

# Função para gerar a linha no formato .m3u IPTV
def generate_iptv_link(youtube_url):
    video_url, title, thumbnail = get_video_url(youtube_url)
    
    if video_url and title:
        # Formatação no estilo extinf para IPTV
        iptv_line = f'#EXTINF:-1 tvg-logo="{thumbnail}" group-title="YouTube", {title}\n{video_url}\n'
        return iptv_line
    else:
        return "Erro ao gerar o link IPTV."

# URL do YouTube a ser convertida
youtube_url = "https://www.youtube.com/watch?v=s32n72LfLz4"

# Gerando o link no formato IPTV
iptv_link = generate_iptv_link(youtube_url)

# Salvando o link IPTV no arquivo LISTAYT.m3u
if iptv_link != "Erro ao gerar o link IPTV.":
    with open("LISTAYT.m3u", "a") as file:
        file.write(iptv_link)
    print("Link IPTV adicionado ao arquivo LISTAYT.m3u")
else:
    print(iptv_link)


