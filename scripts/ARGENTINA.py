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
CHANNEL_FILE_URL = "https://github.com/strikeinthehouse/JCTN/raw/refs/heads/main/channel_argentina.txt"

# Funções utilitárias
def download_channel_file(url):
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        return response.text.splitlines()  # Retorna o conteúdo do arquivo como uma lista de linhas
    except requests.exceptions.RequestException as err:
        logger.error("Erro ao baixar o arquivo: %s", err)
        sys.exit("Erro ao baixar o arquivo .txt")

def extract_youtube_id(url):
    """Extrai o ID do canal do YouTube ou do vídeo a partir da URL."""
    # Para URLs do tipo "/channel/<ID>"
    channel_match = re.search(r"youtube\.com/channel/([a-zA-Z0-9_-]+)", url)
    if channel_match:
        return channel_match.group(1)
    
    # Para URLs do tipo "/watch?v=<ID>" ou "/live/<ID>"
    video_match = re.search(r"(?:youtube\.com/watch\?v=|youtube\.com/live/|youtube\.com/live/\S+)[a-zA-Z0-9_-]+", url)
    if video_match:
        return video_match.group(1)
    
    logger.warning("ID não encontrado para URL: %s", url)
    return None

# Baixa e processa o arquivo de canais
lines = download_channel_file(CHANNEL_FILE_URL)

channel_data = []
channel_data_json = []

banner = r'''
#EXTM3U

###########################################################################

###########################################################################
#EXTM3U
#EXTM3U url-tvg="https://www.bevy.be/bevyfiles/argentina.xml"









#EXTINF:-1 group-title="Argentina" tvg-id="Undefined" tvg-logo="https://i.imgur.com/HbV9HoX.png",Norte | Bahía Blanca | Argentina
http://icecast.hostingbahia.com.ar:8002/live?28344
#EXTINF:-1 group-title="Argentina" tvg-id="ext" tvg-logo="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSDuahOnWWlOYyXxDG06AjPNNbloMrSP3Jp27gssjJTTNyL22bTlI9_3B_ikgw&s",Camaras de Villa Gesell (Av. 3 y 104)
http://cam104y3.gesell.com.ar/playlist.m3u8
#EXTINF:-1 group-title="Argentina" tvg-id="ext" tvg-logo="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQcLeOH4M9sdPlrWP0eHmQKfJTBMrULDwI-0VS-AG9pztqWI4Sm_ONWDiTDU7s&s",Camaras de Villa Gesell (Buenos Aires y Playa)
http://cambsasyplaya.gesell.com.ar/playlist.m3u8
#EXTINF:-1 group-title="Argentina" tvg-id="ext" tvg-logo="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT1cJSBszES8cDQO6Dq51JiL1h1i3QiobX7Wi_02BLUbro56R7h1QJDQUOwPXY&s",Camaras de Villa Gesell (La Pinocha)
http://camlapinocha.gesell.com.ar/playlist.m3u8
#EXTINF:-1 group-title="Argentina" tvg-id="ElGarageTV.ar" tvg-logo="https://lh3.googleusercontent.com/-2gN4wEv_qPI/XjtKDwMuIQI/AAAAAAAAvrY/VTtJwZALBykDRnM8ia0Xbqi0FbREvdrZACK8BGAsYHg/s0/2020-02-05.png",GARAGE TV
https://stream1.sersat.com/hls/garagetv.m3u8
#EXTINF:-1 group-title="Argentina" tvg-id="America TV Argentina" tvg-logo="https://imagenes.gatotv.com/logos/canales/oscuros/america_tv_argentina.png",America TV | Argentina - TDA 2.1
#EXTVLCOPT:http-referrer=https://vmf.edge-apps.net
https://prepublish.f.qaotic.net/a07/americahls-100056/Playlist.m3u8
#EXTINF:-1 group-title="Argentina" tvg-id="AmericaTV.ar" tvg-logo="https://raw.githubusercontent.com/mortal251/logos/main/AMERICA.png",America TV | Argentina - TDA 2.1
#EXTVLCOPT:http-referrer=https://vmf.edge-apps.net
https://prepublish.f.qaotic.net/a07/americahls-100056/Playlist.m3u8
#EXTINF:-1 group-title="Argentina" tvg-id="AmericaTV.ar" tvg-logo="https://raw.githubusercontent.com/mortal251/logos/main/AMERICA.png",America TV | Argentina - TDA 2.1
http://cord-cutter.net:8080/live/j3McKd/673709/164881.m3u8
#EXTINF:-1 group-title="Argentina" tvg-id="AmericaTV.ar" tvg-logo="https://www.lyngsat-logo.com/logo/tv/aa/america-tv-ar.png",América TV
http://181.13.173.86:8000/play/a0a7/index.m3u8
#EXTINF:-1 group-title="Argentina" tvg-id="Undefined" tvg-logo="https://www.m3u.cl/logo/259_Canal_4_Posadas.png",América Canal 4 Posadas | AR
http://iptv.ixfo.com.ar:8081/live/C4POS/playlist.m3u8?PlaylistM3UCL





#EXTINF:-1 tvg-logo="https://scontent.fepa11-1.fna.fbcdn.net/v/t1.6435-9/206638151_10223169123710059_3666810289391430657_n.jpg?_nc_cat=101&ccb=1-3&_nc_sid=825194&_nc_eui2=AeGxugJ54qa7RhgKBnLTrHOu14OonvQq8lrXg6ie9CryWkCQzaYyrufVmZGkiprZVM0&_nc_ohc=dbLCQPiMFxEAX9X0jrT&_nc_ht=scontent.fepa11-1.fna&oh=afeef92e5377cb7720df7b2f4afc60c8&oe=6127F95F" group-title="Argentina",SSIPTV ARG TV - TDA 6.2
http://service-stitcher.clusters.pluto.tv/stitch/hls/channel/5df265697ec3510009df1ef0/master.m3u8?advertisingId=&appName=web&appVersion=unknown&appStoreUrl=&architecture=&buildVersion=&clientTime=0&deviceDNT=0&deviceId=bff1d530-6307-11eb-b3fa-019cb96f121b&deviceMake=Chrome&deviceModel=web&deviceType=web&deviceVersion=unknown&includeExtendedEvents=false&sid=ec2383fd-6e28-4df5-9d1c-b66eee7000c&userId=&serverSideAds=true

#EXTINF:-1 tvg-id="TVPublica.ar" tvg-logo="https://www.lyngsat-logo.com/logo/tv/tt/tv-publica-ar.png" group-title="Argentina",TV PUBLICA
http://181.13.173.86:8000/play/a0aq/index.m3u8

#EXTINF:-1 tvg-id="TVPublica.ar" tvg-logo="https://www.lyngsat-logo.com/logo/tv/tt/tv-publica-ar.png" group-title="Argentina",TV PUBLICA
https://g2.proy-hor.transport.edge-access.net/b16/ngrp:c7_vivo01_dai_source-20001_all/c7_vivo01_dai_source-20001_1080p.m3u8

#EXTINF:-1 tvg-id="TVPublica.ar" tvg-country="AR" tvg-logo="https://raw.githubusercontent.com/mortal251/logos/main/TV_PUBLICA.jpg" group-title="Argentina",TV PUBLICA
https://g2.proy-slo.transport.edge-access.net/b16/ngrp:c7_vivo01_dai_source-20001_all/c7_vivo01_dai_source-20001_480p.m3u8
#EXTINF:-1 tvg-id="TVPublica.ar" tvg-country="AR" tvg-logo="https://raw.githubusercontent.com/mortal251/logos/main/TV_PUBLICA.jpg" group-title="Argentina",TV PUBLICA
http://168.197.196.98:9981/stream/channelid/1475050013?profile=pass
#EXTINF:-1 tvg-id="Television Publica" tvg-name="Television Publica" tvg-logo="https://i.imgur.com/04nIdpc.png" group-title="Argentina",TV PUBLICA 2
http://168.197.196.98:9981/stream/channelid/1475050013

#EXTINF:-1 tvg-id="Television Publica" tvg-name="Television Publica" tvg-logo="https://i.imgur.com/04nIdpc.png" group-title="Argentina",Television Publica - Argentina - TDA 7.1
https://cntlnk-main-edge-access.dlt.qwilted-cds.cqloud.com/entrypoint/c7_vivo01_dai_source-20001_all_1080p.m3u8

#EXTINF:-1 tvg-id="Television Publica" tvg-name="Television Publica" tvg-logo="https://upload.wikimedia.org/wikipedia/commons/0/0a/Logo_Televisi%C3%B3n_P%C3%BAblica_Argentina.png" group-title="Argentina",TV PUBLICA - SINAL ORIGINAL 2 - TDA 7.1
https://cntlnk-main-edge-access.dlt.qwilted-cds.cqloud.com/entrypoint/c7_vivo01_dai_source-20001_all_1080p.m3u8

#EXTINF:-1 tvg-id="Television Publica" tvg-name="Television Publica" tvg-logo="https://i.imgur.com/04nIdpc.png" group-title="Argentina",TV PUBLICA 3
http://abcnew.site:8880/D12m2692/94245219/49978
#EXTINF:-1 tvg-id="TVPublica.ar" tvg-country="AR" tvg-logo="https://raw.githubusercontent.com/mortal251/logos/main/TV_PUBLICA.jpg" group-title="Argentina",TV PUBLICA 4
http://181.191.140.2:8000/play/a0hd/index.m3u8
#EXTINF:-1 tvg-id="TVPublica.ar" tvg-country="AR" tvg-logo="https://raw.githubusercontent.com/mortal251/logos/main/TV_PUBLICA.jpg" group-title="Argentina",TV PUBLICA 5
https://cntlnk-main-edge-access.dlt.qwilted-cds.cqloud.com/entrypoint/c7_vivo01_dai_source-20001_all_1080p.m3u8
#EXTINF:-1 tvg-id="Television Publica" tvg-name="Television Publica" tvg-logo="https://i.imgur.com/04nIdpc.png" group-title="Argentina",Television Publica | Argentina
http://198.27.117.10:8080/Carlos2022/Carlos2022/362546
#EXTINF:-1 tvg-id="Television Publica" tvg-name="Television Publica" tvg-logo="https://i.imgur.com/04nIdpc.png" group-title="Argentina",Television Publica | Argentina
http://177.128.115.10:8000/play/a0a6/116203


#EXTINF:-1 tvg-logo="https://i2.paste.pics/35c791e364c3adb7c6c2ef98504041a0.png" group-title="Argentina",TELECOLORMUX - TDA 8.1
https://live.obslivestream.com/telecolormux/tracks-v1a1/mono.m3u8



#EXTINF:-1 group-title="Argentina" tvg-id="Telefe.ar" tvg-logo="https://cdn.mitvstatic.com/channels/ar_telefe_m.png",Telefe
http://181.13.173.86:8000/play/a06c/index.m3u8
#EXTINF:-1 group-title="Argentina" tvg-id="Telefe.ar" tvg-logo="https://raw.githubusercontent.com/mortal251/logos/main/telefe.jpg",Telefe | Argentina - TDA 11.1
http://181.209.114.13:8000/play/a06c/index.m3u8



#EXTINF:-1 tvg-id="Telefe.ar" tvg-logo="https://telefe-static.akamaized.net/media/18154476/logo-telefe-twitter.png" group-title="Argentina", Telefe (VPN) - TDA 11.1
https://mitelefe.com/Api/Videos/GetSourceUrl/694564/0/HLS

#EXTINF:-1 tvg-id="Telefe.ar" tvg-logo="http://x.playerlatino.live/telefe.png" group-title="Argentina", Telefe (VPN) 2 - TDA 11.1
https://telefe.com/Api/Videos/GetSourceUrl/694564/0/HLS?.m3u8








#EXTINF:-1 group-title="Argentina" tvg-id="Undefined" tvg-logo="https://i.imgur.com/q6BQ5YO.png",Telefe Canal 7 Jujuy
https://stream.arcast.live/canal7jujuy/ngrp:canal7jujuy_all/playlist.m3u8?PlaylistM3UCL
#EXTINF:-1 group-title="Argentina" tvg-id="Undefined" tvg-logo="https://www.m3u.cl/logo/251_13_Max_Television.png",Telefe 13 Max Television
http://coninfo.net:1935/13maxhd/live13maxtvnuevo_720p/playlist.m3u8?PlaylistM3UCL
#EXTINF:-1 group-title="Argentina" tvg-id="13Max.ar" tvg-logo="http://i.imgur.com/oSApjUM.png",13 Max HD
http://coninfo.net:1935/13maxhd/live13maxtvnuevo_720p/chunklist_w2131508282.m3u8
#EXTINF:-1 group-title="Argentina" tvg-id="13Max.ar" tvg-logo="http://i.imgur.com/oSApjUM.png",13 Max FHD
http://coninfo.net:1935/13maxhd/live13maxtvnuevo/playlist.m3u8

#EXTINF:-1 tvg-id="ElTrece.ar" tvg-logo="https://cdn.mitvstatic.com/channels/ar_el-trece_m.png" group-title="Argentina",El Trece - TDA 13.1
http://181.13.173.86:8000/play/a06d/index.m3u8

#EXTINF:-1 tvg-id="13 de Argentina" tvg-name="13 de Argentina" tvg-logo="https://upload.wikimedia.org/wikipedia/commons/4/45/Eltrece_logotipo_2018.png" group-title="Argentina", El Trece - TDA 13.1
https://livetrx01.vodgc.net/eltrecetv/index.m3u8

#EXTINF:-1 tvg-id="13 de Argentina" tvg-name="13 de Argentina" tvg-logo="https://upload.wikimedia.org/wikipedia/commons/4/45/Eltrece_logotipo_2018.png" group-title="Argentina", El Trece - TDA 13.1
http://181.191.140.2:8000/play/a0ir/index.m3u8

#EXTINF:-1 tvg-id="ElTrece.ar" tvg-logo="https://cdn.mitvstatic.com/channels/ar_el-trece_m.png" group-title="Argentina",El Trece
https://live-01-02-eltrece.vodgc.net/eltrecetv/index.m3u8


#EXTINF:-1 tvg-id="ElTrece.ar" tvg-country="AR" tvg-logo="https://raw.githubusercontent.com/mortal251/logos/main/CANAL_13.jpg" group-title="Argentina", CANAL 13 33.1 
https://live-01-02-eltrece.vodgc.net:443/eltrecetv/tracks-v2a1/mono.m3u8

#EXTINF:-1 tvg-id="ElTrece.ar" tvg-country="AR" tvg-logo="https://raw.githubusercontent.com/mortal251/logos/main/CANAL_13.jpg" group-title="Argentina", CANAL 13 33.1 
https://live-01-02-eltrece.vodgc.net/eltrecetv_noti/index.m3u8



#EXTINF:-1 tvg-id="13 de Argentina" tvg-name="13 de Argentina" tvg-logo="https://imagenes.gatotv.com/logos/canales/oscuros/13_de_argentina.png" group-title="Argentina",El Trece | Argentina
http://177.128.115.10:8000/play/a0a6/116200
#EXTINF:-1 tvg-id="13 de Argentina" tvg-name="13 de Argentina" tvg-logo="https://imagenes.gatotv.com/logos/canales/oscuros/13_de_argentina.png" group-title="Argentina",El Trece | Argentina
http://198.27.117.10:8080/Carlos2022/Carlos2022/362529

#EXTINF:-1 group-title="Argentina" tvg-logo="https://www.m3u.cl/logo/236_Canal_9_Litoral.png",El Trece Canal 9 Litoral
https://stream.arcast.live/ahora/ahora/playlist.m3u8?PlaylistM3UCL

#EXTINF:-1 group-title="Argentina" tvg-logo="https://i.postimg.cc/C1hXHVWR/CANAL-10-RIONEGRO.png",El Trece CANAL 10 RIONEGRO 
https://panel.host-live.com:443/tvrionegro/ngrp:tvrionegro_all/playlist.m3u8?PlaylistM3UCL

#EXTINF:-1 tvg-id="ElNueve.ar" tvg-country="AR" tvg-logo="https://raw.githubusercontent.com/mortal251/logos/main/CANAL_9.jpg" group-title="Argentina", CANAL 9  35.1 
http://cord-cutter.net:8080/live/j3McKd/673709/164869.m3u8

#EXTINF:-1 tvg-id="El Nueve AR" tvg-name="El Nueve AR" tvg-country="AR" tvg-logo="https://vignette.wikia.nocookie.net/logopedia/images/f/f7/Canal-nueve-ar2017.png" group-title="Argentina", CANAL 9 35.1 - TDA 35.1
http://168.197.196.98:9981/stream/channelid/369719429?profile=pass&checkedby:alliptvlinks.com

#EXTINF:-1 tvg-id="ElNueve.ar" tvg-country="AR" tvg-logo="https://raw.githubusercontent.com/mortal251/logos/main/CANAL_9.jpg" group-title="Argentina", CANAL 9  35.1
https://bvsat02.cdn.rcs.net.ar/mnp/elnueve/output.mpd





#EXTINF:-1 tvg-id="ElNueve.ar" tvg-logo="https://www.lyngsat-logo.com/logo/tv/ee/el-nueve-ar.png" group-title="Argentina",El Nueve
http://181.13.173.86:8000/play/a0ae/index.m3u8

#EXTINF:-1 tvg-logo="https://image.winudf.com/v2/image1/Y29tLmExMjNmcmVlYXBwcy5mcmVlLmFwcDVkNWVjMWY4ODliOThfaWNvbl8xNTY3NjE5OTcxXzAxNw/icon.png?w=170&fakeurl=1" group-title="Argentina",CANAL 4 TELEAIRE SAN MARTIN - TDA 21.1
https://stmvideo2.livecastv.com/canal4/canal4/playlist.m3u8

#KODIPROP:inputstream.adaptive.license_type=org.w3.clearkey
#KODIPROP:inputstream.adaptive.license_key=745e7abcc90d41ab706b2ac2f4371da3:50acd9d19d1361cb4a8a13a867bdc352



#EXTINF:-1 tvg-id="CronicaTV.ar" tvg-name="CRNHD" tvg-logo="https://raw.githubusercontent.com/mortal251/logos/main/CRONICA_HD.png" group-title="Argentina",Cronica TV | Argentina - TDA 22.1
http://cord-cutter.net:8080/live/j3McKd/673709/164875.m3u8

#EXTINF:-1 tvg-id="CronicaTV.ar" tvg-logo="https://www.lyngsat-logo.com/logo/tv/cc/cronica-tv-ar.png" group-title="Argentina",Crónica TV
http://181.13.173.86:8000/play/a01q/index.m3u8

#EXTINF:-1 tvg-id="CronicaTV.ar" tvg-country="AR" tvg-logo="https://raw.githubusercontent.com/mortal251/logos/main/CRONICA_HD.png" group-title="Argentina", CRONICA HD 
http://190.11.130.46/mnp/cronica/output.mpd

#KODIPROP:inputstream.adaptive.license_type=org.w3.clearkey
#KODIPROP:inputstream.adaptive.license_key=745e7abcc90d41ab706b2ac2f4371da3:50acd9d19d1361cb4a8a13a867bdc352
#EXTINF:-1 tvg-chno="8" tvg-id="CronicaTV.ar" tvg-name="" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/CRNCA.png?raw=true" tvg-group="Noticias", Cronica
https://chromecast.cvattv.com.ar/live/c7eds/CronicaTV/SA_Live_dash_enc_2A/CronicaTV.mpd

#EXTINF:-1 tvg-id="America TV Argentina" tvg-name="America TV Argentina" tvg-logo="https://imagenes.gatotv.com/logos/canales/oscuros/america_tv_argentina.png" group-title="Argentina",MILENIO TV
http://tv.dominiotv.xyz:25461/live/Rolando/Rolando2021/52487.ts

#EXTINF:-1 tvg-id="Encuentro.ar" tvg-country="AR" tvg-logo="http://tvabierta.weebly.com/uploads/5/1/3/4/51344345/encuentro.png" group-title="Argentina",CANAL ENCUENTRO 22.1
http://cord-cutter.net:8080/live/j3McKd/673709/164878.m3u8

#EXTINF:-1 tvg-id="Encuentro.ar" tvg-logo="https://www.lyngsat-logo.com/logo/tv/ee/encuentro-ar.png" group-title="Argentina",Encuentro
http://181.13.173.86:8000/play/a01m/index.m3u8

EXTINF:-1 tvg-logo="https://i.ibb.co/41CYHm1/La-Naci-n.png" group-title="Argentina",LA NACION
http://45.5.151.151:8000/play/a0e2/index.m3u8

#EXTINF:-1 tvg-id="LaNacionPlus.ar" tvg-logo="https://www.lyngsat-logo.com/logo/tv/ll/lnplus-ar.png" group-title="Argentina",LN+
http://181.13.173.86:8000/play/a01s/index.m3u8

#EXTINF:-1 tvg-id="IP" tvg-name="Informacion Periodistica" tvg-logo="https://upload.wikimedia.org/wikipedia/commons/thumb/3/37/Informaci%C3%B3n_Period%C3%ADstica_IP_Logo.svg/260px-Informaci%C3%B3n_Period%C3%ADstica_IP_Logo.svg.png" group-title="Argentina",Informacion Periodistica | Argentina - TDA 24.5
https://d1nmqgphjn0y4.cloudfront.net/live/ip/live.isml/live-audio_1=128000-video=4499968.m3u8

#EXTINF:-1 tvg-id="IP" tvg-name="Informacion Periodística" tvg-logo="https://i.imgur.com/SQSu9M5.png" group-title="Argentina",Informacion Periodística | Argentina - TDA 24.5
https://octubre-live.cdn.vustreams.com/live/ip/live.isml/live-audio_1=128000-video=2800000.m3u8

#EXTINF:-1 tvg-id="InformacionPeriodistica.ar" tvg-country="AR" tvg-logo="https://raw.githubusercontent.com/mortal251/logos/main/IP_NOTICIAS.jpg" group-title="Argentina", IP NOTICIAS
http://190.11.130.46/mnp/ip/output.mpd 

#EXTINF:-1 tvg-id="InformacionPeriodistica.ar" tvg-country="AR" tvg-logo="https://raw.githubusercontent.com/mortal251/logos/main/IP_NOTICIAS.jpg" group-title="Argentina", IP NOTICIAS
http://190.11.130.46/mnp/ip/output.mpd

#EXTINF:-1 tvg-id="InformacionPeriodistica.ar" tvg-name="INFORMACION PERIODISTICA HD" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/IPNOT.png?raw=true" group-title="Argentina",INFORMACION PERIODISTICA HD
http://cord-cutter.net:8080/live/j3McKd/673709/164879.m3u8

#EXTINF:-1 tvg-id="InformacionPeriodistica.ar" tvg-name="IP" tvg-logo="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSdQ4CbRDh4Wgxt0o_pw9V-kw9Vz6T0Re2Q_RD62jp7cZMO0uWvSKSUN6sZ2vjYcbn5fAs&usqp=CAU" group-title="Argentina",IP | Argentina - TDA 24.5
https://d1nmqgphjn0y4.cloudfront.net/live/ip/live.isml/live-audio_1=128000-video=729984.m3u8

#KODIPROP:inputstream.adaptive.license_type=org.w3.clearkey
#KODIPROP:inputstream.adaptive.license_key=5299f96f873aa0f0e47edc4e15784717:9d53176b0969492f2d93f1867be1dce1





#EXTINF:-1 tvg-id="TN.ar" tvg-name="TNNOT" tvg-logo="http://www.radiosargentina.com.ar/png/VI----TN.png" group-title="Argentina",TN Todo Noticias - TDA 20.1
http://cord-cutter.net:8080/live/j3McKd/673709/164873.m3u8

#EXTINF:-1 tvg-id="TN.ar" tvg-logo="http://i.imgur.com/XEnY7aW.png" group-title="Argentina" user-agent="iPhone",TN
http://181.13.173.86:8000/play/a0ap/index.m3u8



#EXTINF:-1 tvg-logo="http://tvabierta.weebly.com/uploads/5/1/3/4/51344345/unife.png" group-title="Argentina",UNIFE 25.1 - TDA 25.1
https://cdn.mycloudstream.io/hls/live/broadcast/pgv5kerk/mono.m3u8


#EXTINF:-1 tvg-id="C5N" tvg-name="C5N" tvg-logo="https://cdn.mitvstatic.com/channels/ar_c5n_m.png" group-title="Argentina",C5N | Argentina - TDA 26.1
http://cord-cutter.net:8080/live/j3McKd/673709/164876.m3u8

#EXTINF:-1 tvg-id="C5N.ar" tvg-logo="https://www.lyngsat-logo.com/logo/tv/cc/c5n-ar.png" group-title="Argentina",C5N
http://181.13.173.86:8000/play/a01p/index.m3u8

#EXTINF:-1 tvg-id="C5N.ar" tvg-name="C5NOT" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/C5NAR.png?raw=true" group-title="Argentina",C5N
http://cord-cutter.net:8080/live/j3McKd/673709/164876.m3u8

#EXTINF:-1 tvg-id="C5N.ar" tvg-name="C5NOT" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/C5NAR.png?raw=true" group-title="Argentina",C5N
http://181.209.114.13:8000/play/a01p/index.m3u8

#EXTINF:-1 tvg-id="America 24" tvg-name="America 24" tvg-logo="https://cdn.mitvstatic.com/channels/ar_america-24_m.png" group-title="Argentina",America 24 | Argentina

#EXTINF:-1 tvg-id="A24" tvg-name="America 24" tvg-logo="https://cdn.mitvstatic.com/channels/ar_america-24_m.png" group-title="Argentina",America 24 | Argentina - TDA 27.1
http://45.5.151.151:8000/play/a0dy/index.m3u8

#EXTINF:-1 tvg-id="A24.ar" tvg-name="AME24" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/A24.png?raw=true" tvg-group="Noticias", A24
http://45.5.151.151:8000/play/a0dy/index.m3u8

#EXTINF:-1 tvg-id="A24.ar" tvg-logo="https://www.lyngsat-logo.com/logo/tv/aa/a24-ar.png" group-title="Argentina",A24
http://181.13.173.86:8000/play/a01o/index.m3u8

#EXTINF:-1 tvg-id="NetTV.ar" tvg-country="AR" tvg-logo="https://raw.githubusercontent.com/mortal251/logos/main/NET_TV.jpg" group-title="Argentina",NET TV 27.2 - TDA 27.2
https://unlimited1-us.dps.live/nettv/nettv.smil/nettv/livestream1/playlist.m3u8

#EXTINF:-1 tvg-id="NetTV.ar" tvg-country="AR" tvg-logo="https://raw.githubusercontent.com/mortal251/logos/main/NET_TV.jpg" group-title="Argentina",NET TV 27.2 - TDA 27.2
https://unlimited1-buenosaires.dps.live/nettv/nettv.smil/nettv/livestream1/chunks.m3u8

#EXTINF:-1 tvg-id="NetTV.ar" tvg-country="AR" tvg-logo="https://raw.githubusercontent.com/mortal251/logos/main/NET_TV.jpg" group-title="Argentina",NET TV 27.2 - TDA 27.2
https://unlimited1-buenosaires.dps.live/nettv/nettv.smil/playlist.m3u8

#EXTINF:-1 tvg-id="NET TV" tvg-name="NET TV" tvg-logo="https://www.canalnet.tv/_templates/desktop/includes/img/logo.png" group-title="Argentina",NET TV | Argentina - TDA 27.2
https://unlimited1-us.dps.live/nettv/nettv.smil/nettv/livestream2/chunks.m3u8

#EXTINF:-1 tvg-id="NETTV.ar" tvg-logo="https://www.lyngsat-logo.com/logo/tv/nn/net-tv-ar.png" group-title="Argentina",Net TV HD
https://unlimited1-us.dps.live/nettv/nettv.smil/playlist.m3u8
#EXTINF:-1 tvg-id="NETTV.ar" tvg-logo="https://www.lyngsat-logo.com/logo/tv/nn/net-tv-ar.png" group-title="Argentina",Net TV SD1
https://unlimited1-us.dps.live/nettv/nettv.smil/nettv/livestream3/chunks.m3u8
#EXTINF:-1 tvg-id="NETTV.ar" tvg-logo="https://www.lyngsat-logo.com/logo/tv/nn/net-tv-ar.png" group-title="Argentina",Net TV FHD
https://pantera1-100gb-cl-movistar.dps.live/nettv/nettv.smil/playlist.m3u8
#EXTINF:-1 tvg-id="NETTV.ar" tvg-logo="https://www.lyngsat-logo.com/logo/tv/nn/net-tv-ar.png" group-title="Argentina",Net TV SD2
https://pantera1-100gb-cl-movistar.dps.live/nettv/nettv.smil/nettv/livestream2/chunks.m3u8




#EXTINF:-1 tvg-id="N/A" group-title="Argentina" tvg-logo="https://fonts.gstatic.com/s/i/productlogos/lens_camera/v1/192px.svg",Canal Net TV (Argentina)
https://unlimited1-us.dps.live/nettv/nettv.smil/nettv/livestream1/playlist.m3u8


#EXTINF:-1 tvg-logo="https://cmmusica.com.ar/images/logo.png" group-title="Argentina",CM TV | Argentina - TDA 33.1
https://g5.proy-hor.transport.edge-access.net/a09/ngrp:CM_CanaldelaMusica-100044_all/CM_CanaldelaMusica-100044_540p.m3u8








#EXTINF:-1 tvg-id="Canal26.ar" tvg-country="AR" tvg-logo="https://yt3.googleusercontent.com/qiB2U_CZaAY_4IdZydkjJwMxnGCpr0v-tLoJmKrjG0KeqA3rLdj5hQ73jnOIjq2kmUcPajCvCTA=s176-c-k-c0x00ffffff-no-rj" group-title="Argentina", CANAL 26
http://190.11.130.46/mnp/canal26/output.mpd

#EXTINF:-1 tvg-id="Canal26.ar" tvg-country="AR" tvg-logo="https://yt3.googleusercontent.com/qiB2U_CZaAY_4IdZydkjJwMxnGCpr0v-tLoJmKrjG0KeqA3rLdj5hQ73jnOIjq2kmUcPajCvCTA=s176-c-k-c0x00ffffff-no-rj" group-title="Argentina", CANAL 26
https://stream-gtlc.telecentro.net.ar/hls/canal26hls/0/playlist.m3u8

#EXTINF:-1 tvg-id="Canal26.ar" tvg-logo="http://i.imgur.com/m504ZL8.png" group-title="Argentina",Canal 26
http://181.13.173.86:8000/play/a01r/index.m3u8

#KODIPROP:inputstream.adaptive.license_type=org.w3.clearkey
#KODIPROP:inputstream.adaptive.license_key=e32aaa4b67430b3b51be1efce5a74ac5:ad60c5e1d378a97271bf8688f094d092
#EXTINF:-1 tvg-chno="4" tvg-id="Canal26.ar" tvg-name="CAN26" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/CAN26.png?raw=true" tvg-group="Noticias", Canal 26
https://cdn.cvattv.com.ar/live/c6eds/26_TV_HD/SA_Live_dash_enc_2A/26_TV_HD.mpd







#EXTINF:-1 tvg-id="Glitz" tvg-name="Glitz" tvg-logo="https://upload.wikimedia.org/wikipedia/commons/b/b7/Glitzlogo.png" group-title="Argentina",Glitz | Argentina
http://tv.dominiotv.xyz:25461/live/Rolando/Rolando2021/52509.ts
'''

banner2 = r'''







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
        # Pega o ID do canal a partir da URL do YouTube
        youtube_id = extract_youtube_id(line)
        if youtube_id:
            channel_data.append({
                'type': 'link',
                'url': f"https://ythls.armelin.one/channel/{youtube_id}.m3u8"
            })

# Escreve no arquivo .m3u
with open("ARGENTINA.m3u", "w") as f:
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

with open("ARGENTINA.json", "w") as f:
    json_data = json.dumps(channel_data_json, indent=2)
    f.write(json_data)
