# 🚀 24/7 BOT DEPLOYMENT GUIDE

## ✅ Wat je nu hebt:
- `continuous_monitor.py` - Bot die 24/7 draait
- Updates elke 5 uur via Telegram
- Instant alerts bij vondsten

---

## 🎯 OPTIE 1: Railway.app (AANGERADEN - MAKKELIJKST)

### Waarom Railway?
- ✅ $5 gratis credits per maand (genoeg voor deze bot!)
- ✅ Automatisch deployen via GitHub
- ✅ Automatisch herstarten bij crashes
- ✅ Super simpele setup

### Stappen:

#### 1. Maak Railway account
```bash
open https://railway.app
```
- Sign up met GitHub

#### 2. Push code naar GitHub (als je dat nog niet hebt)
```bash
cd "/Users/ballie/Desktop/TELEGRAM BBB MUSIC"

# Maak .gitignore aan (als die er nog niet is)
echo "venv/" >> .gitignore
echo "venv_new/" >> .gitignore
echo "*.session" >> .gitignore
echo ".env" >> .gitignore
echo "*.log" >> .gitignore
echo "__pycache__/" >> .gitignore

# Init git (als je dat nog niet hebt)
git init
git add .
git commit -m "Add 24/7 continuous monitor"

# Maak repo op GitHub en push (vervang met jouw username)
# Of gebruik GitHub Desktop app
```

#### 3. Deploy naar Railway
1. Ga naar https://railway.app/dashboard
2. Klik "New Project"
3. Selecteer "Deploy from GitHub repo"
4. Kies je repository
5. Railway detecteert automatisch Python
6. Klik "Deploy"

**Dat is het! Bot draait nu 24/7! 🎉**

#### 4. Check logs
- Klik op je project in Railway dashboard
- Ga naar "Deployments"
- Click op latest deployment
- Zie logs → je zou startup bericht moeten zien

---

## 🎯 OPTIE 2: Render.com (GRATIS, maar iets trager)

### Stappen:

1. Ga naar https://render.com
2. Sign up met GitHub
3. Klik "New +" → "Background Worker"
4. Connect je GitHub repo
5. Settings:
   - **Name:** telegram-music-bot
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python3 continuous_monitor.py`
6. Klik "Create Background Worker"

**Bot draait nu 24/7!**

⚠️ **Note:** Render gratis tier kan soms slapen na inactiviteit, maar werkt wel voor background workers.

---

## 🎯 OPTIE 3: Lokaal draaien (Mac blijft aan)

Als je je Mac toch altijd aan hebt staan:

### A. Met screen (terminal blijft draaien)
```bash
cd "/Users/ballie/Desktop/TELEGRAM BBB MUSIC"
source venv_new/bin/activate

# Start screen sessie
screen -S music_bot

# Run bot
python3 continuous_monitor.py

# Druk: CTRL+A dan D om te "detachen"
# Bot blijft draaien!

# Later: om terug te keren naar bot:
screen -r music_bot

# Om bot te stoppen:
screen -r music_bot
# Dan CTRL+C
```

### B. Als startup service (geavanceerd)
```bash
# Maak startup script
nano ~/Library/LaunchAgents/com.musicbot.plist

# Plak dit erin (pas pad aan als nodig):
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.musicbot</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/ballie/Desktop/TELEGRAM BBB MUSIC/venv_new/bin/python3</string>
        <string>/Users/ballie/Desktop/TELEGRAM BBB MUSIC/continuous_monitor.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>

# Load de service
launchctl load ~/Library/LaunchAgents/com.musicbot.plist

# Start de service
launchctl start com.musicbot
```

---

## 🎯 OPTIE 4: VPS (Meest betrouwbaar, kost geld)

Voor $5-10/maand bij DigitalOcean, Linode, of Vultr:

1. Maak VPS aan (Ubuntu)
2. SSH erin
3. Install Python:
```bash
sudo apt update
sudo apt install python3 python3-pip git
```

4. Clone je repo:
```bash
git clone [je-repo-url]
cd [repo-naam]
pip3 install -r requirements.txt
```

5. Run met screen:
```bash
screen -S bot
python3 continuous_monitor.py
# CTRL+A, D om te detachen
```

---

## 📊 WAT GEBEURT ER NA DEPLOYMENT?

### Direct na start:
1. ✅ Je krijgt Telegram bericht: "🚀 BOT GESTART"
2. ✅ Eerste scan begint meteen
3. ✅ Eerste status update wordt verstuurd

### Elke 5 uur:
1. 🔍 Nieuwe scan draait
2. 📱 Status update naar Telegram
3. 🚨 Als track gevonden: INSTANT alert!

### Als track gevonden:
```
🚨🚨🚨 TARGET GEVONDEN! 🚨🚨🚨

🎯 Target: Nass - Luchten
✅ Gevonden: Nass - Luchten
📅 Release: 2026-01-30
🔗 Spotify: [link]

🔥 GA METEEN DOWNLOADEN! 🔥
```

---

## 🔧 TROUBLESHOOTING

### "Bot crashed na 5 minuten"
→ Check logs op Railway/Render
→ Waarschijnlijk: Spotify credentials issue
→ Test eerst lokaal: `python3 continuous_monitor.py`

### "Geen Telegram berichten"
→ Check of bot_token en chat_id correct zijn
→ Test Telegram API handmatig

### "Schedule werkt niet"
→ Check of `schedule` library geïnstalleerd is
→ Run: `pip install schedule`

### "Wil interval aanpassen"
→ Edit `continuous_monitor.py` line 244-245:
```python
schedule.every(5).hours.do(...)  # Verander 5 naar gewenst aantal uren
```

---

## 💡 EXTRA TIPS

### Test eerst lokaal:
```bash
cd "/Users/ballie/Desktop/TELEGRAM BBB MUSIC"
source venv_new/bin/activate
pip install schedule
python3 continuous_monitor.py
```

Wacht 1-2 minuten → je zou startup bericht in Telegram moeten krijgen!

### Monitor de bot:
- Railway/Render: Check logs in dashboard
- Lokaal: Terminal output toont alle scans
- Telegram: Je krijgt elke 5 uur update

### Stop de bot:
- Railway/Render: Klik "Stop" in dashboard
- Lokaal screen: `screen -r music_bot` dan `CTRL+C`
- Je krijgt "⛔ BOT GESTOPT" bericht in Telegram

---

## 🎯 AANBEVELING

**Voor jou: Start met RAILWAY!**

Waarom?
1. ✅ Gratis $5/maand (ruim genoeg)
2. ✅ Deploy in 5 minuten
3. ✅ Automatisch herstarten
4. ✅ Makkelijk logs checken
5. ✅ Mac hoeft niet aan te blijven

**Railway is perfect voor deze use case!**

---

## 📞 VOLGENDE STAPPEN

1. **Test lokaal** (5 min):
   ```bash
   python3 continuous_monitor.py
   ```
   → Check Telegram voor berichten

2. **Deploy naar Railway** (10 min):
   - Push naar GitHub
   - Connect Railway
   - Deploy
   - Done! ✅

3. **Monitor resultaten**:
   - Elke 5 uur krijg je update
   - Heavy Hits blijft handmatig checken
   - Instagram Stories blijft handmatig checken

**LET'S GO! 🚀**
