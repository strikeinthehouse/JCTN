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




#EXTINF:-1 radio="true" tvg-logo="https://i.imgur.com/HbV9HoX.png" group-title="Argentina",Norte | Bahía Blanca | Argentina
http://icecast.hostingbahia.com.ar:8002/live?28344
#EXTINF:0 tvg-id="ext" group-title="Argentina",Camaras de Villa Gesell (Av. 3 y 104)
http://cam104y3.gesell.com.ar/playlist.m3u8
#EXTINF:0 tvg-id="ext" group-title="Argentina",Camaras de Villa Gesell (Buenos Aires y Playa)
http://cambsasyplaya.gesell.com.ar/playlist.m3u8
#EXTINF:0 tvg-id="ext" group-title="Argentina",Camaras de Villa Gesell (La Pinocha)
http://camlapinocha.gesell.com.ar/playlist.m3u8

#EXTM3U



#EXTINF:-1 group-title="Argentina" tvg-logo="https://i.postimg.cc/xdsxNVXq/609-Canal-Ciudad.png", CANAL DE LA CIUDAD
https://ythlsgo.onrender.com/channel/UCOV_Vx1baZJY9Tfvgm-UI3w.m3u8



#EXTINF:-1 tvg-id="Telemax.ar" tvg-logo="http://tvabierta.weebly.com/uploads/5/1/3/4/51344345/telemax.png" group-title="Argentina", TELEMAX  26.3
https://stream-gtlc.telecentro.net.ar/hls/telemaxhls/0/playlist.m3u8


#EXTINF:-1 tvg-logo="https://www.construirtv.com/wp-content/uploads/2020/03/Logo_300.png" group-title="Argentina", CONSTRUIR TV
https://bvsat02.cdn.rcs.net.ar/mnp/construiriptv/output.mpd



#EXTINF:-1 tvg-id="TyCSports.ar" tvg-logo="https://pbs.twimg.com/profile_images/1571906658581856258/_Yrzet08_400x400.jpg" group-title="Argentina", TyC SPORTS 
https://d3055hobuue3je.cloudfront.net/out/v1/188a8f3baf914a35868453bd5d0b0fd2/index_4.m3u8

#EXTINF:-1 tvg-id="ElGarageTV.ar" tvg-logo="https://lh3.googleusercontent.com/-2gN4wEv_qPI/XjtKDwMuIQI/AAAAAAAAvrY/VTtJwZALBykDRnM8ia0Xbqi0FbREvdrZACK8BGAsYHg/s0/2020-02-05.png" group-title="Argentina", GARAGE TV
https://stream1.sersat.com/hls/garagetv.m3u8

#EXTINF:-1 tvg-id="America TV Argentina" tvg-name="America TV Argentina" tvg-logo="https://imagenes.gatotv.com/logos/canales/oscuros/america_tv_argentina.png" group-title="Argentina",America TV | Argentina - TDA 2.1
#EXTVLCOPT:http-referrer=https://vmf.edge-apps.net
https://prepublish.f.qaotic.net/a07/americahls-100056/Playlist.m3u8

#EXTINF:-1 tvg-id="AmericaTV.ar" tvg-country="AR" tvg-logo="https://raw.githubusercontent.com/mortal251/logos/main/AMERICA.png" group-title="Argentina",America TV | Argentina - TDA 2.1
#EXTVLCOPT:http-referrer=https://vmf.edge-apps.net
https://prepublish.f.qaotic.net/a07/americahls-100056/Playlist.m3u8

#EXTINF:-1 tvg-id="AmericaTV.ar" tvg-country="AR" tvg-logo="https://raw.githubusercontent.com/mortal251/logos/main/AMERICA.png" group-title="Argentina",America TV | Argentina - TDA 2.1
http://cord-cutter.net:8080/live/j3McKd/673709/164881.m3u8

#EXTINF:-1 tvg-id="AmericaTV.ar" tvg-logo="https://www.lyngsat-logo.com/logo/tv/aa/america-tv-ar.png" group-title="Argentina",América TV
http://181.13.173.86:8000/play/a0a7/index.m3u8


#EXTINF:-1 group-title="Argentina" tvg-logo="https://www.m3u.cl/logo/259_Canal_4_Posadas.png",América Canal 4 Posadas | AR
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



#EXTINF:-1 tvg-id="Telefe.ar" tvg-logo="https://cdn.mitvstatic.com/channels/ar_telefe_m.png" group-title="Argentina",Telefe
http://181.13.173.86:8000/play/a06c/index.m3u8
#EXTINF:-1 tvg-id="Telefe.ar" tvg-logo="https://raw.githubusercontent.com/mortal251/logos/main/telefe.jpg" group-title="Argentina",Telefe | Argentina - TDA 11.1
http://181.209.114.13:8000/play/a06c/index.m3u8



#EXTINF:-1 tvg-id="Telefe.ar" tvg-logo="https://telefe-static.akamaized.net/media/18154476/logo-telefe-twitter.png" group-title="Argentina", Telefe (VPN) - TDA 11.1
https://mitelefe.com/Api/Videos/GetSourceUrl/694564/0/HLS

#EXTINF:-1 tvg-id="Telefe.ar" tvg-logo="http://x.playerlatino.live/telefe.png" group-title="Argentina", Telefe (VPN) 2 - TDA 11.1
https://telefe.com/Api/Videos/GetSourceUrl/694564/0/HLS?.m3u8







#EXTINF:-1 group-title="Argentina" tvg-logo="https://i.imgur.com/q6BQ5YO.png",Telefe Canal 7 Jujuy
https://stream.arcast.live/canal7jujuy/ngrp:canal7jujuy_all/playlist.m3u8?PlaylistM3UCL

#EXTINF:-1 group-title="Argentina" tvg-logo="https://www.m3u.cl/logo/251_13_Max_Television.png",Telefe 13 Max Television
http://coninfo.net:1935/13maxhd/live13maxtvnuevo_720p/playlist.m3u8?PlaylistM3UCL

#EXTINF:-1 tvg-id="13Max.ar" tvg-logo="http://i.imgur.com/oSApjUM.png" group-title="Argentina",13 Max HD
http://coninfo.net:1935/13maxhd/live13maxtvnuevo_720p/chunklist_w2131508282.m3u8
#EXTINF:-1 tvg-id="13Max.ar" tvg-logo="http://i.imgur.com/oSApjUM.png" group-title="Argentina",13 Max FHD
http://coninfo.net:1935/13maxhd/live13maxtvnuevo/playlist.m3u8

#EXTINF:-1 tvg-id="13 de Argentina" tvg-name="13 de Argentina" tvg-logo="https://upload.wikimedia.org/wikipedia/commons/4/45/Eltrece_logotipo_2018.png" group-title="Argentina", El Trece - TDA 13.1
https://livetrx01.vodgc.net/eltrecetv/index.m3u8

#EXTINF:-1 tvg-id="13 de Argentina" tvg-name="13 de Argentina" tvg-logo="https://upload.wikimedia.org/wikipedia/commons/4/45/Eltrece_logotipo_2018.png" group-title="Argentina", El Trece - TDA 13.1
http://181.191.140.2:8000/play/a0ir/index.m3u8

#EXTINF:-1 tvg-id="ElTrece.ar" tvg-logo="https://cdn.mitvstatic.com/channels/ar_el-trece_m.png" group-title="Argentina",El Trece
https://live-01-02-eltrece.vodgc.net/eltrecetv/index.m3u8
#EXTINF:-1 tvg-id="ElTrece.ar" tvg-logo="https://cdn.mitvstatic.com/channels/ar_el-trece_m.png" group-title="Argentina",El Trece HD
http://181.13.173.86:8000/play/a06d/index.m3u8

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
#EXTINF:-1 tvg-id="N/A" group-title="Argentina" tvg-logo="https://fonts.gstatic.com/s/i/productlogos/lens_camera/v1/192px.svg",Canal Nueve Multivisión (AR) - TDA 20.1
http://panel.dattalive.com:1935/8250/8250/playlist.m3u8

#EXTINF:-1 tvg-id="N/A" group-title="Argentina" tvg-logo="https://fonts.gstatic.com/s/i/productlogos/lens_camera/v1/192px.svg",Canal Nueve Multivisión (AR) - Feed 1
http://api.new.livestream.com/accounts/679322/events/3782013/live.m3u8

#EXTINF:-1 tvg-id="N/A" group-title="Argentina" tvg-logo="https://fonts.gstatic.com/s/i/productlogos/lens_camera/v1/192px.svg",Canal Nueve Multivisión (AR) - Feed 2
http://panel.dattalive.com:1935/8204/8204/playlist.m3u8

#EXTINF:-1  tvg-id="284" group-title="Argentina" tvg-logo="https://www.m3u.cl/logo/284_Multivision.png",Multivisi n | AR
https://panel.dattalive.com:443/8250/8250/playlist.m3u8?PlaylistM3UCL



#EXTINF:-1 tvg-id="N/A" group-title="Argentina" tvg-logo="https://fonts.gstatic.com/s/i/productlogos/lens_camera/v1/192px.svg",Canal 26 (San Justo-Arg.) - TDA 22.2
http://live-edge01.telecentro.net.ar/live/smil:c26.smil/chunklist_w858131162_b414000_sleng.m3u8

#EXTINF:-1 tvg-id="TECTV.ar" tvg-logo="https://www.tec.gob.ar/wp-content/uploads/2022/05/Tec-logo.png" group-title="Argentina",Tec TV | Argentina - TDA 22.4
https://tv.initium.net.ar:3939/live/tectvmainlive.m3u8




#EXTINF:-1 tvg-id="N/A" group-title="Argentina" tvg-logo="https://www.cxtv.com.br/img/Tvs/Logo/webp-l/d800ee1a28bbee6769de24c5c050c40c.webp",Canal Once - TDA 24.3
https://vivo.canaloncelive.tv/alivepkgr3/ngrp:cepro_all/playlist.m3u8


#EXTINF:-1 tvg-id="Canal 4 Jujuy" tvg-name="Canal 4 Jujuy" tvg-logo="https://s3.amazonaws.com/static-c4-1/assets/img/logos/elcuatro-logo-100x124.png" group-title="Argentina",Canal 4 Jujuy | Argentina - TDA 26.1
https://5cd577a3dd8ec.streamlock.net/canal4/manifest.smil/chunklist_w92188071_b316000.m3u8

#EXTINF:-1 tvg-id="Canal 4 Jujuy" tvg-name="Canal 4 Jujuy" tvg-logo="https://s3.amazonaws.com/static-c4-1/assets/img/logos/elcuatro-logo-100x124.png" group-title="Argentina",Canal 4 Jujuy | Argentina - TDA 26.2
https://5cd577a3dd8ec.streamlock.net/canal4/smil:manifest.smil/chunklist_w1908572533_b316000.m3u8

#EXTINF:-1 tvg-id="N/A" group-title="Argentina" tvg-logo="https://fonts.gstatic.com/s/i/productlogos/lens_camera/v1/192px.svg",Canal 3ABN latino - TDA 32.1
http://uni5rtmp.tulix.tv:1935/bettervida/bettervida/playlist.m3u8


#EXTINF:-1 tvg-id="N/A" group-title="Argentina" tvg-logo="https://fonts.gstatic.com/s/i/productlogos/lens_camera/v1/192px.svg",Canal 5ATV (Argentina)
http://www.coninfo.net:1935/tvcinco/live1/playlist.m3u8



#EXTINF:-1 tvg-id="N/A" group-title="Argentina" tvg-logo="https://fonts.gstatic.com/s/i/productlogos/lens_camera/v1/192px.svg",Canal Fenix TV (Argentina)
http://stmv4.questreaming.com/fenixlarioja/fenixlarioja/playlist.m3u8

#EXTINF:-1 tvg-id="N/A" group-title="Argentina" tvg-logo="https://fonts.gstatic.com/s/i/productlogos/lens_camera/v1/192px.svg",Canal Madryn TV (Argentina)
https://5f700d5b2c46f.streamlock.net/madryntv/madryntv/playlist.m3u8

#EXTINF:-1 tvg-id="N/A" group-title="Argentina" tvg-logo="https://fonts.gstatic.com/s/i/productlogos/lens_camera/v1/192px.svg",Canal Chaco DX (Argentina)
http://arcast.net:1935/mp/mp/playlist.m3u8

#EXTINF:-1 tvg-id="N/A" group-title="Argentina" tvg-logo="https://fonts.gstatic.com/s/i/productlogos/lens_camera/v1/192px.svg",Canal 8250 (Argentina)
https://panel.dattalive.com/8250/8250/playlist.m3u8

#EXTINF:-1 tvg-id="N/A" group-title="Argentina" tvg-logo="https://fonts.gstatic.com/s/i/productlogos/lens_camera/v1/192px.svg",Canal Chaco DX (Argentina) - Feed 2
http://coninfo.net:1935/chacodxdtv/live/playlist.m3u8

#EXTINF:-1 tvg-id="N/A" group-title="Argentina" tvg-logo="https://fonts.gstatic.com/s/i/productlogos/lens_camera/v1/192px.svg",Canal 8250 (Argentina) - Feed 2
http://panel.dattalive.com:1935/8250/8250/playlist.m3u8



#EXTINF:-1 tvg-id="N/A" group-title="Argentina" tvg-logo="https://fonts.gstatic.com/s/i/productlogos/lens_camera/v1/192px.svg",Canal Franz Balboa TV (Bolívia)
https://panel.seo.tv.bo:3337/live/franzbalboa2live.m3u8

#EXTINF:-1 tvg-id="N/A" group-title="Argentina" tvg-logo="https://fonts.gstatic.com/s/i/productlogos/lens_camera/v1/192px.svg",Canal Tastemade (Internacional)
https://tastemade-es8intl-roku.amagi.tv/playlist.m3u8

#EXTINF:-1 tvg-id="N/A" group-title="Argentina" tvg-logo="https://fonts.gstatic.com/s/i/productlogos/lens_camera/v1/192px.svg",Canal Previsora TV (Argentina)
http://www.coninfo.net:1935/previsoratv/live/playlist.m3u8

#EXTINF:-1 tvg-id="N/A" group-title="Argentina" tvg-logo="https://fonts.gstatic.com/s/i/productlogos/lens_camera/v1/192px.svg",Canal Telecentro (Argentina)
http://live-edge01.telecentro.net.ar/live/smil:trm.smil/playlist.m3u8

#EXTINF:-1 tvg-id="N/A" group-title="Argentina" tvg-logo="https://fonts.gstatic.com/s/i/productlogos/lens_camera/v1/192px.svg",Canal IRT (Argentina)
http://cdnh4.iblups.com/hls/irtp.m3u8

#EXTINF:-1 tvg-id="N/A" group-title="Argentina" tvg-logo="https://fonts.gstatic.com/s/i/productlogos/lens_camera/v1/192px.svg",Canal Vallenato (Argentina)
https://59a564764e2b6.streamlock.net/vallenato/Vallenato2/playlist.m3u8

#EXTINF:-1 tvg-id="N/A" group-title="Argentina" tvg-logo="https://fonts.gstatic.com/s/i/productlogos/lens_camera/v1/192px.svg",Canal Vertv (Argentina)
https://5f700d5b2c46f.streamlock.net/vertv/vertv/playlist.m3u8

#EXTINF:-1  tvg-id="N/A" group-title="Argentina" tvg-logo="https://fonts.gstatic.com/s/i/productlogos/lens_camera/v1/192px.svg",Telemax  HD Argent.
http://live-edge01.telecentro.net.ar/live/smil:tlx.smil/chunklist_w950122583_b1828000_sleng.m3u8
#EXTINF:-1  tvg-id="N/A" group-title="Argentina" tvg-logo="https://fonts.gstatic.com/s/i/productlogos/lens_camera/v1/192px.svg",24/7 Canal de Noticias
http://59c5c86e10038.streamlock.net:1935/6605140/6605140/playlist.m3u8?checkedby:iptvcat.com
#EXTINF:-1  tvg-id="N/A" group-title="Argentina" tvg-logo="https://fonts.gstatic.com/s/i/productlogos/lens_camera/v1/192px.svg",5RTV Santa Fe
http://api.new.livestream.com/accounts/22636012/events/8242619/live.m3u8?checkedby:iptvcat.com
#EXTINF:-1  tvg-id="N/A" group-title="Argentina" tvg-logo="https://fonts.gstatic.com/s/i/productlogos/lens_camera/v1/192px.svg",5TV (Corrientes) (480p)
http://www.coninfo.net:1935/tvcinco/live1/playlist.m3u8?checkedby:iptvcat.com
#EXTINF:-1  tvg-id="N/A" group-title="Argentina" tvg-logo="https://fonts.gstatic.com/s/i/productlogos/lens_camera/v1/192px.svg",5TV Corrientes
http://www.coninfo.net:1935/tvcinco/live1/chunklist_w1546509083.m3u8?checkedby:iptvcat.com
#EXTINF:-1  tvg-id="N/A" group-title="Argentina" tvg-logo="https://fonts.gstatic.com/s/i/productlogos/lens_camera/v1/192px.svg",Ciudad TV Chaco
http://coninfo.net:1935/chacodxdtv/live/chunklist_w1251301598.m3u8?checkedby:iptvcat.com
#EXTINF:-1  tvg-id="N/A" group-title="Argentina" tvg-logo="https://fonts.gstatic.com/s/i/productlogos/lens_camera/v1/192px.svg",Music TOP
http://live-edge01.telecentro.net.ar/live/smil:musictop.smil/chunklist_w1582140541_b364000_sleng.m3u8?checkedby:iptvcat.com
#EXTINF:-1  tvg-id="N/A" group-title="Argentina" tvg-logo="https://fonts.gstatic.com/s/i/productlogos/lens_camera/v1/192px.svg",Music Top
http://live-edge01.telecentro.net.ar/live/smil:musictop.smil/chunklist_w538311571_b364000_sleng.m3u8?checkedby:iptvcat.com
#EXTINF:-1  tvg-id="277" group-title="Argentina" tvg-logo="https://www.m3u.cl/logo/277_Canal_XFN.png",Canal XFN * | AR
https://streamconex.com:1936/canalxfn/canalxfn/playlist.m3u8?PlaylistM3UCL
#EXTINF:-1  tvg-id="1026" group-title="Argentina" tvg-logo="https://www.m3u.cl/logo/1026_Tele_Mix.png",Tele Mix * | AR
https://panel.dattalive.com:443/8068/8068/playlist.m3u8?PlaylistM3UCL
#EXTINF:-1  tvg-id="249" group-title="Argentina" tvg-logo="https://www.m3u.cl/logo/249_5TV.png",5TV | AR
http://www.coninfo.net:1935/tvcinco/live1/playlist.m3u8?PlaylistM3UCL
#EXTINF:-1  tvg-id="215" group-title="Argentina" tvg-logo="https://www.m3u.cl/logo/215_Azahares_Radio_Multimedia.png",Azahares Radio Multimedia | AR
http://streamyes.alsolnet.com/azaharesfm/live/playlist.m3u8?PlaylistM3UCL
#EXTINF:-1  tvg-id="224" group-title="Argentina" tvg-logo="https://www.m3u.cl/logo/224_Cadena_103.png",Cadena 103 | AR
http://arcast.net:1935/cadena103/cadena103/playlist.m3u8?PlaylistM3UCL
#EXTINF:-1  tvg-id="299" group-title="Argentina" tvg-logo="https://www.m3u.cl/logo/299_Canal_10_Rio_Negro.png",Canal 10 Rio Negro | AR
https://panel.dattalive.com:443/8204/8204/playlist.m3u8?PlaylistM3UCL
#EXTINF:-1  tvg-id="268" group-title="Argentina" tvg-logo="https://www.m3u.cl/logo/268_Canal_12_Madryn_TV.png",Canal 12 Madryn TV | AR
https://5f700d5b2c46f.streamlock.net:443/madryntv/madryntv/playlist.m3u8?PlaylistM3UCL
#EXTINF:-1  tvg-id="227" group-title="Argentina" tvg-logo="https://www.m3u.cl/logo/227_Canal_13_La_Rioja.jpg",Canal 13 La Rioja | AR
http://arcast.net:1935/mp/mp/playlist.m3u8?PlaylistM3UCL
#EXTINF:-1  tvg-id="228" group-title="Argentina" tvg-logo="https://www.m3u.cl/logo/228_Canal_2_Jujuy.png",Canal 2 Jujuy | AR
http://api.new.livestream.com/accounts/679322/events/3782013/live.m3u8?PlaylistM3UCL
#EXTINF:-1  tvg-id="230" group-title="Argentina" tvg-logo="https://www.m3u.cl/logo/230_Canal_22_Buenos_Aires.jpg",Canal 22 Buenos Aires | AR
https://5f700d5b2c46f.streamlock.net:443/canal22/canal22/playlist.m3u8?PlaylistM3UCL
#EXTINF:0 group-title="Argentina" tvg-logo="https://mediakit.perfil.com/img/canal-e-logo.png",CANAL E - PERFIL TV
https://unlimited1-buenosaires.dps.live/perfiltv/perfiltv.smil/playlist.m3u8

#EXTINF:-1  tvg-id="273" group-title="Argentina" tvg-logo="https://www.m3u.cl/logo/273_Canal_907_FM_Comunicar.png",Canal 907 FM Comunicar | AR
https://panel.dattalive.com/canal907/canal907/chunklist_w1205944599.m3u8?PlaylistM3UCL
#EXTINF:-1  tvg-id="275" group-title="Argentina" tvg-logo="https://www.m3u.cl/logo/275_Canal_Coop.png",Canal Coop | AR
https://panel.dattalive.com:443/8138/8138/playlist.m3u8?PlaylistM3UCL
#EXTINF:-1  tvg-id="237" group-title="Argentina" tvg-logo="https://www.m3u.cl/logo/237_Ciudad_TV.jpg",Ciudad TV | AR
http://coninfo.net:1935/chacodxdtv/live/chunklist_w1251301598.m3u8?PlaylistM3UCL
#EXTINF:-1  tvg-id="239" group-title="Argentina" tvg-logo="https://www.m3u.cl/logo/239_Fenix.jpg",Fenix | AR
https://stmvideo1.livecastv.com/fenixlarioja/fenixlarioja/playlist.m3u8?PlaylistM3UCL
#EXTINF:-1  tvg-id="212" group-title="Argentina" tvg-logo="https://www.m3u.cl/logo/212_Link_TV.png",Link TV | AR
https://panel.dattalive.com:443/8128_1/8128_1/playlist.m3u8?PlaylistM3UCL
#EXTINF:-1  tvg-id="795" group-title="Argentina" tvg-logo="https://www.m3u.cl/logo/795_Metropolitana_FM.png",Metropolitana FM | AR
https://panel.dattalive.com/MetropolitanaFM/MetropolitanaFM/playlist.m3u8?PlaylistM3UCL

#EXTINF:-1  tvg-id="243" group-title="Argentina" tvg-logo="https://www.m3u.cl/logo/243_Power.png",Power | AR
https://live2.tensila.com/1-1-1.power-tv/hls/master.m3u8?PlaylistM3UCL
#EXTINF:-1  tvg-id="210" group-title="Argentina" tvg-logo="https://www.m3u.cl/logo/210_Radiocanal_San_Francisco.png",Radiocanal San Francisco | AR
http://204.199.3.2/.m3u8?PlaylistM3UCL
#EXTINF:-1  tvg-id="308" group-title="Argentina" tvg-logo="https://www.m3u.cl/logo/308_Tele_Estrella.png",Tele Estrella | AR
https://stmvideo2.livecastv.com/telestrella/telestrella/playlist.m3u8?PlaylistM3UCL

#EXTINF:-1  tvg-id="245" group-title="Argentina" tvg-logo="https://www.m3u.cl/logo/245_Telediez.jpg",Telediez | AR
https://videohd.live:19360/8020/8020.m3u8?PlaylistM3UCL
#EXTINF:-1  tvg-id="814" group-title="Argentina" tvg-logo="https://www.m3u.cl/logo/814_TeleNord.jpg",TeleNord | AR
http://www.coninfo.net:1935/previsoratv/live/playlist.m3u8?PlaylistM3UCL
#EXTINF:-1  tvg-id="248" group-title="Argentina" tvg-logo="https://www.m3u.cl/logo/248_Uni_Teve.png",Uni Teve | AR
https://vivo.solumedia.com:19360/uniteve/uniteve.m3u8?PlaylistM3UCL
#EXTINF:-1  tvg-id="1003" group-title="Argentina" tvg-logo="https://www.m3u.cl/logo/1003_Sublime_Gracia_TV.png",Sublime Gracia TV | AR
https://5f700d5b2c46f.streamlock.net:443/sublime/sublime/playlist.m3u8?PlaylistM3UCL

#EXTINF:-1 group-title="Argentina",Litus HD Argentina
http://192.99.38.174:1935/litustv/ngrp:litustv_all/playlist.m3u8

#EXTINF:-1 group-title="Argentina",Canal 6 Posadas | AR
https://iptv.ixfo.com.ar:30443/live/c6digital/playlist.m3u8?PlaylistM3UCL


#EXTINF:-1 group-title="Argentina",Canal 21 TV | AR
https://iptv.ixfo.com.ar:30443/c21tv/hd/c21tv/playlist.m3u8?PlaylistM3UCL
#EXTINF:-1 group-title="Argentina",Canal 22 Buenos Aires | AR
https://5f700d5b2c46f.streamlock.net:443/canal22/canal22/playlist.m3u8?PlaylistM3UCL

#EXTINF:-1 group-title="Argentina",Canal 12 Madryn TV | AR
https://5f700d5b2c46f.streamlock.net:443/madryntv/madryntv/playlist.m3u8?PlaylistM3UCL
#EXTINF:-1 group-title="Argentina",Canal 13 La Rioja | AR
http://arcast.net:1935/mp/mp/playlist.m3u8?PlaylistM3UCL

#EXTINF:-1 group-title="Argentina",Azahares Radio Multimedia | AR
http://streamyes.alsolnet.com/azaharesfm/live/playlist.m3u8?PlaylistM3UCL
#EXTINF:-1 group-title="Argentina",5R TV Santa Fe | AR
http://api.new.livestream.com/accounts/22636012/events/8242619/live.m3u8?PlaylistM3UCL
#EXTINF:-1 group-title="Argentina",5TV | AR
http://www.coninfo.net:1935/tvcinco/live1/playlist.m3u8?PlaylistM3UCL

#EXTINF:-1 tvg-id="Neo TV" tvg-name="Neo TV" tvg-logo="https://neotvdigital.com.ar/wp-content/uploads/2022/07/Logo-Neo-Tv.png" group-title="Argentina",Neo TV | Argentina
https://videostream.shockmedia.com.ar:19360/neotvdigital/neotvdigital.m3u8

#EXTINF:-1 group-title="Argentina",Canal Provincial | AR
https://streaming.telered.com.ar/provincial/streaming/mystream.m3u8?PlaylistM3UCL
#EXTINF:-1 group-title="Argentina",Sublime Gracia TV | AR
https://5f700d5b2c46f.streamlock.net:443/sublime/sublime/playlist.m3u8?PlaylistM3UCL











#KODIPROP:inputstream.adaptive.license_type=org.w3.clearkey
#KODIPROP:inputstream.adaptive.license_key=f4eade7bbc39b25402acfa301bbad04a:a74d1df4235a74878327aa8d53ff283c
#EXTINF:-1 tvg-chno="6" tvg-id="LaNacionPlus.ar" tvg-name="LNAC+" tvg-logo="https://git.io/J35ry" tvg-group="Noticias", La Nación +
https://chromecast.cvattv.com.ar/live/c7eds/La_Nacion/SA_Live_dash_enc_2A/La_Nacion.mpd





#EXTINF:-1 tvg-chno="9" tvg-id="CanalE" tvg-current-title="Programación Canal E" tvg-logo="https://www.perfil.com/img/minisitios/econocanal/logo.png" tvg-group="Noticias", Canal E
https://unlimited1-buenosaires.dps.live/perfiltv/perfiltv.smil/playlist.m3u8

#EXTINF:-1 tvg-chno="10"tvg-name="NGFED" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/NGFE.png?raw=true" tvg-group="Noticias", Norte Grande Federal
http://www.coninfo.net:1935/tvlink/live/playlist.m3u8

#EXTINF:-1 tvg-chno="11" tvg-id="" tvg-logo="https://multivision.tv/wp-content/uploads/2024/04/LOGO-MONEDA.png" tvg-group="Noticias", Multivisión Federal
https://panel.host-live.com:443/8250/8250/playlist.m3u8

#KODIPROP:inputstream.adaptive.license_type=org.w3.clearkey
#KODIPROP:inputstream.adaptive.license_key=0b20ed9da0e5457c9dfd3ae0b6092491:98997a7020c18cb28174a2490147830a
#EXTINF:-1 tvg-chno="821" tvg-id="CNNenEspanol.us" tvg-name="CNNEE" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/CNNEE.png?raw=true" group-title="Mundo", CNN En Español
https://chromecast.cvattv.com.ar/live/c6eds/CNN_en_Espanol/SA_Live_dash_enc_2A/CNN_en_Espanol.mpd
























#EXTINF:-1 tvg-id="DeporTV.ar" tvg-logo="https://www.lyngsat-logo.com/logo/tv/dd/deportv-ar.png" group-title="Argentina",DeporTV
http://181.13.173.86:8000/play/a06h/index.m3u8









#EXTINF:-1 tvg-chno="313" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/CLANI.png?raw=true" tvg-group="Infantiles y Familiares", Clan
https://rtvelivestream.akamaized.net/rtvesec/int/clan_int_main_dvr.m3u8



#EXTINF:-1 tvg-chno="413" tvg-id="" tvg-logo="https://www.canalcinemaplus.net/wp-content/uploads/2013/07/logo.png" group-title="Variedades", Cinema+
https://byecableiptvnew3.ddns.net/ENVIVOCINEMA/tracks-v1a1/mono.m3u8

#EXTINF:-1 tvg-chno="517" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/TVEST.png?raw=true" tvg-group="Variedades", Star TVE
https://rtvelivestream.akamaized.net/rtvesec/int/star_main_dvr.m3u8


#EXTINF:-1 tvg-chno="515" tvg-id="" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/UCLTV.png?raw=true" group-title="Variedades", UCL
https://livedelta.cdn.antel.net.uy/out/u/url_canalu.m3u8

#KODIPROP:inputstream.adaptive.license_type=org.w3.clearkey
#KODIPROP:inputstream.adaptive.license_key=ac3ae78beb64478ab390b4ad70e3e0c9:c7d669761c3516d852a0edf9e07c9198


#EXTINF:-1 tvg-chno="703" tvg-id="TECTV.ar" tvg-logo="https://www.tec.gob.ar/wp-content/uploads/2022/05/Tec-logo.png" group-title="Culturales", TEC
https://vd01.streaminghd.net.ar:3787/live/jcslppmtlive.m3u8



#EXTINF:-1 tvg-chno="716" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/INTI.png?raw=true" group-title="Culturales", INTI
https://5e2f36bc1c433.streamlock.net/inti/inti-network.stream/chunklist.m3u8




#EXTINF:-1 tvg-chno="802" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/TVE24.png?raw=true" group-title="Mundo", 24 Horas (España)
https://ztnr.rtve.es/ztnr/1694255.m3u8



#EXTINF:-1 tvg-chno="806" tvg-id="CGTNSpanish.cn" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/CGTNE.png?raw=true" group-title="Mundo", CGTN
https://livees.cgtn.com/1000e/prog_index.m3u8

#EXTINF:-1 tvg-chno="807" tvg-id="DWEspanol.de" tvg-logo="https://git.io/JOTLM" group-title="Mundo", Deutsche Welle
https://dwamdstream104.akamaized.net/hls/live/2015530/dwstream104/index.m3u8

#EXTINF:-1 tvg-chno="819" tvg-id="Telesur.ve" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/TLSUR.png?raw=true" group-title="Mundo", TeleSUR
https://cdnesmain.telesur.ultrabase.net/mbliveMain/hd/chunklist.m3u8




#EXTINF:-1 tvg-chno="809" tvg-id="NHKWorldJapan.jp" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/NHKWJ.png?raw=true" group-title="Mundo", NHK World Japan 
https://cdn.nhkworld.jp/www11/nhkworld-tv/bmcc-live/es/playlist.m3u8


#EXTINF:-1 tvg-chno="822" tvg-id="CNNInternationalLatinAmerica.us" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/CNNIN.png?raw=true" group-title="Mundo", CNN Internacional
https://cnn-cnninternational-1-eu.rakuten.wurl.tv/playlist.m3u8

#KODIPROP:inputstream.adaptive.license_type=org.w3.clearkey
#KODIPROP:inputstream.adaptive.license_key=3fe3f31a5e7b48a1b548e9364757ce66:32993fc281207fe915f6f1e990957868
#EXTINF:-1 tvg-chno="824" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/FOXNW.png?raw=true" group-title="Mundo", FOX News
https://edge-live16-sl.cvattv.com.ar/live/c6eds/Fox_News/SA_Live_dash_enc/Fox_News.mpd

#EXTINF:-1 tvg-chno="825" tvg-id="TRTWorld.tr" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/TRTWR.png?raw=true" tvg-group="Mundo", TRT World
https://tv-trtworld.live.trt.com.tr:443/master_720.m3u8

#KODIPROP:inputstream.adaptive.license_type=org.w3.clearkey
#KODIPROP:inputstream.adaptive.license_key=d86b0f56d32f45adb0a6b4e488c8f0c2:e4f180b0e61be3e80ab602df5e56ff3f
#EXTINF:-1 tvg-chno="826" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/EURON.png?raw=true" group-title="Mundo", Euronews
https://cdn.cvattv.com.ar/live/c6eds/Euronews/SA_Live_dash_enc/Euronews.mpd

#EXTINF:-1 tvg-chno="804" tvg-id="GaliciaTVAmerica.es" tvg-logo="https://static.flow.com.ar/images/729/CH_LOGO/350/500/0/0/778293230765.png" group-title="Mundo", Galicia TV America
https://crtvg-america.flumotion.cloud/playlist.m3u8

#EXTINF:-1 tvg-chno="805" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/EITBB.png?raw=true" group-title="Mundo", Etb Basque
https://multimedia.eitb.eus/live-content/eitbbasque-hls/master.m3u8

#KODIPROP:inputstream.adaptive.license_type=org.w3.clearkey
#KODIPROP:inputstream.adaptive.license_key=d214547d7d9a4011a39a899ce6e70071:16c2ed0617cf1e123f3af6ea8875a82d
#EXTINF:-1 tvg-chno="810" tvg-id="RaiItaliaAmerica.it" tvg-logo="https://static.flow.com.ar/images/716/CH_LOGO/1920/1080/0/0/577119940729.png" group-title="Mundo", RAI Italia
https://chromecast.cvattv.com.ar/live/c6eds/RAI/SA_Live_dash_enc_2A/RAI.mpd

#EXTINF:-1 tvg-chno="811" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/RTPIN.png?raw=true" tvg-group="Mundo", RTP Internacional
https://streaming-live.rtp.pt/liverepeater/rtpi.smil/.m3u8



#EXTINF:-1 tvg-chno="814" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/BOTV.png?raw=true" tvg-group="Mundo", Bolivia TV
https://video1.getstreamhosting.com:1936/8224/8224/playlist.m3u8

#KODIPROP:inputstream.adaptive.license_type=org.w3.clearkey
#KODIPROP:inputstream.adaptive.license_key=68a5bd6c58e6c05bacfd18d3feec31f2:ae23f8357512df2dfabcb8104b078182
#EXTINF:-1 tvg-chno="815" tvg-id="" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/PYTV.png?raw=true" group-title="Mundo", Paraguay TV
https://chromecast.cvattv.com.ar/live/c7eds/Paraguay_TV/SA_Live_dash_enc_2A/Paraguay_TV.mpd

#KODIPROP:inputstream.adaptive.license_type=org.w3.clearkey
#KODIPROP:inputstream.adaptive.license_key=1211d1dba12d213a033be86bf5654c04:6cf032c1e40195189f39d91500743c64
#EXTINF:-1 tvg-chno="816" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/CCINT.png?raw=true" group-title="Mundo", Caracol Internacional
https://latamvosliveclarovideo.akamaized.net/Content/DASH_DASH_FK/Live/Channel(CARACOL_INT)/manifest.mpd

#EXTINF:-1 tvg-chno="817" tvg-id="" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/TVPEI.png?raw=true" group-title="Mundo", TV Perú Internacional
https://cdnhd.iblups.com/hls/ee2450c81e554f4cae0e6292106993c2.m3u8

#EXTINF:-1 tvg-chno="818" tvg-id="" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/AZINT.png?raw=true" tvg-group="Mundo", Azteca Internacional
https://dujft6o2exhah.cloudfront.net/v1/master/3722c60a815c199d9c0ef36c5b73da68a62b09d1/cc-0lvc4h1b07aou/mun.m3u8


#KODIPROP:inputstream.adaptive.license_type=org.w3.clearkey
#KODIPROP:inputstream.adaptive.license_key=b37d85be9d2b4b619f945beff713fda3:917309c98f072b0bd484dd6560c6d166
#EXTINF:-1 tvg-chno="901" tvg-id="LasEstrellasLatinAmerica.mx" tvg-logo="https://static.flow.com.ar/images/670/CH_LOGO/350/500/0/0/74835190079.png" group-title="Mundo", Las Estrellas
https://chromecast.cvattv.com.ar/live/c6eds/Canal_de_las_estrellas/SA_Live_dash_enc_2A/Canal_de_las_estrellas.mpd

#KODIPROP:inputstream.adaptive.license_type=org.w3.clearkey
#KODIPROP:inputstream.adaptive.license_key=34cdc6269c656c6994d86ee9cbbcdc6c:b24f4c3fb57f95854d3b2568ee16fda8
#EXTINF:-1 tvg-chno="902" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/UNVSN.png?raw=true" group-title="Mundo", Univisión
https://latamvosliveclarovideo.akamaized.net/Content/DASH_DASH_FK/Live/Channel(UNICABLEHD_ARG)/manifest.mpd

#KODIPROP:inputstream.adaptive.license_type=org.w3.clearkey
#KODIPROP:inputstream.adaptive.license_key=53d752e4649dadd808d913985f86ee77:d1fd24db1b61d634cabfc44538ce9b0e
#EXTINF:-1 tvg-chno="903" tvg-logo="https://git.io/JOTtz" group-title="Estilos de Vida", Telemundo Internacional
https://chromecast.cvattv.com.ar/live/c7eds//Telemundo_HD/SA_Live_dash_enc_2A/Telemundo_HD.mpd

#KODIPROP:inputstream.adaptive.license_type=org.w3.clearkey
#KODIPROP:inputstream.adaptive.license_key=9b0a76dd7a0df1e1b4320aeb1254d1a9:d011267775c38d6d2ab09b428c03d63f
#EXTINF:-1 tvg-chno="904" tvg-id="DiscoveryHomeHealthSouth.us" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/DSH&H.png?raw=true" group-title="Estilos de Vida", Discovery Home And Health
https://chromecast.cvattv.com.ar/live/c3eds/DiscoveryHomeHealthHD/SA_Live_dash_enc_2A/DiscoveryHomeHealthHD.mpd


#KODIPROP:inputstream.adaptive.license_type=org.w3.clearkey
#KODIPROP:inputstream.adaptive.license_key=58761c7b2819491eb3a0d765842c341a:9dabc48f88bd7f266734e57501bd6f47
#EXTINF:-1 tvg-chno="905" tvg-id="TLCSouth.us" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/DSTLC.png?raw=true" group-title="Estilos de Vida", TLC
https://chromecast.cvattv.com.ar/live/c6eds/TLC/SA_Live_dash_enc_2A/TLC.mpd

#KODIPROP:inputstream.adaptive.license_type=org.w3.clearkey
#KODIPROP:inputstream.adaptive.license_key=5d759477f0ad1bdef2c6de09e7c275fd:82cc6eea185eecc934df95adfbbf9dbc
#EXTINF:-1 tvg-chno="906" tvg-id="HolaTVLatinAmerica.es" tvg-logo="https://mma.prnewswire.com/media/1199606/HOLA_TV_Logo.jpg" group-title="Estilos de Vida", Hola! TV
https://chromecast.cvattv.com.ar/live/c7eds/Hola_TV/SA_Live_dash_enc_2A/Hola_TV.mpd

#EXTINF:-1 tvg-chno="907" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/CARAS.png?raw=true" group-title="Estilos de Vida", Caras TV
https://unlimited1-buenosaires.dps.live/carastv/carastv.smil/playlist.m3u8


#KODIPROP:inputstream.adaptive.license_type=org.w3.clearkey
#KODIPROP:inputstream.adaptive.license_key=49a0179b034ae899cb67d8a5834181aa:486e2c6d69adea7e17f2960e8e366612
#EXTINF:-1 tvg-chno="908" tvg-id="TBSSouth.us" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/TNTNO.png?raw=true" group-title="Estilos de Vida", TNT Novelas
https://chromecast.cvattv.com.ar/live/c6eds/TBS/SA_Live_dash_enc_2A/TBS.mpd


#KODIPROP:inputstream.adaptive.license_type=org.w3.clearkey
#KODIPROP:inputstream.adaptive.license_key=dac8ff1688994efd898222acdd05cafc:22fdf97c7233667518258ed16ccb2545
#EXTINF:-1 tvg-chno="909" tvg-id="MasChicPanregional.ar" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/MCHIC.png?raw=true" group-title="Estilos de Vida", Más Chic
https://chromecast.cvattv.com.ar/live/c6eds/Mas_Chic/SA_Live_dash_enc_2A/Mas_Chic.mpd


#KODIPROP:inputstream.adaptive.license_type=org.w3.clearkey
#KODIPROP:inputstream.adaptive.license_key=5883553207f13e3dc8cecd1113d5ba68:45434d40636dfa0e5312b93218e02185
#EXTINF:-1 tvg-chno="910" tvg-id="EHDSouth.us" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/ENTMN.png?raw=true" group-title="Estilos de Vida", E!
https://chromecast.cvattv.com.ar/live/c6eds/E_Entertainment_Television/SA_Live_dash_enc_2A/E_Entertainment_Television.mpd


#KODIPROP:inputstream.adaptive.license_type=org.w3.clearkey
#KODIPROP:inputstream.adaptive.license_key=6ca0fbad21a0e908c0280dcc27e6ee0e:62670eedbafdf9360b4ecaed738e26cd
#EXTINF:-1 tvg-chno="911" tvg-id="FoodNetworkPanregional.us" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/FDNET.png?raw=true" group-title="Estilos de Vida", Food Network
https://chromecast.cvattv.com.ar/live/c6eds/Food_Network/SA_Live_dash_enc_2A/Food_Network.mpd


#KODIPROP:inputstream.adaptive.license_type=org.w3.clearkey
#KODIPROP:inputstream.adaptive.license_key=93d853ac4c8e24cf0295f6f97ee53bd3:fa5817fab4fb054ccea1abb9f3d767ed
#EXTINF:-1 tvg-chno="912" tvg-id="ElGourmetSouth.ar" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/GRMT.png?raw=true" group-title="Estilos de Vida", El Gourmet
https://chromecast.cvattv.com.ar/live/c3eds/Gourmet/SA_Live_dash_enc_2A/Gourmet.mpd


#KODIPROP:inputstream.adaptive.license_type=org.w3.clearkey
#KODIPROP:inputstream.adaptive.license_key=eae51b1d67ff47adac7b6bd3a4b1120a:b4d6bb47193f33ffc12379cdc447455d
#EXTINF:-1 tvg-chno="913" tvg-id="LifetimePanregional.us" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/LFTME.png?raw=true" group-title="Estilos de Vida", Lifetime
https://chromecast.cvattv.com.ar/live/c6eds/Lifetime/SA_Live_dash_enc_2A/Lifetime.mpd

#EXTINF:-1 tvg-chno="915" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/KDRAM.png?raw=true" group-title="Estilos de Vida", Kanal D Drama
https://cdn-uw2-prod.tsv2.amagi.tv/linear/amg01602-themahqfrance-vivekanald-samsungspain/playlist.m3u8

#EXTINF:-1 tvg-chno="916" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/CLIC.png?raw=true" group-title="Estilos de Vida", Clic
https://stream.ads.ottera.tv/playlist.m3u8?network_id=4827

#KODIPROP:inputstream.adaptive.license_type=org.w3.clearkey
#KODIPROP:inputstream.adaptive.license_key=43bc6a87ee4f21aa320ba00b980a6fd8:bd55130539a30faa1d90b3142eebe0b2
#EXTINF:-1 tvg-chno="914" tvg-id="" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/DHGTV.png?raw=true" group-title="Religión", HGTV
https://cdn.cvattv.com.ar/live/c7eds/Home_and_Garden/SA_Live_dash_enc/Home_and_Garden.mpd

#KODIPROP:inputstream.adaptive.license_type=org.w3.clearkey
#KODIPROP:inputstream.adaptive.license_key=07df3c48652a431ab779d133f085b799:ee2fbeec1ecdffa5617383f684dfda0e
#EXTINF:-1 tvg-chno="1001" tvg-id="EWTNEspanaLatinAmerica.us" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/EWTNE.png?raw=true" group-title="Religión", EWTN
https://chromecast.cvattv.com.ar/live/c6eds/EWTN/SA_Live_dash_enc_2A/EWTN.mpd

#KODIPROP:inputstream.adaptive.license_type=org.w3.clearkey
#KODIPROP:inputstream.adaptive.license_key=29ccae9b98d74e76b35ac4e9a7fd1af1:cd6f0d4dca0fc30533e845fc8ea6a945
#EXTINF:-1 tvg-chno="1002" tvg-id="CanalOrbe21.ar" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/CAN21.png?raw=true" group-title="Religión", Orbe 21
https://chromecast.cvattv.com.ar/live/c6eds/Canal_21/SA_Live_dash_enc_2A/Canal_21.mpd

#EXTINF:-1 tvg-chno="1003" tvg-id="" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/ENLCE.png?raw=true" group-title="Religión", Enlace
https://livecdn.enlace.plus/enlace/smil:enlace-fhd.smil/playlist.m3u8

#EXTINF:-1 tvg-chno="1004" tvg-id="" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/CALUZ.png?raw=true" group-title="Religión", Canal Luz
https://g4.proy-hor.transport.edge-access.net/a11/ngrp:canal_luz01-100009_all/Playlist.m3u8?sense=true

#KODIPROP:inputstream.adaptive.license_type=org.w3.clearkey
#KODIPROP:inputstream.adaptive.license_key=0c9eb3ead38a122ac460ad96a8ebfd2e:66bfbfa4449eb8bc1bcf7577d5bffaad
#EXTINF:-1 tvg-chno="1101" tvg-id="MTVSouth.us" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/MTVLA.png?raw=true" group-title="Música y Radios", MTV
https://chromecast.cvattv.com.ar/live/c6eds/MTV_HD/SA_Live_dash_enc_2A/MTV_HD.mpd

#KODIPROP:inputstream.adaptive.license_type=clearkey
#KODIPROP:inputstream.adaptive.license_key=c18b6aa739be4c0b774605fcfb5d6b68:e41c3a6f7532b2e3a828d9580124c89d
#EXTINF:-1 tvg-chno="1102" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/MTV80.png?raw=true" tvg-aspect-ratio=4:3 aspect-ratio=4:3 group-title="Música y Radios", MTV 80s
https://webtvstream.bhtelecom.ba/hls18/mtv_80s.mpd

#KODIPROP:inputstream.adaptive.license_type=org.w3.clearkey
#KODIPROP:inputstream.adaptive.license_key=1f0c09ed9e5841cf867ba6eb3cdfd61d:802c89c6bae6a245aaafcf40c1986fc1
#EXTINF:-1 tvg-chno="1104" tvg-id="MTV00s.uk" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/MTV00.png?raw=true" group-title="Música y Radios", MTV 00s
https://chromecast.cvattv.com.ar/live/c7eds/MTV00/SA_Live_dash_enc_2A/MTV00.mpd

#KODIPROP:inputstream.adaptive.license_type=clearkey
#KODIPROP:inputstream.adaptive.license_key=c18b6aa739be4c0b774605fcfb5d6b68:e41c3a6f7532b2e3a828d9580124c89d
#EXTINF:-1 tvg-chno="1103" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/MTV90.png?raw=true" group-title="Música y Radios", MTV 90s
https://webtvstream.bhtelecom.ba/hls16/mtv_90s.mpd

#KODIPROP:inputstream.adaptive.license_type=clearkey
#KODIPROP:inputstream.adaptive.license_key=c18b6aa739be4c0b774605fcfb5d6b68:e41c3a6f7532b2e3a828d9580124c89d
#EXTINF:-1 tvg-chno="1105" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/CLMTV.png?raw=true" group-title="Música y Radios", Club MTV
https://webtvstream.bhtelecom.ba/hls19/club_mtv.mpd

#KODIPROP:inputstream.adaptive.license_type=org.w3.clearkey
#KODIPROP:inputstream.adaptive.license_key=61008dfc867544cd872de99b1f2b82cf:716449756316b91c54803aaa22a2fbf0
#EXTINF:-1 tvg-chno="1107" tvg-id="MTVHitsEurope.uk" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/MTVHS.png?raw=true" group-title="Música y Radios", MTV Hits
https://chromecast.cvattv.com.ar/live/c6eds/MTV_Hits/SA_Live_dash_enc_2A/MTV_Hits.mpd

#EXTINF:-1 tvg-chno="1108" tvg-id="" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/RLATV.png?raw=true" group-title="Música y Radios", Latina TV
https://stream-gtlc.telecentro.net.ar/hls/latinatvhls/main.m3u8

#KODIPROP:inputstream.adaptive.license_type=org.w3.clearkey
#KODIPROP:inputstream.adaptive.license_key=a354b0c82a3a720c4a6f52ed5a1190f4:45a76dcc84f058cfabc8b958d7303b28
#EXTINF:-1 tvg-chno="1109" tvg-id="QuieroMusicaenmiIdioma.ar" tvg-logo="https://static.flow.com.ar/images/715/CH_LOGO/1920/1080/0/0/80393273073281.png" group-title="Música y Radios", Quiero Musica
https://chromecast.cvattv.com.ar/live/c6eds/Quiero_HD/SA_Live_dash_enc_2A/Quiero_HD.mpd


#KODIPROP:inputstream.adaptive.license_type=org.w3.clearkey
#KODIPROP:inputstream.adaptive.license_key=682f36b5736f4560951ca14b80d29524:3accb729067a39b3b8143f1b447b9d25
#EXTINF:-1 tvg-chno="1110" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/CMMUS.png?raw=true" group-title="Música y Radios", CM
https://chromecast.cvattv.com.ar/live/c6eds/CM/SA_Live_dash_enc_2A/CM.mpd



#KODIPROP:inputstream.adaptive.license_type=org.w3.clearkey
#KODIPROP:inputstream.adaptive.license_key=daecef5fe32f4ce083c6a0c692755d6a:d4227f24389a9ba77293214b93eb0d7d
#EXTINF:-1 tvg-chno="1111" tvg-id="HTV.us" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/HTVLA.png?raw=true" group-title="Música y Radios", HTV
https://chromecast.cvattv.com.ar/live/c6eds/HTV/SA_Live_dash_enc_2A/HTV.mpd

#KODIPROP:inputstream.adaptive.license_type=org.w3.clearkey
#KODIPROP:inputstream.adaptive.license_key=eabe2c22350c26c7f0ad84b34932f08d:39fa06836ec0f81d8dd9b6e01a3070e3
#EXTINF:-1 tvg-chno="1115" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/VTRIX.png?raw=true" group-title="Música y Radios", Vorterix
https://chromecast.cvattv.com.ar/live/c6eds/Vorterix/SA_Live_dash_enc_2A/Vorterix.mpd

#EXTINF:-1 tvg-chno="1114" tvg-id="MusicTop.ar" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/MSTOP.png?raw=true" group-title="Música y Radios", Music TOP
https://stream-gtlc.telecentro.net.ar/hls/musictophls/main.m3u8

#KODIPROP:inputstream.adaptive.license_type=org.w3.clearkey
#KODIPROP:inputstream.adaptive.license_key=68aa8810573e1dc11fb2d82a51d55402:d92e36380b02f531f70dadba49e95f27
#EXTINF:-1 tvg-chno="1116" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/CNCRT.png?raw=true" group-title="Música y Radios", Concert Channel
https://latamvosliveclarovideo.akamaized.net/Content/DASH_DASH_FK/Live/Channel(CONCERT_CHANNEL_HD)/manifest.mpd

#KODIPROP:inputstream.adaptive.license_type=org.w3.clearkey
#KODIPROP:inputstream.adaptive.license_key=a15b0430c06d2631ed0e850fa419c4d7:4f8f17d8b9e7c8c6baea633469b5d687
#EXTINF:-1 tvg-id="NicktoonsLatinAmerica.us" tvg-chno="1117" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/NKMUS.png?raw=true" group-title="Música y Radios", Nick Music
https://latamvosliveclarovideo.akamaized.net/Content/DASH_DASH_FK/Live/Channel(NICKTOONS)/manifest.mpd

#KODIPROP:inputstream.adaptive.license_type=org.w3.clearkey
#KODIPROP:inputstream.adaptive.license_key=b2aae44a74144be8b2118e20d1412bab:8a7ae996d12d8d5d5637d1044f8e08b7
#EXTINF:-1 tvg-chno="1150" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/FMEVT.png?raw=true" group-title="Música y Radios", Flow Music Eventos
https://chromecast.cvattv.com.ar/live/c7eds/Flow_Music_XP/SA_Live_dash_enc_2A/Flow_Music_XP.mpd

#EXTINF:-1 tvg-chno="1151" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/FMCLS.png?raw=true" group-title="Música y Radios", Flow Music Clásicos
https://musicsrc.cvattv.com.ar/RM03

#EXTINF:-1 tvg-chno="1152" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/FMELT.png?raw=true" group-title="Música y Radios", Flow Music Electrónica
https://musicsrc.cvattv.com.ar/RM41

#EXTINF:-1 tvg-chno="1153" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/FMRCK.png?raw=true" group-title="Música y Radios", Flow Music Rock
https://musicsrc.cvattv.com.ar/RM18

#EXTINF:-1 tvg-chno="1154" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/FMRGT.png?raw=true" group-title="Música y Radios", Flow Music Reggaeton
https://musicsrc.cvattv.com.ar/RM30

#EXTINF:-1 tvg-chno="1155" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/FMRG2.png?raw=true" group-title="Música y Radios", Flow Music Reggaeton 2
https://musicsrc.cvattv.com.ar/RM29

#EXTINF:-1 tvg-chno="1156" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/FMLAT.png?raw=true" group-title="Música y Radios", Flow Music Latinos
https://musicsrc.cvattv.com.ar/RM31

#EXTINF:-1 tvg-chno="1157" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/FMRNA.png?raw=true" group-title="Música y Radios", Flow Music Rock Nacional
https://musicsrc.cvattv.com.ar/RM17

#EXTINF:-1 tvg-chno="1158" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/FM70S.png?raw=true" group-title="Música y Radios", Flow Music 70's Hits
https://musicsrc.cvattv.com.ar/RM07

#EXTINF:-1 tvg-chno="1159" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/FM80S.png?raw=true" group-title="Música y Radios", Flow Music 80's Hits
https://musicsrc.cvattv.com.ar/RM05

#EXTINF:-1 tvg-chno="1160" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/FM90S.png?raw=true" group-title="Música y Radios", Flow Music 90's Hits
https://musicsrc.cvattv.com.ar/RM04

#EXTINF:-1 tvg-chno="1161" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/FMHIT.png?raw=true" group-title="Música y Radios", Flow Music Grandes Éxitos
https://musicsrc.cvattv.com.ar/RM06

#EXTINF:-1 tvg-chno="1162" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/FMTNG.png?raw=true" group-title="Música y Radios", Flow Music Tango
https://musicsrc.cvattv.com.ar/RM46

#EXTINF:-1 tvg-chno="1163" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/FMDSC.png?raw=true" group-title="Música y Radios", Flow Music Disco
https://musicsrc.cvattv.com.ar/RM14

#EXTINF:-1 tvg-chno="1164" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/FMJZZ.png?raw=true" group-title="Música y Radios", Flow Music Jazz
https://musicsrc.cvattv.com.ar/RM37

#EXTINF:-1 tvg-chno="1165" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/FMREG.png?raw=true" group-title="Música y Radios", Flow Music Reggae
https://musicsrc.cvattv.com.ar/RM23

#EXTINF:-1 tvg-chno="1166" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/FMRTR.png?raw=true" group-title="Música y Radios", Flow Music Retro
https://musicsrc.cvattv.com.ar/RM16

#EXTINF:-1 tvg-chno="1167" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/FMCIN.png?raw=true" group-title="Música y Radios", Flow Music Cine
https://musicsrc.cvattv.com.ar/RM24

#EXTINF:-1 tvg-chno="1168" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/FMCLC.png?raw=true" group-title="Música y Radios", Flow Music Cine Clásico
https://musicsrc.cvattv.com.ar/RM25

#EXTINF:-1 tvg-chno="1169" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/FMLNT.png?raw=true" group-title="Música y Radios", Flow Music Lentos
https://musicsrc.cvattv.com.ar/RM27

#EXTINF:-1 tvg-chno="1201" tvg-logo="https://www.continental.com.ar/img/logo-night.png" tvg-logo-fallback="https://github.com/masterentertainment/listas/blob/main/Fondos/RLS4.jpg?raw=true" group-title="Música y Radios", Continental (AM 590)
http://www.radiosargentina.com.ar/php/tvm3uYT.php?id=YTAR0001

#EXTINF:-1 tvg-chno="1202" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/RRIV.png?raw=true" group-title="Música y Radios", Rivadavia (AM 630)
http://www.radiosargentina.com.ar/php/tvm3uYT.php?id=YTAR0002

#EXTINF:-1 tvg-chno="1203" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/CAD3.png?raw=true" group-title="Música y Radios", Cadena 3 (AM 700)
https://playerservices.streamtheworld.com/api/livestream-redirect/radio3.mp3

#EXTINF:-1 tvg-chno="1204" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/R710.png?raw=true" group-title="Música y Radios", Radio 10 (AM 710)
http://www.radiosargentina.com.ar/php/tvm3uYT.php?id=YTAR0003

#EXTINF:-1 tvg-chno="1205" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/R750.png?raw=true" group-title="Música y Radios", AM 750
https://playerservices.streamtheworld.com/api/livestream-redirect/AM750AAC.aac

#EXTINF:-1 tvg-chno="1206" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/MITRE.png?raw=true" group-title="Música y Radios", Mitre (AM 790)
http://www.radiosargentina.com.ar/php/tvm3uYT.php?id=YTAR0004

#EXTINF:-1 tvg-chno="1207" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/RDNAC.png?raw=true" group-title="Música y Radios", Nacional (AM 860)
#EXTIMG:"https://pbs.twimg.com/profile_images/1799993061562363904/taj1hRqI_400x400.jpg"
https://sa.mp3.icecast.magma.edge-access.net/sc_rad1

#EXTINF:-1 tvg-chno="1208" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/RRED.png?raw=true" group-title="Música y Radios", Radio La Red (AM 910)
https://playerservices.streamtheworld.com/api/livestream-redirect/LA_RED_AM910AAC.aac

#EXTINF:-1 tvg-chno="1209" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/RCNN.png?raw=true" group-title="Música y Radios", CNN Radio (AM 950)
https://redirector.dps.live/cnn-ar/aac/icecast.audio

#EXTINF:-1 tvg-chno="1210" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/RDPLT.png?raw=true" group-title="Música y Radios", Del Plata (AM 1030)
http://www.radiosargentina.com.ar/php/tvm3uYT.php?id=YTAR0007

#EXTINF:-1 tvg-chno="1211" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/DSTPE.png?raw=true" group-title="Música y Radios", El Destape (AM 1070)
http://www.radiosargentina.com.ar/php/tvm3uYT.php?id=YTAR0076

#EXTINF:-1 tvg-chno="1212" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/LA990.png?raw=true" group-title="Música y Radios", Splendid 990
http://www.radiosargentina.com.ar/php/tvm3uYT.php?id=YTAR0005

#EXTINF:-1 tvg-chno="1220" tvg-logo="https://4dproducciones.com.ar/wp-content/uploads/2022/02/RCV_Logo-5.png" group-title="Música y Radios", Radio Con Vos (FM 89.9)
http://www.radiosargentina.com.ar/php/tvm3uYT.php?id=YTAR0012

#EXTINF:-1 tvg-chno="1221" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/NROCK.png?raw=true" group-title="Música y Radios", Nacional Rock (FM 93.7)
https://sa.mp3.icecast.magma.edge-access.net/sc_rad39

#EXTINF:-1 tvg-chno="1222" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/RDSNY.png?raw=true" group-title="Música y Radios", Radio Disney (FM 94.3)
https://musicsrc.cvattv.com.ar/RDIS

#EXTINF:-1 tvg-chno="1223" tvg-logo="https://www.metro951.com/vivo/img/player.png" group-title="Música y Radios", Metro 95.1
http://playerservices.streamtheworld.com/api/livestream-redirect/METROAAC_SC

#EXTINF:-1 tvg-chno="1224" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/NCLAS.png?raw=true" group-title="Música y Radios", Nacional Clásica (FM 96.7)
https://sa.mp3.icecast.magma.edge-access.net/sc_rad37

#EXTINF:-1 tvg-chno="1225" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/R975.png?raw=true" group-title="Música y Radios", Vale 97.5
http://www.radiosargentina.com.ar/php/tvm3uYT.php?id=YTAR0016

#EXTINF:-1 tvg-chno="1226" tvg-logo="https://media.cdnandroid.com/31/e9/ed/56/imagen-mega-98-3-0big.jpg" group-title="Música y Radios", MEGA 98.3
http://www.radiosargentina.com.ar/php/tvm3uYT.php?id=YTAR0017

#EXTINF:-1 tvg-chno="1227" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/NFOLK.png?raw=true" group-title="Música y Radios", Nacional Folklórica (FM 98.7)
https://sa.mp3.icecast.magma.edge-access.net/sc_rad38

#EXTINF:-1 tvg-chno="1228" tvg-logo="https://cloudfront-us-east-1.images.arcpublishing.com/radiomitre/CZJMM4BJVRFANO4VGMMYWSTEVE.png" group-title="Música y Radios", La 100 (FM 99.9)
https://live-05-13-la100.vodgc.net/live-05-13-la100/tracks-v3a1/mono.m3u8

#EXTINF:-1 tvg-chno="1231" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/LOS40.png?raw=true" group-title="Música y Radios", Los 40 (FM 105.5)
http://playerservices.streamtheworld.com/api/livestream-redirect/LOS40_ARGENTINA_SC

#EXTINF:-1 tvg-chno="1229" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/R1015.png?raw=true" group-title="Música y Radios", POP 101.5
http://www.radiosargentina.com.ar/php/tvm3uYT.php?id=YTAR0020

#EXTINF:-1 tvg-chno="1230" tvg-logo="https://fmaspen.com/wp-content/themes/aspen/images/logoaspen.png" group-title="Música y Radios", Aspen (FM 102.3)
https://playerservices.streamtheworld.com/api/livestream-redirect/ASPEN.mp3

#EXTINF:-1 tvg-chno="1232" tvg-logo="https://www.dsportsradio.com/img/logo-night.png" group-title="Música y Radios", DSports Radio (FM 103.1)
http://playerservices.streamtheworld.com/api/livestream-redirect/DSPORTSRADIO_SC

#EXTINF:-1 tvg-chno="1234" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/ROBS.png?raw=true" group-title="Música y Radios", El Observador 107.9
https://s8.stweb.tv/observador/live/playlist.m3u8

#EXTINF:-1  tvg-chno="1233" tvg-logo="https://urbanaplayfm.com/file/2023/09/logo-web-blanco.png" group-title="Música y Radios", Urbana Play (FM 104.3)
http://www.radiosargentina.com.ar/php/tvm3uYT.php?id=YTAR0022

#EXTINF:-1 tvg-id="Canal 4 San Juan" tvg-name="Canal 4 San Juan" tvg-logo="http://www.canal4sanjuan.com.ar/digital/images/logo-cir.png" group-title="Argentina",Canal 4 San Juan | Argentina
http://streamlov.alsolnet.com/canal4sanjuan/live/chunklist_w1603184235.m3u8



#EXTINF:-1 tvg-chno="2004" tvg-logo="https://i0.wp.com/directostv.teleame.com/wp-content/uploads/2017/10/Canal-4-Esquel-en-vivo-Online.png" tvg-group="Locales", Canal 4 Esquel
https://stream.arcast.com.ar/canal4esquel/canal4esquel/playlist.m3u8

#EXTINF:-1 tvg-chno="2012" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/12PM.png?raw=true" tvg-group="Locales", Canal 12 Trelew
https://5f700d5b2c46f.streamlock.net/madryntv/madryntv/playlist.m3u8

#EXTINF:-1  tvg-chno="1250" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/%23LA17.png?raw=true" group-title="Radios Locales", #LA17 (AM 540)
http://138.36.96.199:8001/lu17

#EXTINF:-1  tvg-chno="1251" tvg-logo="https://git.io/JOTLg" group-title="Música y Radios", Nacional Esquel (AM 560)
https://sa.mp3.icecast.magma.edge-access.net/sc_rad9

#EXTINF:-1  tvg-chno="1252" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/LU20C.png?raw=true" group-title="Música y Radios", LU20 Radio Chubut (AM 580)
https://streaming1.locucionar.com/proxy/radiochubut?mp=/stream

#EXTINF:-1 tvg-chno="1253" tvg-logo="https://git.io/J351K" group-title="Radios Locales", Nacional Patagonia Argentina (AM 630)
http://sa.mp3.icecast.magma.edge-access.net:7200/sc_rad42

#EXTINF:-1  tvg-chno="1254" tvg-logo="https://git.io/JOTLw" group-title="Radios Locales", Nacional Comodoro Rivadavia (AM 670)
http://sa.mp3.icecast.magma.edge-access.net:7200/sc_rad11

#EXTINF:-1  tvg-chno="1255" tvg-logo="https://github.com/masterentertainment/listas/blob/main/logos/R3780.png?raw=true" group-title="Radios Locales", Radio 3 Cadena Patagonia (AM 780)
https://cdn.instream.audio/:9085/stream

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
