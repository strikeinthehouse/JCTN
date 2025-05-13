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
#EXTM3U url-tvg="https://www.open-epg.com/files/chile1.xml"

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


#EXTINF:-1 group-title="CHILE" tvg-id="Undefined" tvg-logo="http://www.radiosplay.com/logos/3/2/6/7/32679.png",Radio Portal FoxMix Chile
https://sonic.portalfoxmix.cl/8002/stream
#EXTINF:-1 group-title="CHILE" tvg-id="Teletrak" tvg-logo="https://i.imgur.com/iHhc7PK.png",Teletrak | Chile
http://unlimited6-cl.dps.live/sportinghd/sportinghd.smil/playlist.m3u8
#EXTINF:-1 group-title="CHILE" tvg-id="Iquique Tv" tvg-logo="https://iquiquetv.cl/wp-content/uploads/2020/05/iquiqueTV_logo_202005_272x90.png",Iquique Tv | Chile
https://marine2.miplay.cl/arcatel/iquiquetv720/tracks-v1a1/mono.m3u8
#EXTINF:-1 group-title="CHILE" tvg-id="Buin Somos Todos" tvg-logo="https://i.ytimg.com/vi/k_Q7-gqkfAo/maxresdefault.jpg",Buin Somos Todos | Chile
https://bst.buin.cl/0.m3u8
#EXTINF:-1 group-title="CHILE" tvg-id="Caracola TV" tvg-logo="https://www.caracolatv.cl/wp-content/uploads/2021/12/logo-296x300.jpg",Caracola TV | Chile
https://wifispeed.trapemn.tv:1936/comunales/caracola-tv/playlist.m3u8

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

#EXTINF:-1 group-title="CHILE" tvg-id="" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/UCLTV.png?raw=true",UCL
https://livedelta.cdn.antel.net.uy/out/u/url_canalu.m3u8


'''

banner2 = r'''

#EXTINF:-1 group-title="CHILE" tvg-id="Undefined" tvg-logo="https://i.imgur.com/S8VPPgr.png",Red Fueguina Medios | SD | Porvenir
https://inliveserver.com:1936/11012/11012/playlist.m3u8
#EXTINF:-1 group-title="CHILE" tvg-id="Undefined" tvg-logo="https://i.imgur.com/ilCiqga.png",Canal 21 | HD | Chillan
https://tls-cl.cdnz.cl/canal21tv/live/playlist.m3u8
#EXTINF:-1 group-title="CHILE" tvg-id="Undefined" tvg-logo="https://i.imgur.com/saLbzvM.png",Iquique TV | HD | Iquique
https://marine2.miplay.cl/arcatel/iquiquetv720/tracks-v1a1/mono.m3u8
#EXTINF:-1 group-title="CHILE" tvg-id="Undefined" tvg-logo="https://i.imgur.com/FMFLFIL.png",Atacama TV | HD | Copiapó
https://v2.tustreaming.cl/atacamatv/tracks-v1a1/mono.m3u8
#EXTINF:-1 group-title="CHILE" tvg-id="Undefined" tvg-logo="https://i.imgur.com/aPA11ts.png",Holvoet TV | SD | Copiapó
https://pantera1-100gb-cl-movistar.dps.live/holvoettv/holvoettv.smil/holvoettv/livestream3/chunks.m3u8
#EXTINF:-1 group-title="CHILE" tvg-id="Undefined" tvg-logo="https://i.imgur.com/VsfXiJy.png",Pop Media | HD | Santiago
https://v4.tustreaming.cl/poptv/tracks-v1a1/mono.m3u8
#EXTINF:-1 group-title="CHILE" tvg-id="Undefined" tvg-logo="https://i.imgur.com/jL7zgG5.png",Tele Angol | HD | Angol
https://pantera1-100gb-cl-movistar.dps.live/teleangol/teleangol.smil/teleangol/livestream1/chunks.m3u8
#EXTINF:-1 group-title="CHILE" tvg-id="Undefined" tvg-logo="https://i.imgur.com/GG8zE02.png",T-Vinet | HD | Osorno
https://unlimited1-cl-isp.dps.live/inet2/inet2.smil/inet2/livestream1/chunks.m3u8
#EXTINF:-1 group-title="CHILE" tvg-id="Undefined" tvg-logo="https://i.imgur.com/JHG0k6v.png",Santa María Televisión | SD | Coyhaique
https://unlimited1-cl-isp.dps.live/smtv/smtv.smil/playlist.m3u8
#EXTINF:-1 group-title="CHILE" tvg-id="Undefined" tvg-logo="https://i.imgur.com/VhOolgs.png",El Pingüino | HD | Punta Arenas
http://streaming.elpinguino.com:1935/live/pinguinotv_720p/livestream.m3u8
#EXTINF:-1 group-title="CHILE" tvg-id="Undefined" tvg-logo="https://i.imgur.com/mjX7HC0.png",Soberanía| HD | Punta Arenas
https://tls-cl.cdnz.cl/radiosoberania/live/chunklist_w1753930486.m3u8
#EXTINF:-1 group-title="CHILE" tvg-id="Undefined" tvg-logo="https://i.imgur.com/Vx20KSy.jpg",Umag TV 2| HD | Punta Arenas
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
                'url': f"https://ythls-v3.onrender.com/channel/{youtube_id}.m3u8"
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
    

#rato

import requests
import re
import gzip
import os
import shutil
import lzma # Adicionado para suporte a .xz
from xml.etree import ElementTree as ET
from urllib.parse import urlparse

# URL do arquivo M3U
M3U_URL = "https://raw.githubusercontent.com/strikeinthehouse/1/refs/heads/main/lista1.M3U"
OUTPUT_XMLTV_FILE = "GUIA.xml"
TEMP_DIR = "epg_temp_files"
PROCESSED_DIR = os.path.join(TEMP_DIR, "processed_xmls") # Diretório para XMLs processados

def download_file(url, destination):
    """Baixa um arquivo de uma URL para um destino local."""
    print(f"Tentando baixar: {url}")
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, stream=True, timeout=60, headers=headers, allow_redirects=True)
        response.raise_for_status()  # Levanta um erro para códigos de status ruins (4xx ou 5xx)
        with open(destination, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Arquivo baixado com sucesso: {url} -> {destination}")
        return True
    except requests.exceptions.Timeout:
        print(f"Timeout ao baixar {url}")
        return False
    except requests.exceptions.TooManyRedirects:
        print(f"Muitos redirecionamentos ao baixar {url}")
        return False
    except requests.exceptions.RequestException as e:
        print(f"Erro ao baixar {url}: {e}")
        return False

def extract_epg_urls_from_m3u(m3u_content):
    """Extrai URLs de EPG de um conteúdo M3U."""
    pattern = r'(?:url-tvg|x-tvg-url)="([^"]+)"'
    matches = re.findall(pattern, m3u_content)
    epg_urls = set()
    for match in matches:
        urls_in_match = match.split(',')
        for url in urls_in_match:
            cleaned_url = url.strip()
            if cleaned_url: 
                epg_urls.add(cleaned_url)
    print(f"URLs de EPG encontrados no M3U: {list(epg_urls)}")
    return list(epg_urls)

def get_file_name_from_url(url, index):
    """Gera um nome de arquivo a partir da URL ou usa um índice."""
    try:
        path = urlparse(url).path
        file_name = os.path.basename(path)
        base, ext = os.path.splitext(file_name)
        if not ext or ext.lower() not in ['.xml', '.gz', '.xz']:
            if '.xml.gz' in url.lower():
                file_name = f"epg_{index}.xml.gz"
            elif '.xml.xz' in url.lower():
                file_name = f"epg_{index}.xml.xz"
            elif '.xml' in url.lower():
                file_name = f"epg_{index}.xml"
            elif '.gz' in url.lower():
                file_name = f"epg_{index}.gz"
            elif '.xz' in url.lower():
                file_name = f"epg_{index}.xz"
            else:
                file_name = f"epg_file_{index}.dat"
        else:
            file_name = f"{base}_{index}{ext}"
        return file_name
    except Exception as e:
        print(f"Erro ao extrair nome do arquivo da URL {url}: {e}. Usando nome genérico epg_file_{index}.dat")
        return f"epg_file_{index}.dat"

def decompress_and_normalize_epgs(downloaded_files, output_dir):
    """Descompacta arquivos EPG e os normaliza para XML, salvando no output_dir."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Diretório para XMLs processados criado: {output_dir}")

    processed_xml_files = []
    for i, file_path in enumerate(downloaded_files):
        base_name = os.path.basename(file_path)
        if base_name.endswith(".gz"):
            xml_file_name = base_name[:-3]
        elif base_name.endswith(".xz"):
            xml_file_name = base_name[:-3]
        elif base_name.endswith(".xml"):
            xml_file_name = base_name
        else:
            print(f"Arquivo com extensão desconhecida ou não é um EPG esperado, pulando: {file_path}")
            continue
        
        if not xml_file_name.endswith(".xml"):
            xml_file_name += ".xml"
        
        final_xml_path = os.path.join(output_dir, f"{os.path.splitext(xml_file_name)[0]}_{i}.xml")

        try:
            print(f"Processando arquivo: {file_path} -> {final_xml_path}")
            content_to_parse = None
            if file_path.endswith(".gz"):
                with gzip.open(file_path, 'rb') as f_gz:
                    content_to_parse = f_gz.read()
            elif file_path.endswith(".xz"):
                with lzma.open(file_path, 'rb') as f_xz:
                    content_to_parse = f_xz.read()
            elif file_path.endswith(".xml"):
                with open(file_path, 'rb') as f_xml:
                    content_to_parse = f_xml.read()
            else:
                continue

            if content_to_parse:
                try:
                    decoded_content = content_to_parse.decode('utf-8')
                except UnicodeDecodeError:
                    print(f"Falha ao decodificar {file_path} como UTF-8, tentando latin-1...")
                    try:
                        decoded_content = content_to_parse.decode('latin-1')
                    except UnicodeDecodeError as ude_latin:
                        print(f"Falha ao decodificar {file_path} como latin-1: {ude_latin}. Pulando arquivo.")
                        continue
                
                ET.fromstring(decoded_content) 
                
                with open(final_xml_path, 'w', encoding='utf-8') as f_out:
                    f_out.write(decoded_content)
                processed_xml_files.append(final_xml_path)
                print(f"Arquivo XML normalizado salvo: {final_xml_path}")
            
        except ET.ParseError as e_parse:
            print(f"Erro de parsing XML em {file_path}: {e_parse}. Pulando arquivo.")
        except gzip.BadGzipFile:
            print(f"Arquivo GZip inválido: {file_path}. Pulando.")
        except lzma.LZMAError as e_lzma:
            print(f"Erro LZMA ao processar {file_path}: {e_lzma}. Pulando.")
        except Exception as e:
            print(f"Erro inesperado ao processar {file_path}: {e}. Pulando.")
            
    return processed_xml_files

def merge_xmltv_files(xml_files, output_file_path):
    """Mescla múltiplos arquivos XMLTV em um único arquivo."""
    print(f"\nIniciando mesclagem de {len(xml_files)} arquivos XMLTV para {output_file_path}")
    # Cria o elemento raiz <tv>
    merged_root = ET.Element("tv")
    # Para evitar canais duplicados, rastreia os IDs dos canais já adicionados
    channel_ids = set()

    for xml_file in xml_files:
        try:
            print(f"Mesclando arquivo: {xml_file}")
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            # Adiciona atributos do elemento raiz do arquivo de origem ao merged_root, se não existirem
            # Isso pode ser útil para atributos como 'source-info-url', 'source-info-name', etc.
            # Evita sobrescrever se já definido por um arquivo anterior, mas pode ser ajustado.
            for key, value in root.attrib.items():
                if key not in merged_root.attrib:
                    merged_root.set(key, value)

            for channel_element in root.findall("channel"):
                channel_id = channel_element.get("id")
                if channel_id not in channel_ids:
                    merged_root.append(channel_element)
                    channel_ids.add(channel_id)
                else:
                    print(f"Canal duplicado encontrado e ignorado: ID {channel_id} do arquivo {xml_file}")
            
            for programme_element in root.findall("programme"):
                merged_root.append(programme_element)
            print(f"Conteúdo de {xml_file} adicionado à mesclagem.")

        except ET.ParseError as e:
            print(f"Erro de parsing XML ao mesclar {xml_file}: {e}. Pulando este arquivo.")
        except Exception as e:
            print(f"Erro inesperado ao mesclar {xml_file}: {e}. Pulando este arquivo.")

    # Cria a árvore XML final e escreve no arquivo
    merged_tree = ET.ElementTree(merged_root)
    try:
        # ET.indent(merged_tree, space="  ", level=0) # Para Python 3.9+
        merged_tree.write(output_file_path, encoding="utf-8", xml_declaration=True)
        print(f"Arquivo XMLTV mesclado salvo com sucesso em: {output_file_path}")
        return True
    except Exception as e:
        print(f"Erro ao salvar o arquivo XMLTV mesclado: {e}")
        return False

def main():
    """Função principal para orquestrar o processo."""
    if os.path.exists(OUTPUT_XMLTV_FILE):
        os.remove(OUTPUT_XMLTV_FILE)
        print(f"Arquivo {OUTPUT_XMLTV_FILE} existente removido.")
        
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
        print(f"Diretório temporário {TEMP_DIR} existente removido.")
    os.makedirs(TEMP_DIR)
    print(f"Diretório temporário criado: {TEMP_DIR}")

    print(f"Baixando o arquivo M3U de: {M3U_URL}")
    m3u_file_name = "lista_original.m3u"
    m3u_file_path = os.path.join(TEMP_DIR, m3u_file_name)

    if not download_file(M3U_URL, m3u_file_path):
        print("Falha ao baixar o arquivo M3U. Saindo.")
        if os.path.exists(TEMP_DIR):
            shutil.rmtree(TEMP_DIR)
        return

    with open(m3u_file_path, 'r', encoding='utf-8', errors='ignore') as f:
        m3u_content = f.read()
    
    epg_urls = extract_epg_urls_from_m3u(m3u_content)

    if not epg_urls:
        print("Nenhum URL de EPG encontrado no arquivo M3U. Saindo.")
        if os.path.exists(TEMP_DIR):
            shutil.rmtree(TEMP_DIR)
        return

    downloaded_epg_files = []
    print("\nIniciando download dos arquivos EPG...")
    for i, epg_url in enumerate(epg_urls):
        file_name = get_file_name_from_url(epg_url, i)
        destination_path = os.path.join(TEMP_DIR, file_name)
        print(f"Baixando EPG {i+1}/{len(epg_urls)}: {epg_url}")
        if download_file(epg_url, destination_path):
            downloaded_epg_files.append(destination_path)
        else:
            print(f"Falha ao baixar EPG: {epg_url}")

    if not downloaded_epg_files:
        print("Nenhum arquivo EPG foi baixado com sucesso. Saindo.")
        if os.path.exists(TEMP_DIR):
            shutil.rmtree(TEMP_DIR)
        return
    
    print(f"\nArquivos EPG baixados com sucesso: {downloaded_epg_files}")

    print("\nIniciando descompressão e normalização dos arquivos EPG...")
    normalized_xml_files = decompress_and_normalize_epgs(downloaded_epg_files, PROCESSED_DIR)

    if not normalized_xml_files:
        print("Nenhum arquivo EPG pôde ser normalizado para XML. Saindo.")
        if os.path.exists(TEMP_DIR):
            shutil.rmtree(TEMP_DIR)
        return

    print(f"\nArquivos EPG normalizados para XML: {normalized_xml_files}")

    print("\nIniciando mesclagem dos arquivos XMLTV normalizados...")
    if merge_xmltv_files(normalized_xml_files, OUTPUT_XMLTV_FILE):
        print(f"\nProcesso concluído! Arquivo final: {OUTPUT_XMLTV_FILE}")
    else:
        print("\nProcesso concluído com erros na mesclagem ou ao salvar o arquivo final.")

    # Limpeza final do diretório temporário
    if os.path.exists(TEMP_DIR):
        try:
            shutil.rmtree(TEMP_DIR)
            print(f"Diretório temporário {TEMP_DIR} removido com sucesso.")
        except Exception as e:
            print(f"Erro ao remover o diretório temporário {TEMP_DIR}: {e}")

if __name__ == "__main__":
    main()

