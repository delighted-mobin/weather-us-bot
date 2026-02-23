import requests
import json
from PIL import Image
from datetime import datetime, time as t, timedelta
from flask import Flask, request, send_file, jsonify
import os

TOKEN = os.environ.get("BOT_TOKEN", "")
TELEGRAM_API = f"https://api.telegram.org/bot{TOKEN}"
app = Flask(__name__)
id = None

def get_map(state : str = ["mazandaran"], type : list = ["rain", "total"]):
    data = []
    send_message(id, "1")
    with open(f"config.json", "r") as f:
        data = json.loads(f.read())
        f.close()

    send_message(id, "2")

    return data["models"][state][type[0]][type[1]]["request"]

def get_type(state: str = "mazandaran", model: str = "gfs", type: list = ["rain","total"], tm: int = 24, interval: int = 6):
    #link = "https://img6.weather.us/images/data/cache/model/model_modusa_2026021506_4_15569_147.png"
    #usa = 1-2.5 18z | 7-8.5 00z | 13-14.5 06z| 19-20.5 12z

    link = "https://img6.weather.us/images/data/cache/model/"
    link_list = []
    map_link = get_map(state, type)

    send_message(id, "3")

    with open("config.json", "r") as f:
        config = json.loads(f.read())
        f.close()

    send_message(id, "4")

    link = link+config["maps"][model]["link"]
    interval = interval if interval >= int(config["maps"][model]["interval"]) else int(config["maps"][model]["interval"])

    send_message(id, "5")

    if len(config["maps"][model]["update_time"]) == 4:
        for i in range(0, tm+1, interval):
            d = datetime.now()
            d_time = datetime.now()
            utimes = config["maps"][model]["update_time"]
            run = "00"

            if i == 0:
                i = 1

            if t(utimes[0][0], utimes[0][1]) <= d.time() < t(utimes[1][0], utimes[1][1]):
                run = "18"
            elif t(utimes[1][0], utimes[1][1]) <= d.time() < t(utimes[2][0], utimes[2][1]):
                run = "00"
            elif t(utimes[2][0], utimes[2][1]) <= d.time() < t(utimes[3][0], utimes[3][1]):
                run = "06"
            elif t(utimes[3][0], utimes[3][1]) <= d.time():
                run = "12"
            elif d.time() < t(utimes[0][0], utimes[0][1]):
                run = "12"
                d_time = d - timedelta(days=1)
                
            link_list.append({"link": link+f"_{d_time.year}{d_time.month:02}{d_time.day:02}{run}_{i}_{map_link}.png", "run": i})

    elif len(config["maps"][model]["update_time"]) == 2:
        for i in range(0, tm+1, interval):
            d = datetime.now()
            d_time = datetime.now()
            utimes = config["maps"][model]["update_time"]
            run = "00"

            if i == 0:
                i = 1

            if t(utimes[0][0], utimes[0][1]) <= d.time() < t(utimes[1][0], utimes[1][1]):
                run = "18"
            elif t(utimes[1][0], utimes[1][1]) <= d.time():
                run = "06"
            elif d.time() < t(utimes[0][0], utimes[0][1]):
                run = "06"
                d_time = d - timedelta(days=1)
                
            link_list.append({"link": link+f"_{d_time.year}{d_time.month:02}{d_time.day:02}{run}_{i}_{map_link}.png", "run": i})

    send_message(id, "6")

    return link_list

#----------- Not useful for current method ---------------
def get_web(state: str = "mazandaran", model: str = "gfs", type: list = ["rain","total"], tm: int = 24, interval: int = 6):
    #https://weather.us/model-charts/euro/2026022112/mazandaran/temperature/20260221-1300z.html

    send_message(id, "7")
    with open("config.json", "r") as f:
        config = json.loads(f.read())
        f.close()

    send_message(id, "8")

    link = "https://weather.us/model-charts/"+config["maps"][model]["web"]
    interval = interval if interval >= int(config["maps"][model]["interval"]) else int(config["maps"][model]["interval"])

    send_message(id, "9")
    d = datetime.now()
    d_time = datetime.now()
    utimes = config["maps"][model]["update_time"]
    run = "00"
    send_message(id, "10")

    if t(utimes[0][0], utimes[0][1]) <= d.time() < t(utimes[1][0], utimes[1][1]):
        run = "18"
    elif t(utimes[1][0], utimes[1][1]) <= d.time():
        run = "06"
    elif d.time() < t(utimes[0][0], utimes[0][1]):
        run = "06"
        d_time = d - timedelta(days=1)
    
    link += f"/{d_time.year}{d_time.month:02}{d_time.day:02}{run}/{state}/{config["models"][state][type[0]][type[1]]["web"]}"
    link_lit = []

    for i in range(0, tm+1, interval):
        d = datetime.now()
        utimes = config["maps"][model]["update_time"]

        if i == 0:
            i = 1

        rr = int(run) + i

        if rr/24 >= 1:
            d = d + timedelta(days=int(rr/24))
            rr = rr - (int(rr/24)*24)

        link_lit.append({"link": f"{link}/{d.year}{d.month:02}{d.day:02}-{rr:02}00z.html", "run": i})
        
    send_message(id, "11")
    return link_lit
#---------------------------------------------------------

def create_map(state: str = "mazandaran", model: str = "gfs", type: list = ["rain","total"], tm: int = 24, interval: int = 6):
    send_message(id, "12")
    links = get_type(state,model,type,tm,interval)
    send_message(id, "13")
    headers = [
        {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) ",
            "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": "",
            "Connection": "keep-alive"
        },
        {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) ",
            "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": "https://weather.us",
            "Connection": "keep-alive"
        },
        {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) ",
            "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": "https://img3.weather.us",
            "Connection": "keep-alive"
        },
        {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) ",
            "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": "https://img5.weather.us",
            "Connection": "keep-alive"
        },
        {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                            "AppleWebKit/537.36 (KHTML, like Gecko) ",
            "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": "https://img6.weather.us",
            "Connection": "keep-alive"
        }
    ]
    send_message(id, "14")
    for i in links:
        session = requests.Session()
        session.get("https://weather.us",headers=headers[1])
        session.get("https://img3.weather.us",headers=headers[2])
        session.get("https://img5.weather.us",headers=headers[3])
        session.get("https://img6.weather.us",headers=headers[4])
        send_message(id, "15")
        
        headers[0]["Referer"] = i["link"]
        send_message(id, "16")
        req = session.get(i["link"],headers=headers[0])
        with open(str(i["run"])+".png", "wb") as f:
            f.write(req.content)
        send_message(id, "17")
        background = Image.open(str(i["run"])+".png")  
        overlay = Image.open(f"data\\{type[0]}_layout.png")
        borders = Image.open("data\\borders.png")

        overlay = overlay.resize(background.size)
        combined = Image.alpha_composite(background.convert("RGBA"), overlay.convert("RGBA"))
        combined2 = Image.alpha_composite(combined.convert("RGBA"), borders.convert("RGBA"))

        combined2.save(str(i["run"])+".png")
        send_message(id, "18")

#-------------------------- TELEGRAM BOT ----------------------------

def send_updates(chat_id, text):

    media = [
        {"type": "photo", "media": "attach://photo1"},
        {"type": "photo", "media": "attach://photo2"}
    ]

    files = {
        "photo1": open("data\\1.png", "rb"),
        "photo2": open("data\\6.png", "rb")
    }

    try:
        requests.post(f"{TELEGRAM_API}/sendMediaGroup", json={
            "chat_id": chat_id,
            "text": text, 
            "media": json.dumps(media)
            },
            files=files, 
            timeout=10 
        )
    except Exception as e:
        print("Error sending message:", e)

def send_message(chat_id, text):
    try:
        requests.post(f"{TELEGRAM_API}/sendMessage", json={
            "chat_id": chat_id,
            "text": text}, 
            timeout=10
        )
    except Exception as e:
        print("Error sending message:", e)

@app.get("/")
def index():
    # Simple health check
    return "runned"


@app.post("/")
def webhook():
    update = request.get_json(silent=True) or {}
    message = update.get("message") or update.get("edited_message")
    if not message:
        return jsonify(ok=True)

    class msg: 
        chat_id = message["chat"]["id"]
        id = message.get("message_id","")
        mfrom = message["from"]
        reply = message.get("reply_to_message")
        type = str(message["chat"]["type"])
        text = str(message.get("text", ""))
    
    if msg.mfrom["is_bot"] == True:
        return
    
    if msg.type == "private":
        global id
        id = msg.chat_id
        create_map()
        send_updates(msg.chat_id, "ok")

    return jsonify(ok=True)

#app.run(port=1010)

