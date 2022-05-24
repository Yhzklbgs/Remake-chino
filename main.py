#!usr/bin/python
# -*- coding: utf-8 -*-
from LineClient import *
from threading import Thread
from datetime import datetime
import sys, traceback, time, os, json, livejson, requests, re, pytz

# LOGIN WITH TOKEN
client = LINE('ISI TOKEN',appType = "ISI APPTYPE")

# LOGIN WITH EMAIL
#client = LINE('ISI EMAIL','ISI PASSWORD',appType = "ISI APPTYPE")

settings = livejson.File("settings.json",True, True, 4)
owner = settings['owner']
defaultGroup = settings['defaultGroup']

if owner is None:
    print('Isi mid owner dulu di settings.json')
    sys.exit(1)

if settings['runtime'] is None:
    settings['runtime'] = time.time()

if settings['defaultGroup'] is None:
    settings['defaultGroup'] = owner

# MAIN FUNCTION #

def reply(msg,text):
    for i in range(0, len(text), 10000):
        textt = text[i:i+10000]
        client.sendReplyMessage(msg.id,msg.to,textt)

def timeChange(secs):
    mins, secs = divmod(secs,60)
    hours, mins = divmod(mins,60)
    days, hours = divmod(hours,24)
    weeks, days = divmod(days,7)
    months, weeks = divmod(weeks,4)
    text = ""
    if months != 0: text += "%02d Months" % (months)
    if weeks != 0: text += " %02d Weeks" % (weeks)
    if days != 0: text += " %02d Days" % (days)
    if hours !=  0: text +=  " %02d Hours" % (hours)
    if mins != 0: text += " %02d Minutes" % (mins)
    if secs != 0: text += " %02d Seconds" % (secs)
    if text[0] == " ":
        text = text[1:]
    return text

def checkRuntime(msg):
    timeNow = time.time()
    runtime = timeNow - settings['runtime']
    runtime = timeChange(runtime)
    reply(msg,f'{runtime}')

def logError(text):
    traceback.print_tb(text.__traceback__)
    client.log("ERROR 404 !\n" + str(text))

def mycmd(text, rname):
    cmd = ""
    pesan = text
    if pesan.startswith(rname):
        pesan = pesan.replace(rname, "", 1)
        if " & " in text:
            cmd = pesan.split(" & ")
        else:
            cmd = [pesan]
    return cmd

def getUrlInText(text):
    regex = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    datas = re.findall(regex, text)
    links = []
    for link in datas:
        if link not in links:
            links.append(link)
    return links

# AUTO DOWNLOAD FUNCTION #

def downloadTiktokUrl(to,text):
    try:
        r = requests.get(f'https://api.coursehero.store/musicallydown?url={text}')
        data = r.json()
        video = data['result']['download']
        thumb = 'https://seeklogo.com/images/T/tiktok-logo-B9AC5FE794-seeklogo.com.png'
        client.sendTemplateVideoV2(to,video,thumb)
    except Exception as e:
        traceback.print_tb(e.__traceback__)

def downloadInstagramUrl(to,text):
    try:
        r = requests.get(f'http://8.209.197.129/instagram/post?url={text}&apikey=CARI APIKEY NYA SENDIRI')
        data = r.json()
        urls = []
        for media in data['result']['media']:
            if media['is_video']:
                client.sendTemplateVideoV2(to,media['video'])
            else:
                client.sendTemplateImageV2(to,media['image'])
    except Exception as e:
        traceback.print_tb(e.__traceback__)

def downloadYoutubeUrl(to,text):
    try:
        r = requests.get(f'http://8.209.197.129/ytdl?url={text}&apikey==ARI APIKEY NYA SENDIRI')
        data = r.json()
        if 'shorts' in text:
            video = data['data']['ytInfo']['url']
            thumb = 'https://i.ibb.co/x6NJbMB/Youtube.png'
            client.sendTemplateVideoV2(to,video,thumb)
        else:
            video = data['data']['videoInfo']['url']
            thumb = data['data']['videoInfo']['thumbnails']
            client.sendTemplateVideoV2(to,video,thumb)
    except Exception as e:
        traceback.print_tb(e.__traceback__)

# CONVERT PRIMARY FUNCTION #
def cvprim(msg, to, sender, auth, app):
    try:
        if app.lower() == "chrome":
            appName = "CHROMEOS\t2.4.4\tChrome OS\t1"
        if app.lower() == "win":
            appName = "DESKTOPWIN\t6.7.2\tWindows\t10"
        if app.lower() == "mac":
            appName = "DESKTOPMAC\t6.7.2\tMAC\t10"
        if app.lower() == "ipad":
            appName = "IOSIPAD\t11.6.3\tIphoneX\t14"
        authToken = f'{auth}'
        params = {"appname": appName, "authtoken": authToken}
        reply(msg, 'Please waiting for convert, token secondary will send in your private chat')
        r = requests.get('https://api.coursehero.store/lineprimary2secondary',params=params)
        main = r.json()
        token = f'{main["result"]["token"]}'
        reply(msg, "Result token send in private chat")
        client.sendMessage(sender,token)
    except Exception as e:
        reply(msg,'Please make sure primary token not banned')
        logError(e)

def doConvert(msg,to,sender,text):
    if text.lower() =='cvprim':
        res = ' 「 Convert 」'
        res += '\nType : Primary♪'
        res += '\nDetail : ↴'
        res += '\n  ↳ Mac'
        res += '\n  ↳ Win'
        res += '\n  ↳ Ipad'
        res += '\n  ↳ Chrome'
        res += '\nUsage : ↴'
        res += "\n  ↳ Cvprim <Type/No> <Token>"
        reply(msg,res)
    else:
        sep = text.replace(text.split(" ")[0]+" ","")
        auth = sep.split(" ")[1]
        if sep.split(" ")[0].lower() == "mac" or sep.split(" ")[0].lower() == "1":
            login = Thread(target=cvprim, args=(msg,to,sender,auth,"mac"))
            login.daemon = True
            login.start()

# TOKEN FUNCTION #
def getToken(msg, to, sender, app):
    try:
        if app.lower() == "chrome":
            appName = "CHROMEOS\t2.4.4\tChrome OS\t1"
        if app.lower() == "win":
            appName = "DESKTOPWIN\t6.7.2\tWindows\t10"
        if app.lower() == "mac":
            appName = "DESKTOPMAC\t6.7.2\tMAC\t10"
        if app.lower() == "ipad":
            appName = "IOSIPAD\t11.6.3\tIphoneX\t14"
        params = {"appname": appName}
        r = requests.get("https://api.coursehero.store/lineqr",params=params)
        main = r.json()
        reply(msg, f"Open this link on your LINE for smartphone in 2 minutes {main['result']['qrlink']}")
        client.sendTemplateImageV2(to,main['result']['qrcode'])
        pincode = json.loads(requests.get(f"https://api.coursehero.store/lineqr/pincode/{main['result']['session']}",params=params).text)
        pincode = f"Pincode @! {pincode['result']['pincode']}"
        client.sendMentionV4(to,pincode,[sender])
        auth = json.loads(requests.get(f"https://api.coursehero.store/lineqr/auth/{main['result']['session']}",params=params).text)
        reply(msg, "Result token send in private chat")
        client.sendMessage(sender,f'{auth["result"]["accessToken"]}')
    except Exception as e:
        traceback.print_tb(e.__traceback__)

def doToken(msg,to,sender,text):
    if text.lower() =='token':
        res = ' 「 Generator 」'
        res += '\nType : Token♪'
        res += '\nDetail : ↴'
        res += '\n  ↳ Mac'
        res += '\n  ↳ Win'
        res += '\n  ↳ Ipad'
        res += '\n  ↳ Chrome'
        res += '\nUsage : ↴'
        res += "\n  ↳ Token <Type/Num>"
        reply(msg,res)
    else:
        sep = text.replace(text.split(" ")[0]+" ","")
        if sep.split(" ")[0].lower() == "mac" or sep.split(" ")[0].lower() == "1":
            login = Thread(target=getToken, args=(msg,to,sender,"mac"))
            login.daemon = True
            login.start()
        if sep.split(" ")[0].lower() == "win" or sep.split(" ")[0].lower() == "2":
            login = Thread(target=getToken, args=(msg,to,sender,"win"))
            login.daemon = True
            login.start()
        if sep.split(" ")[0].lower() == "ipad" or sep.split(" ")[0].lower() == "3":
            login = Thread(target=getToken, args=(msg,to,sender,"mac"))
            login.daemon = True
            login.start()
        if sep.split(" ")[0].lower() == "chrome" or sep.split(" ")[0].lower() == "4":
            login = Thread(target=getToken, args=(msg,to,sender,"mac"))
            login.daemon = True
            login.start()

# APPNAME FUNCTION #
def appNameLine(msg):
    try:
        r = requests.get('https://minz-restapi.xyz/lineappname')
        data = r.json()
        ret = "APPNAME LINE\n"
        ret += f"\nAndroid : {data['result']['ANDROID']}"
        ret += f"\nChromeos : {data['result']['CHROMEOS']}"
        ret += f"\nDesktopmac : {data['result']['DESKTOPMAC']}"
        ret += f"\nDesktopwin : {data['result']['DESKTOPWIN']}"
        ret += f"\nIos : {data['result']['IOS']}"
        ret += f"\nIosipad : {data['result']['IOSIPAD']}"
        reply(msg,ret)
    except Exception as e:
        logError(e)

def main(op):
    try:
        op = LineClient(op, client)
        if op.type == 5:
            client.findAndAddContactsByMid(op.param1)
            client.sendMentionV4(op.param1, "Hello @!\nThanks For Add Me As Friend.\nPlease Add My Official Account",[op.param1])
            client.sendContact(op.param1, "u1cef5d9f20f0390e49b5a3b96eee3b01")
        if op.type == 124:
            if client.profile.mid in op.param3:
                group = client.getChats([op.param1])
                client.time = pytz.timezone('Asia/Jakarta')
                timeEx = datetime.now(tz=client.time)
                ret_ = "NOTIFIED INVITE INTO GROUP\n\n"
                ret_ += "Executor: @!"
                ret_ += "\nGroup: "f"{group.chats[0].chatName}"
                ret_ += '\nDate: '+ datetime.strftime(timeEx,'%Y-%m-%d')+"\nTime: "+ datetime.strftime(timeEx,'%H:%M:%S')
                if op.param2 in owner:
                    client.acceptChatInvitation(op.param1)
                    client.sendMessage(op.param1,'Thanks for invite me')
                else:
                    client.sendMentionV4(defaultGroup,ret_,[op.param2])
                    client.acceptChatInvitation(op.param1)
                    client.sendMessage(op.param1,'You don`t have access')
                    client.deleteSelfFromChat(op.param1)
        if op.type == 133:
            if client.profile.mid in op.param3:
                if op.param2 not in owner:
                    group = client.getChats([op.param1])
                    client.time = pytz.timezone('Asia/Jakarta')
                    timeEx = datetime.now(tz=client.time)
                    ret_ = "NOTIFIED KICK FROM GROUP\n\n"
                    ret_ += "Executor: @!"
                    ret_ += "\nVictim: "f"{client.getContact(op.param3).displayName}"
                    ret_ += "\nGroup: "f"{group.chats[0].chatName}"
                    ret_ += '\nDate: '+ datetime.strftime(timeEx,'%Y-%m-%d')+"\nTime: "+ datetime.strftime(timeEx,'%H:%M:%S')
                    client.sendMentionV4(defaultGroup,ret_,[op.param2])
            if owner in op.param3:
                client.deleteOtherFromChat(op.param1,[op.param2])
                client.inviteIntoChat(op.param1,[op.param3])
        if op.type == 26:
            msg = op.message
            text  = str(op.text)
            msg_id = op.id
            receiver = op.to
            sender = op._from
            to = op.to
            txt = text.lower()
            if msg.contentType == 16:
                content = msg.contentMetadata
                if content['serviceType'] == "AB":
                    ret = '「 Check Album 」\n'
                    ret += f'\nAlbum Name : `{content["albumName"]}`'
                    ret += f'\nAlbum URL : {content["postEndUrl"]}'
                    client.sendMessage(to,ret)
            if msg.contentType == 0:
                if None == msg.text:
                    return
                if text.lower().startswith(settings["rname"].lower() + " "):
                    rname = settings["rname"].lower() + " "
                else:
                    rname = settings["rname"].lower()
                if msg.toType == 2:
                    if "tiktok.com" in text.lower():
                        links = getUrlInText(text)
                        for link in links:
                            login = Thread(target=downloadTiktokUrl, args=(to,link))
                            login.daemon = True
                            login.start()
                    if "instagram.com" in text.lower():
                        links = getUrlInText(text)
                        for link in links:
                            login = Thread(target=downloadInstagramUrl, args=(to,link))
                            login.daemon = True
                            login.start()
                    if "youtube.com" in text.lower():
                        links = getUrlInText(text)
                        for link in links:
                            login = Thread(target=downloadYoutubeUrl, args=(to,link))
                            login.daemon = True
                            login.start()
                    txt = msg.text.lower()
                    txt = " ".join(txt.split())
                    mykey = []
                    if (txt.startswith(rname)):
                        mykey = mycmd(txt, rname)
                    else:
                        mykey = []
                    if txt == "rname":
                        reply(msg,settings['rname'])
                    if txt == rname:
                        tz = pytz.timezone("Asia/Jakarta")
                        timeNow = datetime.now(tz=tz)
                        mek = "Moshimoshi (もしもし)"
                        mek += "\n\n" + datetime.strftime(timeNow,'%d-%m-%Y')
                        mek += " " + datetime.strftime(timeNow,'%H:%M:%S')
                        reply(msg,mek)
                    if txt.startswith('token'):
                        doToken(msg,to,sender,text)
                    if txt.startswith('cvprim'):
                        doConvert(msg,to,sender,text)
                    if txt == 'appname':
                        appNameLine(msg)
                    if txt.startswith('chatowner'):
                        sep = txt.split(" ")
                        message = txt.replace(sep[0] + " ","")
                        if sender in owner:
                            return
                        if sender not in settings['pc']:
                            settings['pc'][sender] = {'mid': sender, 'pesan': []}
                        if message == ' ':
                            return reply(msg,'Please put ur message u want to tell for creator')
                        client.sendMentionV4(defaultGroup, f'From : @!\n{message}',[sender])
                        settings['pc'][sender]['pesan'].append(message)
                        reply(msg, 'Pesan terkirim ke owner')
                        client.sendMentionV4(owner, 'You have 1 new message from @!',[sender])
                    if txt == 'list pc' or txt.startswith('list pc ') or txt.startswith('bales pc ') and sender in owner:
                        rets = 'Detail PC:'
                        try:
                            m = {}
                            for i in settings['pc']:
                                m[i] = settings['pc'][i]['mid'], settings['pc'][i]['pesan']
                            sort = sorted(m)
                            sort.reverse()
                            sort = sort[0:]
                            if txt == 'list pc' and sender in owner:
                                nama = []
                                for i in sort:
                                    nama.append(i)
                                k = len(nama)//20
                                for aa in range(k+1):
                                    if aa == 0:ret = 'list pc:';no = aa
                                    else:ret = 'list pc:';no = aa *20
                                    dd = ret
                                    for mid in nama[aa*20:(aa+1)*20]:
                                        no += 1
                                        if no == len(nama):dd+= f'\n{no}. @! {len(settings["pc"][mid]["pesan"])} pesan.'
                                        else:dd+= f'\n{no}. @! {len(settings["pc"][mid]["pesan"])} pesan.'
                                    client.sendMentionV2(msg_id,to, dd, nama[aa*20:(aa+1)*20])
                            if txt.startswith('list pc ') and sender in owner:
                                asd = sort[int(txt.lower().split(' ')[2])-1]
                                no = 0
                                rets += f'\n @!. {len(settings["pc"][asd]["pesan"])} Pesan'
                                h = [asd]
                                for k in range(len(settings["pc"][asd]["pesan"])):
                                    no += 1
                                    if no == 1:rets += f'\n{no}. {settings["pc"][asd]["pesan"][k]}\n'
                                    else:rets += f'\n{no}. {settings["pc"][asd]["pesan"][k]}\n'
                                client.sendMentionV2(msg_id,to, rets, h)
                            if txt.startswith('bales pc ') and sender in owner:
                                asd = sort[int(txt.lower().split(' ')[2])-1]
                                pesan = txt.replace(txt[:11],"")
                                client.sendMentionV4(asd, f'Balesan dari owner: @!\n{str(txt.replace(txt[:11],""))}',[sender])
                                client.sendMentionV2(msg_id,to,"Berhasil membalas pesan dari @!",[asd])
                                del settings['pc'][asd]
                        except Exception as e:
                            traceback.print_tb(e.__traceback__)
                    if txt.startswith("exec") and sender in owner:
                        try:
                            key = text.replace(text.split("\n")[0],"")
                            sys.stdout = open("exec.txt","w")
                            exec(key)
                            sys.stdout.close()
                            sys.stdout = sys.__stdout__
                            with open("exec.txt","r") as r:
                                txt = r.read()
                            reply(msg,txt)
                        except Exception as e:
                            logError(e)
                            reply(msg,f"{e}")
                    for a in mykey:
                        txt = a
                        if txt in ('help','.help','#help','key','menu','commands','cmd'):
                            ret = "𝗛𝗘𝗟𝗣 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦\n"
                            ret += "Type : ‘Public Bots’\n\n"
                            ret += "  Detail : ↴\n"
                            ret += "    ⚘ Chatowner <Text>\n"
                            ret += "    ⚘ Appname\n"
                            ret += "    ⚘ Cvprim\n"
                            ret += "    ⚘ Genprim <Auth>\n"
                            ret += "    ⚘ Getcall\n"
                            ret += "    ⚘ Media\n"
                            ret += "    ⚘ React\n"
                            ret += "    ⚘ Tagall\n"
                            ret += "    ⚘ Token"
                            reply(msg,ret)
                        elif txt == 'hi':
                            reply(msg,'hi too')
                        elif txt == 'speed':
                            start = time.time()
                            profile = client.getProfile()
                            mtime = time.time() - start
                            ping = mtime * 1000
                            reply(msg,"%s ms."%(round(ping,2)))
                        elif txt == 'runtime':
                            checkRuntime(msg)
                        elif txt == 'bye':
                            if msg._from in owner:
                                reply(msg,'Thanks for using me')
                                client.deleteSelfFromChat(to)
                            else:
                                reply(msg,'Sok iye mo ngusir gw lu')
                                client.deletOtherFromChat(sender)
                        elif txt == 'set defaultgroup':
                            if settings['defaultGroup'] != None:
                                reply(msg,'Default group already set')
                            else:
                                settings['defaultGroup'] = to
                                reply(msg,'Success set Default group in here')
                        elif txt == 'del defaultgroup':
                            if settings['defaultGroup'] == None:
                                reply(msg,'Default group already not set')
                            else:
                                settings['defaultGroup'] = None
                                reply(msg,'Success clear Default group in here')
                        elif txt == 'restart' and sender in owner:
                            reply(msg,'Restart♪')
                            settings['restartPoint'] = to
                            client.restart()
                        elif txt.startswith("uprname "):
                            string = txt.split(" ")[1]
                            settings['rname'] = string
                            reply(msg,f"Responsename change to {settings['rname']}")
    except Exception:
        traceback.print_exc()
    except KeyboardInterrupt:
        sys.exit("Keyboard Interrupt.")

def fetch():
    try:
        if settings["restartPoint"] is not None:
            try:client.sendMessage(settings["restartPoint"], 'Activated♪')
            except Exception as e:print(e)
            settings["restartPoint"] = None
        while 1:
            ops = client.fetchOps()
            for op in ops:
                if op.revision == -1 and op.param2 != None:
                    client.globalRev = int(op.param2.split("\x1e")[0])
                if op.revision == -1 and op.param1 != None:
                    client.individualRev = int(op.param1.split("\x1e")[0])
                client.setRevision(op.revision)
                main(op)
    except Exception:
        traceback.print_exc()
    except KeyboardInterrupt:
        sys.exit("KeyboardInterrupt.")

if __name__ == "__main__":
    fetch()