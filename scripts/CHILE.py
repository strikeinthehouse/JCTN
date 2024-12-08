import requests
import logging
from logging.handlers import RotatingFileHandler
import json
import re

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

log_file = "log.txt"
file_handler = RotatingFileHandler(log_file)
file_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

# URL do arquivo .txt
CHANNEL_FILE_URL = "https://github.com/strikeinthehouse/JCTN/raw/refs/heads/main/channel_chile.txt"

# Funções utilitárias
def download_channel_file(url):
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        return response.text.splitlines()  # Retorna o conteúdo do arquivo como uma lista de linhas
    except requests.exceptions.RequestException as err:
        logger.error("Erro ao baixar o arquivo: %s", err)
        sys.exit("Erro ao baixar o arquivo .txt")



def extract_youtube_id(line):
    # Regex pattern to extract YouTube video IDs
    video_match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", line)
    if video_match:
        return video_match.group(1)
    
    # Log a warning if no valid YouTube ID is found
    logger.warning("No valid YouTube ID found in: %s", line)
    return None



# Baixa e processa o arquivo de canais
lines = download_channel_file(CHANNEL_FILE_URL)

channel_data = []
channel_data_json = []

banner = r'''
#EXTM3U x-tvg-url="https://raw.githubusercontent.com/mudstein/XML/main/TIZENiptvchile.xml"
#EXTM3U url-tvg="https://www.bevy.be/bevyfiles/chile.xml"

#EXTINF:-1 tvg-id="TVN.cl" tvg-logo="http://i.imgur.com/f41IHoB.png" group-title="CHILE",TVN
https://marine2.miplay.cl/tvnchile/playlist.m3u8

#EXTINF:-1 tvg-id="TVN.cl" tvg-logo="http://i.imgur.com/f41IHoB.png" group-title="CHILE",TVChile
http://45.181.123.233:8000/play/a0qg

#EXTINF:-1 tvg-id="NTV.cl" tvg-logo="https://www.lyngsat-logo.com/logo/tv/nn/ntv-cl.png" group-title="CHILE",NTV
https://marine2.miplay.cl/ntv/playlist.m3u8

#EXTINF:-1 tvg-id="LaRed.cl" tvg-logo="https://www.lyngsat-logo.com/logo/tv/ll/la-red-cl.png" group-title="CHILE",La Red HD
https://unlimited2-cl-isp.dps.live/lared/lared.smil/playlist.m3u8
#EXTINF:-1 tvg-id="LaRed.cl" tvg-logo="https://www.lyngsat-logo.com/logo/tv/ll/la-red-cl.png" group-title="CHILE",La Red
https://marine2.miplay.cl/lared/playlist.m3u8

#EXTINF:-1 tvg-id="UCVTV.cl" tvg-logo="https://pbs.twimg.com/profile_images/1283856690648096770/L-vGlyO4_400x400.png" group-title="CHILE",UCV HD
https://unlimited2-cl-isp.dps.live/ucvtv2/ucvtv2.smil/playlist.m3u8
#EXTINF:-1 tvg-id="UCVTV.cl" tvg-logo="https://pbs.twimg.com/profile_images/1283856690648096770/L-vGlyO4_400x400.png" group-title="CHILE",UCV
https://marine2.miplay.cl/ucv3/playlist.m3u8

#EXTINF:-1 tvg-id="tvmas.cl" tvg-logo="https://img.soy-chile.cl/Fotos/2018/10/29/file_20181029173540.jpg" group-title="CHILE",TV+
https://marine2.miplay.cl/tvmas/playlist.m3u8

#EXTINF:-1 tvg-id="24Horas.cl" tvg-logo="https://www.lyngsat-logo.com/logo/tv/tt/tvn_24_horas_cl.png" group-title="CHILE",24 Horas
https://marine2.miplay.cl/24horas/playlist.m3u8

#EXTINF:-1 tvg-id="Mega.cl" tvg-logo="https://www.lyngsat-logo.com/logo/tv/mm/mega-cl.png" group-title="CHILE",Mega
https://marine2.miplay.cl/megacl/playlist.m3u8
#EXTINF:-1 tvg-id="Mega.cl" tvg-logo="https://www.lyngsat-logo.com/logo/tv/mm/mega-cl.png" group-title="CHILE",Mega SD
http://45.181.123.233:8000/play/a0qh
#EXTINF:-1 tvg-id="Mega.cl" tvg-logo="https://www.lyngsat-logo.com/logo/tv/mm/mega-cl.png" group-title="CHILE",Mega HD
http://45.181.123.233:8000/play/a0is

#EXTINF:-1 tvg-id="ChileVision.cl" tvg-logo="https://brandemia.org/sites/default/files/inline/images/logo_chilevision.jpg" group-title="CHILE",CHV
https://marine2.miplay.cl/chvchile/playlist.m3u8
#EXTINF:-1 tvg-id="ChileVision.cl" tvg-logo="https://brandemia.org/sites/default/files/inline/images/logo_chilevision.jpg" group-title="CHILE",CHV SD
http://45.181.123.233:8000/play/a0qi
#EXTINF:-1 tvg-id="ChileVision.cl" tvg-logo="https://brandemia.org/sites/default/files/inline/images/logo_chilevision.jpg" group-title="CHILE",CHV HD
http://45.181.123.233:8000/play/a0kl

#EXTINF:-1 tvg-id="Canal13.cl" tvg-logo="http://i.imgur.com/HqKYZvm.png" group-title="CHILE",Canal 13
https://marine2.miplay.cl/c13/playlist.m3u8
#EXTINF:-1 tvg-id="Canal13.cl" tvg-logo="http://i.imgur.com/HqKYZvm.png" group-title="CHILE",Canal 13 SD
http://45.181.123.233:8000/play/a0qj
#EXTINF:-1 tvg-id="Canal13.cl" tvg-logo="http://i.imgur.com/HqKYZvm.png" group-title="CHILE",Canal 13 HD
http://45.181.123.233:8000/play/a0lh

#EXTINF:-1 tvg-id="13C.cl" tvg-logo="http://i.imgur.com/HqKYZvm.png" group-title="CHILE",T13
https://marine2.miplay.cl/t13/playlist.m3u8

#EXTINF:-1 tvg-id="ZonaLatina.cl" tvg-logo="https://zonalatinatv.com/wp-content/uploads/2023/04/ZL-Lateral-NO-OFICIAL.png" group-title="CHILE",Zona Latina
http://45.181.123.233:8000/play/a15n
#EXTINF:-1 tvg-id="ViaX.cl" tvg-logo="https://cdn.mitvstatic.com/channels/cl_via-x_m.png" group-title="CHILE",ViaX HD
http://45.181.123.233:8000/play/a0oh

#EXTINF:-1 tvg-id="TVU.cl" tvg-logo="https://upload.wikimedia.org/wikipedia/commons/thumb/0/0f/Logo_tvu.png/1024px-Logo_tvu.png" group-title="CHILE",TVU
https://unlimited1-cl-isp.dps.live/tvu/tvu.smil/playlist.m3u8

#EXTINF:-1 tvg-id="UChile.cl" tvg-logo="https://www.uchile.cl/.imaging/default/dam/imagenes/Uchile/imagenes-noticias/172128_1_u-chile-tv-logo-1200px-fondo-negro_S/jcr:content.png" group-title="CHILE",U Chile TV (geo)
https://unlimited1-cl-isp.dps.live/uchiletv/uchiletv.smil/uchiletv/livestream0/chunks.m3u8?nimblesessionid=9302469

#EXTINF:-1 tvg-id="TVR.cl" tvg-logo="https://www.televisiongratis.tv/components/com_televisiongratis/images/televisin-regional-de-chile-1483.png" group-title="CHILE",TVR HD
https://pantera1-100gb-cl-movistar.dps.live/tvr/tvr.smil/playlist.m3u8
#EXTINF:-1 tvg-id="TVR.cl" tvg-logo="https://www.televisiongratis.tv/components/com_televisiongratis/images/televisin-regional-de-chile-1483.png" group-title="CHILE",TVR
https://marine2.miplay.cl/tvr/playlist.m3u8

#EXTINF:-1 tvg-id="STGOTV.cl" tvg-logo="https://pbs.twimg.com/media/DmuwuKqXsAUevyn.jpg" group-title="CHILE",STGO TV
https://stv4.janus.cl/playlist/stream.m3u8?s=lq&t=3&id=m30upk7m&q=&d=w

#EXTINF:-1 tvg-id="CNNChile.cl" tvg-logo="http://i.imgur.com/Dd9PMar.png" group-title="CHILE",CNN Chile
http://45.181.123.233:8000/play/a15o

#EXTINF:-1 tvg-id="TVN Chile" tvg-name="TVN Chile" tvg-logo="https://imagenes.gatotv.com/logos/canales/oscuros/tvn_chile.png" group-title="CHILE",TVN | Chile


#EXTINF:-1 tvg-id="Solo Stand Up" tvg-name="Solo Stand Up" tvg-logo="https://lh3.googleusercontent.com/-vs6bQTy4Dns/X30TqJ-CdrI/AAAAAAAA6M4/WUtqB3d4eiEp7oHE44DkOhh5V0NNTDMSACK8BGAsYHg/s0/2020-10-06.png" group-title="CHILE",Solo Stand Up | Chile


#EXTINF:-1 tvg-id="13 de Chile" tvg-name="13 de Chile" tvg-logo="https://imagenes.gatotv.com/logos/canales/oscuros/13_de_chile.png" group-title="CHILE",Canal 13 | Chile

#EXTINF:-1 tvg-id="Chilevision" tvg-name="Chilevision" tvg-logo="https://imagenes.gatotv.com/logos/canales/oscuros/chilevision.png" group-title="CHILE",Chilevision | Chile


#EXTINF:-1 tvg-id="TVN Chile" tvg-name="TVN Chile" tvg-logo="https://imagenes.gatotv.com/logos/canales/oscuros/tvn_chile.png" group-title="CHILE",TVN | Chile


#EXTINF:-1 tvg-id="ETC TV" tvg-name="ETC TV" tvg-logo="https://i.imgur.com/QVC28lh.png" group-title="CHILE",ETC TV | Chile


#EXTINF:-1 tvg-id="13 de Chile" tvg-name="13 de Chile" tvg-logo="https://imagenes.gatotv.com/logos/canales/oscuros/13_de_chile.png" group-title="CHILE",Canal 13 | Chile

#EXTINF:-1 tvg-id="Chilevision" tvg-name="Chilevision" tvg-logo="https://imagenes.gatotv.com/logos/canales/oscuros/chilevision.png" group-title="CHILE",Chilevision | Chile


#EXTINF:-1 tvg-logo="http://www.radiosplay.com/logos/3/2/6/7/32679.png" group-title="CHILE",Radio Portal FoxMix Chile
https://sonic.portalfoxmix.cl/8002/stream

#EXTINF:-1 tvg-id="ETC TV" tvg-name="ETC TV" tvg-logo="https://i.imgur.com/QVC28lh.png" group-title="INFANTILES",ETC TV | Chile
http://177.128.115.10:8000/play/a0a6

#EXTINF:-1 tvg-logo="https://i.imgur.com/i1wxNqd.png" group-title="MUSICA",TVR | Chile
https://unlimited2-cl.dps.live/tvr/tvr.smil/playlist.m3u8

#EXTINF:-1 tvg-id="Retro Plus TV" tvg-name="Retro Plus TV" tvg-logo="https://lh3.googleusercontent.com/-obky0xopJjA/XrIZZ5C1quI/AAAAAAAA0bo/OBDSs6fw5zEa1eQJrv7j7IkMtaoQFcBJgCK8BGAsYHg/s0/2020-05-05.png" group-title="MUSICA",Retro Plus TV | Chile
https://59f1cbe63db89.streamlock.net:1443/retroplustv/_definst_/retroplustv/playlist.m3u8

#EXTINF:-1 tvg-logo="https://lh3.googleusercontent.com/-obky0xopJjA/XrIZZ5C1quI/AAAAAAAA0bo/OBDSs6fw5zEa1eQJrv7j7IkMtaoQFcBJgCK8BGAsYHg/s0/2020-05-05.png" group-title="MUSICA",RETRO PLUS 2 TV | Chile
https://59f1cbe63db89.streamlock.net:1443/retroplussenal2/_definst_/retroplussenal2/playlist.m3u8

#EXTINF:-1 tvg-id="" tvg-name="" tvg-logo="https://planetatv.online/wp-content/uploads/2022/02/LOGOPNG.png" group-title="MUSICA",PlanetaTV 90s | Chile
https://mediacpstreamchile.com:1936/8102/8102/chunklist_w1159975531.m3u8

#EXTINF:-1 tvg-id="" tvg-name="" tvg-logo="https://planetatv.cl/2022/wp-content/uploads/2022/09/perfil-facebook.png" group-title="MUSICA",PlanetaTV Music | Chile
https://tls-cl.cdnz.cl/music/live/chunklist_w260426131.m3u8

#EXTINF:-1 tvg-id="" tvg-name="" tvg-logo="https://planetatv.cl/2022/wp-content/uploads/2022/09/perfil-facebook.png" group-title="MUSICA",PlanetaTV Music | Chile
https://scl.edge.grupoz.cl/music/live/playlist.m3u8

#EXTINF:-1 tvg-logo="http://i.imgur.com/63s1k43.png" group-title="MUSICA",Portal FoxMix Tv HD | Chile
http://149.56.17.92:1935/portalfoxmix/_definst_/portalfoxmix/playlist.m3u8

#EXTINF:-1 tvg-logo="https://mundodelamusicachile.cl/wp-content/uploads/2021/05/Sin-ti%CC%81tulo-1.png" group-title="MUSICA",Mundo de la Musica TV | Chile
https://tv.streamingchilenos.com:1936/8034/8034/playlist.m3u8

#EXTINF:-1 tvg-logo="https://lh3.googleusercontent.com/-mOgOT3QHduQ/XxcP0slOnxI/AAAAAAAA3KI/s0jjr5v_hUsKOLXgjwJM3uZ88HJDjR7bQCK8BGAsYHg/s0/2020-07-21.png" group-title="MUSICA",Mix 24-7 | Chile
http://159.69.56.148:25461/live/M3UMix247/89ph5uifoi/1.m3u8

#EXTINF:-1 tvg-logo="http://djlonchoradio.com/wp-content/uploads/2018/09/tv-300x300.jpg" group-title="MUSICA",Dj Loncho Radio Tv | Chile
https://srv2.zcast.com.br/djlonchotv/djlonchotv/playlist.m3u8

#EXTINF:-1 tvg-id="Magazine" tvg-name="Magazine" tvg-logo="https://lh3.googleusercontent.com/-VQiXnvScrdo/X9kBIY6eCeI/AAAAAAAA8Pk/RqwvHCzyqT07Izb5NG9RLx7serX6u18JQCK8BGAsYHg/s0/2020-12-15.png" group-title="MODA",Chic Magazine | Chile
https://paneltv.online:1936/8056/8056/playlist.m3u8

#EXTINF:-1 tvg-id="" tvg-logo="https://i2.paste.pics/20f4f7278dc7ab118f657d93da43474d.png" group-title="FAMILIARES",EvaStream TV | Chile
https://mediacpstreamchile.com:1936/evavision/evavision/playlist.m3u8

#EXTINF:-1 tvg-id="Teletrak" tvg-name="Teletrak" tvg-logo="https://i.imgur.com/iHhc7PK.png" group-title="DEPORTES",Teletrak | Chile
http://unlimited6-cl.dps.live/sportinghd/sportinghd.smil/playlist.m3u8

#EXTINF:-1 tvg-id="Mundo Auto Tv" tvg-name="Mundo Auto Tv" tvg-logo="https://i.imgur.com/GxKchKG.png" group-title="DEPORTES",Mundo Auto TV | Chile
https://5c64355d4b57c.streamlock.net:1936/mundoautotv/mundoautotv/chunklist_w1460343737.m3u8

#EXTINF:-1 tvg-id="Programacion Local" tvg-name="Programacion Local" tvg-logo="https://i2.paste.pics/90f2f266cb4f68333119a06b99d65d10.png" group-title="FAMILIARES",Retro Play TV | Chile
https://v4.tustreaming.cl/retroplaytv/index.m3u8

#EXTINF:-1 tvg-id="Retro Plus TV" tvg-name="Retro Plus TV" tvg-logo="https://i2.paste.pics/d35132c511d1ef461b3e4af7db9e0b5f.png" group-title="FAMILIARES",Retro Plus TV | Chile
https://59f1cbe63db89.streamlock.net:1443/retroplussenal3/_definst_/retroplussenal3/playlist.m3u8

#EXTINF:-1 tvg-logo="https://lh3.googleusercontent.com/-JXvAv4nY-K8/XnTXs1clGLI/AAAAAAAAxCw/ntmMdCu1UQEXtAHPFrYyW8I1l5bRGiAWwCK8BGAsYHg/s0/2020-03-20.png" group-title="FAMILIARES",La Popular TV | Chile
https://5d1ca66d2d698.streamlock.net:1936/8076/8076/playlist.m3u8

#EXTINF:-1 tvg-id="Mega" tvg-name="Mega" tvg-logo="https://lh3.googleusercontent.com/-xqKe__ypgDY/XnzFn9NLnbI/AAAAAAAAxMU/2Wj9IOC1LaQxtJGRzcVOTrQWxP9z3RgPwCK8BGAsYHg/s0/2020-03-26.png" group-title="FAMILIARES",Mega | Chile
https://unlimited1-cl-isp.dps.live/mega/mega.smil/mega/livestream0/chunks.m3u8

#EXTINF:-1 tvg-id="Iquique Tv" tvg-name="Iquique Tv" tvg-logo="https://iquiquetv.cl/wp-content/uploads/2020/05/iquiqueTV_logo_202005_272x90.png" group-title="FAMILIARES",Iquique Tv | Chile
https://marine2.miplay.cl/arcatel/iquiquetv720/tracks-v1a1/mono.m3u8

#EXTINF:-1 tvg-logo="https://lh3.googleusercontent.com/-JXvAv4nY-K8/XnTXs1clGLI/AAAAAAAAxCw/ntmMdCu1UQEXtAHPFrYyW8I1l5bRGiAWwCK8BGAsYHg/s0/2020-03-20.png" group-title="FAMILIARES",La Popular TV | Chile
https://tv.streaming-chile.com:1936/lapopulartv/lapopulartv/playlist.m3u8

#EXTINF:-1 tvg-id="Buin Somos Todos" tvg-name="Buin Somos Todos" tvg-logo="https://i.ytimg.com/vi/k_Q7-gqkfAo/maxresdefault.jpg" group-title="FAMILIARES",Buin Somos Todos | Chile
https://bst.buin.cl/0.m3u8



#EXTINF:-1 tvg-id="74 de Chile" tvg-name="74 de Chile" tvg-logo="https://i.imgur.com/AgUx16i.png" group-title="FAMILIARES",Canal 74 TV | Chile
https://stmv1.zcasthn.com.br/canal74hd/canal74hd/playlist.m3u8

#EXTINF:-1 tvg-id="74 de Chile" tvg-name="74 de Chile" tvg-logo="https://i.imgur.com/AgUx16i.png" group-title="FAMILIARES",Canal 74 TV op | Chile
https://stmv1.zcastbr.com/canal74hd/canal74hd/playlist.m3u8

#EXTINF:-1 tvg-id="Canal Punto 99" tvg-name="Canal Punto 99" tvg-logo="https://i.imgur.com/55Juhdx.jpg" group-title="FAMILIARES",Canal Punto 99 | Chile
https://stmv1.zcasthn.com.br/juanantunez/juanantunez/playlist.m3u8

#EXTINF:-1 tvg-id="Caracola TV" tvg-name="Caracola TV" tvg-logo="https://www.caracolatv.cl/wp-content/uploads/2021/12/logo-296x300.jpg" group-title="FAMILIARES",Caracola TV | Chile
https://wifispeed.trapemn.tv:1936/comunales/caracola-tv/playlist.m3u8
#EXTINF:-1 tvg-id="Infantil TV" tvg-name="Infantil TV" tvg-logo="https://gebelutv.files.wordpress.com/2014/11/unnamed.png" group-title="INFANTILES",Cloud Server Kids Tv | Chile
https://videostreaming.cloudserverlatam.com/kids/kids/chunklist_w780109170.m3u8

#EXTINF:-1 tvg-id="NTV" tvg-name="NTV" tvg-logo="https://i.imgur.com/w1jK0n7.png" group-title="INFANTILES",NTV | Chile
https://marine2.miplay.cl/ntv/playlist.m3u8

#EXTINF:-1 tvg-id="Kids 90" tvg-name="Kids 90" tvg-logo="https://i.imgur.com/A5U3jer.png" group-title="INFANTILES",Kids 90 | Chile
https://videostreaming.cloudserverlatam.com/Kids90/Kids90/playlist.m3u8

#EXTINF:-1 tvg-id="PlanetaTV Kids" tvg-name="PlanetaTV Kids" tvg-logo="https://i.imgur.com/ZN3ry2f.png" group-title="INFANTILES",PlanetaTV Kids | Chile
https://tls-cl.cdnz.cl/planetatvkids/live/chunklist_w1953958808.m3u8

#EXTINF:-1 tvg-id="PlanetaTV Kids" tvg-name="PlanetaTV Kids" tvg-logo="https://i.imgur.com/ZN3ry2f.png" group-title="INFANTILES",PlanetaTV Kids | Chile
https://scl.edge.grupoz.cl/planetatvkids/live/playlist.m3u8

#KODIPROP:inputstream.adaptive.license_type=org.w3.clearkey
#KODIPROP:inputstream.adaptive.license_key=c5d0d76e24844235988f9265619e5fec:446b71a6deb806c6f129e25de999d07c
#EXTINF:-1 tvg-chno="812" tvg-id="TVChile.cl" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/TVNI.png?raw=true" group-title="CHILE", TV Chile
https://chromecast.cvattv.com.ar/live/c6eds/Tv_Chile/SA_Live_dash_enc_2A/Tv_Chile.mpd

#EXTINF:0 player-buffer="30" tvg-logo="https://i.ibb.co/QP2CjJG/CNN-Chile.png" group-title="CHILE",CNN Chile
http://newultra.xyz:8080/34tehu87se24ma97/m37me65wu93m/57269

#EXTINF:0 player-buffer="30" tvg-logo="https://i.ibb.co/QP2CjJG/CNN-Chile.png" group-title="CHILE",CNN Chile
http://fortv.cc:8080/DeishouV2573/120712/164892


#EXTINF:-1 tvg-id="mega-hd.cl" tvg-name="MEGA HD" tvg-logo="http://yourlogourl.com/mega-hd.png" group-title="CHILE",MEGA HD
http://cord-cutter.net:8080/live/j3McKd/673709/164883.m3u8
#EXTINF:-1 tvg-id="chilevision-hd.cl" tvg-name="CHILEVISION HD" tvg-logo="http://yourlogourl.com/chilevision-hd.png" group-title="CHILE",CHILEVISION HD
http://cord-cutter.net:8080/live/j3McKd/673709/164884.m3u8
#EXTINF:-1 tvg-id="13i.cl" tvg-name="13I" tvg-logo="http://yourlogourl.com/13i.png" group-title="CHILE",13I
http://cord-cutter.net:8080/live/j3McKd/673709/164885.m3u8
#EXTINF:-1 tvg-id="tvn-chile-hd.cl" tvg-name="TVN CHILE HD" tvg-logo="http://yourlogourl.com/tvn-chile-hd.png" group-title="CHILE",TVN CHILE HD
http://cord-cutter.net:8080/live/j3McKd/673709/164888.m3u8
#EXTINF:-1 tvg-id="cnn-chile-hd.cl" tvg-name="CNN CHILE HD" tvg-logo="http://yourlogourl.com/cnn-chile-hd.png" group-title="CHILE",CNN CHILE HD
http://cord-cutter.net:8080/live/j3McKd/673709/164892.m3u8


#EXTINF:-1,  tvg-name="TVN"  tvg-logo="https://1000marcas.net/wp-content/uploads/2022/12/TVN-Chile-Logo-thmb.png" group-title="CHILE",TVN (CHILE)
https://streamer01.digital.com.bo/2ap337/__cl/cg:sworigin2/__c/TVNCHILE/__op/hls-default/__f/index.m3u8
#EXTINF:-1 tvg-id="Tvn" tvg-logo="https://raw.githubusercontent.com/HERBERTM3/Logos/main/tvn.jpg" group-title="CHILE",TVN (VPN) ACHO
https://cvthmk.000webhostapp.com/tvn.php
https://cvthmk.000webhostapp.com/tvnhd.php
https://tvn--24df53d9e0.repl.co/
https://mdstrm.com/live-stream-playlist-v/57a498c4d7b86d600e5461cb.m3u8?access_token=FmNotzoOXDoZWaHupBbLurn8Ijrjq1C1gAOHRTaBvcLr3K6T00meQLanhm4zCOLXtFHlVUR8wAc
#pagina web:https://www.tvn.cl/en-vivo
#token:https://live.tvn.cl
#herramienta para ver el token:https://codebeautify.org/source-code-viewer



#EXTINF:-1 xui-id="125" tvg-id="CHVAAH" tvg-name="Chilevisión" tvg-logo="https://normielista.cl:443/images/0GV_IuQaPDLyYaZp9L5H2CMg2ozhFk3H2yn6s37Y4X_0xaKkuCYoGKPL_-hbrOy6TaaN6EC_eDJyzmXiMgM4Gg.png" group-title="CHILE",Chilevisión
https://normielista.cl:443/play/0Bu2UVekNecKvoeYhzqb9VTVNpb0Ty6APnEPt0h4YBNaTAhytRXgJHnEzvivdqpz/ts

#EXTINF:-1,  tvg-name="CHILEVISIONCONTIGO"  tvg-logo="https://media.cnnchile.com/sites/2/2021/04/22-11-2019-Chilevision.jpg" group-title="CHILE",CANAL 13
http://daleplay.club:8080/listatbsdaleplay22/listatbsdaleplaypararepetircanales/156122

#EXTINF:-1 tvg-id="Chilevision" tvg-logo="https://raw.githubusercontent.com/HERBERTM3/Logos/main/chv.jpg" group-title="CHILE",Chilevision (VPN)
https://cvthmk.000webhostapp.com/chvhd.php
https://chilevision--92fbc459f4.repl.co/
https://chv-m3u.chorroaeboy.repl.co/
https://mdstrm.com/live-stream-playlist-v/5c928b7f6d6f41084bdae898.m3u8?access_token=SX4xOAnbdD56p36OoVCv45HGPNgEMrMV9D8icJTVvzlCYKzRCZQtxOJ2kcrWje3YgXPvTmZttHX
#pagina web:https://www.chilevision.cl/senal-online
#pagina token:https://www.chilevision.cl/ms_player_src_01/live_1/5c928b7f6d6f41084bdae898/1681435537.js


#EXTINF:-1 xui-id="128" tvg-id="MEGA" tvg-name="Mega" tvg-logo="https://normielista.cl:443/images/0GV_IuQaPDLyYaZp9L5H2CMg2ozhFk3H2yn6s37Y4X-phSNZlGbmiki05OMDvwB3.png" group-title="CHILE",Mega
https://unlimited1-cl-isp.dps.live/mega/mega.smil/playlist.m3u8

#EXTINF:-1 tvg-id="Ntv" tvg-logo="https://raw.githubusercontent.com/HERBERTM3/Logos/main/ntv.jpg" group-title="CHILE",NTV (VPN)
https://mdstrm.com/live-stream-playlist/5aaabe9e2c56420918184c6d.m3u8
#pagina web:https://mdstrm.com/live-stream/5aaabe9e2c56420918184c6d
#Sin token
#herramienta para ver el token:https://codebeautify.org/source-code-viewer


#EXTINF:-1 tvg-id="24 Play" tvg-logo="https://raw.githubusercontent.com/HERBERTM3/Logos/main/24 play.jpg" group-title="Televisión",24 Play
https://mdstrm.com/live-stream-playlist/57d1a22064f5d85712b20dab.m3u8
#pagina web:https://mdstrm.com/live-stream/57d1a22064f5d85712b20dab
#Sin token
#herramienta para ver el token:https://codebeautify.org/source-code-viewer

#EXTINF:-1 xui-id="123" tvg-id="C13STGO" tvg-name="Canal 13" tvg-logo="https://normielista.cl:443/images/0GV_IuQaPDLyYaZp9L5H2CMg2ozhFk3H2yn6s37Y4X9UAj6nCi9ytepPsaKrCz8k.png" group-title="CHILE",Canal 13
https://ythls.onrender.com/channel/UCsRnhjcUCR78Q3Ud6OXCTNg.m3u8


#EXTINF:-1 tvg-id="La Red HD" tvg-logo="https://raw.githubusercontent.com/HERBERTM3/Logos/main/lared.jpg" group-title="CHILE",La Red
https://unlimited1-cl-isp.dps.live/lared/lared.smil/playlist.m3u8?PlaylistM3UCL
https://d2ab26kihxq8p0.cloudfront.net/hls/live.m3u8
#pagina web:https://www.lared.cl/senal-online
#Playe:https://rudo.video/live/lared
https://unlimited1-cl-isp.dps.live/lared/lared.smil/playlist.m3u8


#EXTINF:-1 tvg-id="1437" tvg-name="TVN3" tvg-logo="https://i2.paste.pics/2ba64b67051e159ff48060da1a687fd0.png" group-title="CHILE",TVN3
https://mdstrm.com/live-stream-playlist/5653641561b4eba30a7e4929.m3u8?PlaylistM3UCL

#EXTINF:-1 xui-id="129" tvg-id="TVMAS" tvg-name="TV+" tvg-logo="https://normielista.cl:443/images/HM3xx55KZnCUdlPuNC1k2GwUee_HeV47TzX8gNpnfyDYJ6p7Kx-jfO4caNakoUhllyFnR5yWYSnRv4lnoRMwPA.png" ggroup-title="CHILE",TV+
https://normielista.cl:443/play/0Bu2UVekNecKvoeYhzqb9VTVNpb0Ty6APnEPt0h4YBN-QdWvfzXcmwCqNlLe77eJ/ts

#EXTINF:-1 xui-id="151" tvg-id="TDCLVHD" tvg-name="Discovery Channel" tvg-logo="https://normielista.cl:443/images/HM3xx55KZnCUdlPuNC1k2CQmSialG6ZFMmnpVE7A3yqON5YO_qN3tthlYeEufoUOqJP914nRtNv6GRAI4Jfu5A.png" ggroup-title="CHILE",Discovery Channel
https://normielista.cl:443/play/0Bu2UVekNecKvoeYhzqb9U3VvRIXL7HaW-FbHrzwKyPiuztYG1AN5PMmsGlPN9Ry/ts
#EXTINF:-1 xui-id="180" tvg-id="NGCARGA" tvg-name="National Geographic Channel" tvg-logo="https://normielista.cl:443/images/HM3xx55KZnCUdlPuNC1k2I7gRHQqlt2urJ_cA-odHswb6x4e_G074Gnl5R6p3lC_zSnMKvu1W2w2Nbp0M8r2YA.png" group-title="CHILE",National Geographic Channel
https://normielista.cl:443/play/0Bu2UVekNecKvoeYhzqb9cJ27zzRXaUVifkaTkP6RywvEgUce_3dNBoNeiMKinhX/ts
#EXTINF:-1 xui-id="171" tvg-id="HCCHDA" tvg-name="History Channel" tvg-logo="https://normielista.cl:443/images/HM3xx55KZnCUdlPuNC1k2PncQnjvX0UIbf-mXiFDYhhRHpsWl0xSTi7hPPFBCAuLQS5yOHjOjCFVYrkZQGabaQ.png" group-title="CHILE",History Channel
https://normielista.cl:443/play/0Bu2UVekNecKvoeYhzqb9Z6cf5QAjTDyhklY3sDH2YoSMiZtRs2Xqoh9XnYGyMA0/ts


'''

banner2 = r'''
#EXTINF:-1 tvg-logo="https://i.imgur.com/5fEIf7q.png" group-title="Radios Chilenas Con Video",-Radios Chilenas Con Video-
https://i.imgur.com/7o6at8Q.mp4
#EXTINF:-1 tvg-logo="https://i.imgur.com/c2qDoi3.png" group-title="Radios Chilenas Con Video",Chocolate FM | SD | Maipú
https://paneltv.online:1936/8106/8106/chunklist_w1524549576.m3u8
#EXTINF:-1 tvg-logo="https://i.imgur.com/G5UGhwA.png" group-title="Radios Chilenas Con Video",Favorita TV | SD | Curicó
http://streamyes.alsolnet.com/radiofavoritatv/live/chunklist_w2007168887.m3u8
#EXTINF:-1 tvg-logo="https://i.imgur.com/IaTIPLW.png" group-title="Radios Chilenas Con Video",Pulso | SD | Santiago
https://panel.tvstream.cl:1936/8004/8004/playlist.m3u8
#EXTINF:-1 tvg-logo="https://i.imgur.com/SkcUAno.png" group-title="Radios Chilenas Con Video",Radio Rancagua TV| SD | Rancagua
https://5d1ca66d2d698.streamlock.net:1936/8056/8056/playlist.m3u8
#EXTINF:-1 tvg-logo="https://i.imgur.com/S8VPPgr.png" group-title="Radios Chilenas Con Video",Red Fueguina Medios | SD | Porvenir
https://inliveserver.com:1936/11012/11012/playlist.m3u8
#EXTINF:-1 tvg-logo="https://i.imgur.com/Vt424Nn.png" group-title="CHILE",TVN CHILE | FHD | Santiago | Alt.

#EXTINF:-1 tvg-logo="https://i.imgur.com/PrG6SkZ.png" group-title="CHILE",Chilevisión | SD | Santiago | Alt.
https://onx.la/fe0aa.m3u8
#EXTINF:-1 tvg-logo="https://i.imgur.com/ILZeBjW.png" group-title="CHILE",Canal 13 | SD | Santiago | Alt.
https://onx.la/3aa24.m3u8
#EXTINF:-1 tvg-logo="https://i.imgur.com/puJ88Pk.png" group-title="CHILE",La Red | FHD | Santiago 2
https://d2ab26kihxq8p0.cloudfront.net/hls/live.m3u8
#EXTINF:-1 tvg-logo="https://i.imgur.com/27i6iYB.png" group-title="CHILE",UCV2 | HD | Valparaíso
https://unlimited10-cl.dps.live/ucvtveventos/ucvtveventos.smil/playlist.m3u8
#EXTINF:-1 tvg-logo="https://i.imgur.com/ilCiqga.png" group-title="CHILE",Canal 21 | HD | Chillan
https://tls-cl.cdnz.cl/canal21tv/live/playlist.m3u8
#EXTINF:-1 tvg-logo="https://i.imgur.com/dPUYBfM.png" group-title="CHILE",Bio Bio TV | FHD | Providencia
https://pantera1-100gb-cl-movistar.dps.live/bbtv/bbtv.smil/bbtv/livestream2/chunks.m3u8
#EXTINF:-1 tvg-logo="https://i.imgur.com/sL057W6.png" group-title="CHILE",Cámara De Diputados| FHD | Valparaíso
http://camara.03.cl.cdnz.cl/camara19/live/chunklist.m3u8
#EXTINF:-1 tvg-logo="https://i.imgur.com/fUQEubL.png" group-title="CHILE",Retro Plus | HD | Chile-Perú
https://59f1cbe63db89.streamlock.net:1443/retroplustv/_definst_/retroplustv/playlist.m3u8
#EXTINF:-1 tvg-logo="https://i.imgur.com/fUQEubL.png" group-title="CHILE",Retro Plus 2 | HD | Chile-Perú
https://59f1cbe63db89.streamlock.net:1443/retroplussenal2/_definst_/retroplussenal2/playlist.m3u8
#EXTINF:-1 tvg-logo="https://i.imgur.com/fUQEubL.png" group-title="CHILE",Retro Plus 3 | HD | Chile-Perú
https://59f1cbe63db89.streamlock.net:1443/retroplussenal3/_definst_/retroplussenal3/playlist.m3u8
#EXTINF:-1 tvg-logo="https://i.imgur.com/saLbzvM.png" group-title="CHILE",Iquique TV | HD | Iquique
https://marine2.miplay.cl/arcatel/iquiquetv720/tracks-v1a1/mono.m3u8
#EXTINF:-1 tvg-logo="https://i.imgur.com/FMFLFIL.png" group-title="CHILE",Atacama TV | HD | Copiapó
https://v2.tustreaming.cl/atacamatv/tracks-v1a1/mono.m3u8
#EXTINF:-1 tvg-logo="https://i.imgur.com/aPA11ts.png" group-title="CHILE",Holvoet TV | SD | Copiapó
https://pantera1-100gb-cl-movistar.dps.live/holvoettv/holvoettv.smil/holvoettv/livestream3/chunks.m3u8
#EXTINF:-1 tvg-logo="https://i.imgur.com/ZSpzX1F.png" group-title="CHILE",TV Quinta Región | HD | Valparaíso
https://mediacpstreamchile.com:1936/8002/8002/chunklist_w1281292195.m3u8
#EXTINF:-1 tvg-logo="https://i.imgur.com/VsfXiJy.png" group-title="CHILE",Pop Media | HD | Santiago
https://v4.tustreaming.cl/poptv/tracks-v1a1/mono.m3u8
#EXTINF:-1 tvg-logo="https://i.imgur.com/PDVNb9i.png" group-title="CHILE",Buin Somos Todos| HD | Buin
https://bst.buin.cl/0.m3u8
#EXTINF:-1 tvg-logo="https://i.imgur.com/hoYBepx.png" group-title="CHILE",Canal 5 | HD | Linares
https://unlimited10-cl.dps.live/tv5/tv5.smil/tv5/livestream1/chunks.m3u8
#EXTINF:-1 tvg-logo="https://i.imgur.com/Iu3turn.png" group-title="CHILE",Ñublevisión | HD | Chillán
https://cdn.oneplaychile.cl:1936/regionales/nublevision.stream/playlist.m3u8
#EXTINF:-1 tvg-logo="https://i.imgur.com/cibYn6l.png" group-title="CHILE",Click TV | HD | Coronel
http://v2.tustreaming.cl/clicktv/tracks-v1a1/mono.m3u8
#EXTINF:-1 tvg-logo="https://i.imgur.com/jL7zgG5.png" group-title="CHILE",Tele Angol | HD | Angol
https://pantera1-100gb-cl-movistar.dps.live/teleangol/teleangol.smil/teleangol/livestream1/chunks.m3u8
#EXTINF:-1 tvg-logo="https://i.imgur.com/phbDD2v.png" group-title="CHILE",Pucón TV | FHD | Pucón
https://unlimited1-cl-isp.dps.live/pucontv/pucontv.smil/pucontv/livestream2/chunks.m3u8
#EXTINF:-1 tvg-logo="https://i.imgur.com/GG8zE02.png" group-title="CHILE",T-Vinet | HD | Osorno
https://unlimited1-cl-isp.dps.live/inet2/inet2.smil/inet2/livestream1/chunks.m3u8
#EXTINF:-1 tvg-logo="https://i.imgur.com/Vm9LuU5.jpg" group-title="CHILE",Décima TV| FHD | Ancud
http://unlimited10-cl.dps.live/decimatv/decimatv.smil/decimatv/livestream1/chunks.m3u8
#EXTINF:-1 tvg-logo="https://i.imgur.com/JHG0k6v.png" group-title="CHILE",Santa María Televisión | SD | Coyhaique
https://unlimited1-cl-isp.dps.live/smtv/smtv.smil/playlist.m3u8
#EXTINF:-1 tvg-logo="https://i.imgur.com/VhOolgs.png" group-title="CHILE",El Pingüino | HD | Punta Arenas
http://streaming.elpinguino.com:1935/live/pinguinotv_720p/livestream.m3u8
#EXTINF:-1 tvg-logo="https://i.imgur.com/mjX7HC0.png" group-title="CHILE",Soberanía| HD | Punta Arenas
https://tls-cl.cdnz.cl/radiosoberania/live/chunklist_w1753930486.m3u8
#EXTINF:-1 tvg-logo="https://i.imgur.com/Vx20KSy.jpg" group-title="CHILE",Umag TV 2| HD | Punta Arenas
https://tls-cl.cdnz.cl/umag2/live/playlist.m3u8
'''

# Processa as linhas do arquivo
for line in lines:
    line = line.strip()
    if not line or line.startswith('~~'):
        continue
    if not line.startswith('http') and len(line.split("|")) == 4:
        line = line.split('|')
        ch_name = line[0].strip()
        grp_title = line[1].strip().title()
        tvg_logo = line[2].strip()
        tvg_id = None
        channel_data.append({
            'type': 'info',
            'ch_name': ch_name,
            'grp_title': grp_title,
            'tvg_logo': tvg_logo,
            'tvg_id': tvg_id
        })
    else:
        youtube_id = extract_youtube_id(line)
        if youtube_id:
            channel_data.append({
                'type': 'link',
                'url': f"https://ythls.armelin.one/channel/{youtube_id}.m3u8"
            })


# Escreve no arquivo .m3u
with open("CHILE.m3u", "w") as f:
    f.write(banner)

    prev_item = None

    for item in channel_data:
        if item['type'] == 'info':
            prev_item = item
        if item['type'] == 'link' and item['url']:
            f.write(f'\n#EXTINF:-1 group-title="{prev_item["grp_title"]}" tvg-logo="{prev_item["tvg_logo"]}", {prev_item["ch_name"]}')
            f.write('\n')
            f.write(item['url'])
            f.write('\n')
    f.write(banner2)
            
          
# Escreve no arquivo JSON (opcional, mantém o formato detalhado)
prev_item = None
for item in channel_data:
    if item['type'] == 'info':
        prev_item = item
    if item['type'] == 'link' and item['url']:
        channel_data_json.append({
            "id": prev_item.get("tvg_id", ""),
            "name": prev_item["ch_name"],
            "alt_names": [""],
            "network": "",
            "owners": [""],
            "country": "AR",
            "subdivision": "",
            "city": "Buenos Aires",
            "broadcast_area": [""],
            "languages": ["spa"],
            "categories": [prev_item["grp_title"]],
            "is_nsfw": False,
            "launched": "2016-07-28",
            "closed": "2020-05-31",
            "replaced_by": "",
            "website": item['url'],
            "logo": prev_item["tvg_logo"]
        })

with open("CHILE.json", "w") as f:
    json_data = json.dumps(channel_data_json, indent=2)
    f.write(json_data)
    
    

