#!/usr/bin/env python3
"""
🔥 CONTINUOUS TARGET MONITOR 🔥
Draait 24/7 en stuurt elke 5 uur updates via Telegram

Deployment opties:
- Railway.app (aangeraden)
- Render.com
- Fly.io
- VPS (DigitalOcean, etc.)
"""

import requests
import json
import time
from datetime import datetime, timedelta
import schedule
import sys

class ContinuousMonitor:
    """24/7 monitoring bot voor early releases"""
    
    def __init__(self):
        self.bot_token = "8316998623:AAFW4D85_UIdi1hHSrit7xOku1chW_5dv3g"
        self.chat_id = "5940089017"
        
        # Spotify credentials
        self.spotify_client_id = "fe4bfac114e946289273400b097416ad"
        self.spotify_client_secret = "86638b315877443a86b150d1e31b277b"
        self.spotify_token = None
        self.spotify_token_expiry = None
        
        # Tracking
        self.scan_count = 0
        self.start_time = datetime.now()
        self.last_scan_time = None
        
        # Target info
        self.targets = {
            "nass_luchten": {
                "artist": "Nass",
                "track": "Luchten",
                "release_date": "2026-01-30",
                "variations": ["luchten", "lucht", "luchte"],
                "found": False,
                "spotify_url": None
            },
            "jojo_before_hype": {
                "artist": "Jojo Air",
                "track": "Before The Hype",
                "release_date": "2026-01-29",
                "variations": ["before the hype", "before hype", "beforethehype", "b4 the hype"],
                "artist_variations": ["Jojo Air", "JojoAir", "Jojo", "Jimmy", "Solid Circle"],
                "found": False,
                "spotify_url": None
            }
        }
    
    def send_telegram(self, message, silent=False):
        """Stuur bericht naar Telegram"""
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        data = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "HTML",
            "disable_notification": silent
        }
        try:
            response = requests.post(url, json=data, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Telegram send failed: {e}")
            return False
    
    def get_spotify_token(self):
        """Get Spotify access token (cache voor 1 uur)"""
        if self.spotify_token and self.spotify_token_expiry:
            if datetime.now() < self.spotify_token_expiry:
                return self.spotify_token
        
        auth_url = "https://accounts.spotify.com/api/token"
        auth_data = {
            "grant_type": "client_credentials",
            "client_id": self.spotify_client_id,
            "client_secret": self.spotify_client_secret
        }
        
        try:
            response = requests.post(auth_url, data=auth_data, timeout=10)
            data = response.json()
            self.spotify_token = data["access_token"]
            # Token is geldig voor ~1 uur
            self.spotify_token_expiry = datetime.now() + timedelta(minutes=55)
            return self.spotify_token
        except Exception as e:
            print(f"❌ Spotify auth failed: {e}")
            return None
    
    def search_spotify_target(self, target_key):
        """Zoek één target op Spotify"""
        target = self.targets[target_key]
        
        # Skip als al gevonden
        if target["found"]:
            return False
        
        token = self.get_spotify_token()
        if not token:
            return False
        
        headers = {"Authorization": f"Bearer {token}"}
        artist_variations = target.get("artist_variations", [target["artist"]])
        
        for artist_name in artist_variations:
            try:
                # Artist search
                search_url = f"https://api.spotify.com/v1/search"
                params = {
                    "q": artist_name,
                    "type": "artist",
                    "limit": 3
                }
                response = requests.get(search_url, headers=headers, params=params, timeout=10)
                artists = response.json().get("artists", {}).get("items", [])
                
                for artist in artists:
                    artist_id = artist["id"]
                    
                    # Get recent releases
                    albums_url = f"https://api.spotify.com/v1/artists/{artist_id}/albums"
                    params = {
                        "include_groups": "single,album",
                        "limit": 20
                    }
                    albums_response = requests.get(albums_url, headers=headers, params=params, timeout=10)
                    albums = albums_response.json().get("items", [])
                    
                    # Check elke release
                    for album in albums:
                        album_name = album["name"].lower()
                        
                        # Check alle variations
                        for variation in target["variations"]:
                            if variation.lower() in album_name:
                                # MATCH GEVONDEN!
                                target["found"] = True
                                target["spotify_url"] = album["external_urls"]["spotify"]
                                
                                alert = f"🚨🚨🚨 TARGET GEVONDEN! 🚨🚨🚨\n\n"
                                alert += f"<b>🎯 Target:</b> {target['artist']} - {target['track']}\n"
                                alert += f"<b>✅ Gevonden:</b> {artist['name']} - {album['name']}\n"
                                alert += f"<b>📅 Release:</b> {album.get('release_date', 'Unknown')}\n"
                                alert += f"<b>🔗 Spotify:</b> {album['external_urls']['spotify']}\n\n"
                                alert += f"🔥 GA METEEN DOWNLOADEN! 🔥"
                                
                                self.send_telegram(alert, silent=False)
                                return True
                
                time.sleep(0.5)
                
            except Exception as e:
                print(f"❌ Search error for {artist_name}: {e}")
                continue
        
        return False
    
    def run_full_scan(self):
        """Volledige scan van alle targets"""
        self.scan_count += 1
        self.last_scan_time = datetime.now()
        
        print(f"\n{'='*70}")
        print(f"🔍 SCAN #{self.scan_count} - {self.last_scan_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*70}")
        
        found_something = False
        
        # Scan beide targets
        for target_key, target_info in self.targets.items():
            print(f"\n🎯 Checking: {target_info['artist']} - {target_info['track']}")
            
            if target_info["found"]:
                print(f"  ✅ Already found: {target_info['spotify_url']}")
                continue
            
            found = self.search_spotify_target(target_key)
            if found:
                found_something = True
                print(f"  🔥 FOUND!")
            else:
                print(f"  ❌ Not found yet")
        
        return found_something
    
    def send_status_update(self):
        """Stuur update bericht elke 5 uur"""
        uptime = datetime.now() - self.start_time
        uptime_hours = int(uptime.total_seconds() / 3600)
        
        # Count gevonden tracks
        found_count = sum(1 for t in self.targets.values() if t["found"])
        total_count = len(self.targets)
        
        # Days remaining
        days_until_first = (datetime(2026, 1, 29) - datetime.now()).days
        
        message = f"📊 <b>STATUS UPDATE</b>\n\n"
        message += f"⏰ Scan #{self.scan_count}\n"
        message += f"🕐 Uptime: {uptime_hours} uur\n"
        message += f"📅 Nog {days_until_first} dagen tot release\n\n"
        
        message += f"<b>🎯 Targets ({found_count}/{total_count} gevonden):</b>\n\n"
        
        for target_key, target_info in self.targets.items():
            if target_info["found"]:
                message += f"✅ {target_info['artist']} - {target_info['track']}\n"
                message += f"   🔗 {target_info['spotify_url']}\n\n"
            else:
                message += f"❌ {target_info['artist']} - {target_info['track']}\n"
                message += f"   📅 Release: {target_info['release_date']}\n\n"
        
        if found_count == total_count:
            message += "🎉 <b>ALLE TARGETS GEVONDEN!</b>"
        else:
            message += "🔍 Bot blijft scannen...\n"
            message += "💡 Check ook Heavy Hits handmatig!"
        
        self.send_telegram(message, silent=True)
        print(f"\n✅ Status update verzonden!")
    
    def run_continuous(self):
        """Start 24/7 monitoring loop"""
        startup_msg = f"🚀 <b>BOT GESTART</b>\n\n"
        startup_msg += f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        startup_msg += f"🔄 Scan interval: 5 uur\n"
        startup_msg += f"🎯 Targets: {len(self.targets)}\n\n"
        startup_msg += f"✅ Bot draait nu 24/7!\n"
        startup_msg += f"📱 Je krijgt elke 5 uur een update."
        
        self.send_telegram(startup_msg)
        print(startup_msg.replace("<b>", "").replace("</b>", ""))
        
        # Schedule tasks
        schedule.every(5).hours.do(self.run_full_scan)
        schedule.every(5).hours.do(self.send_status_update)
        
        # Run eerste scan meteen
        self.run_full_scan()
        self.send_status_update()
        
        print(f"\n{'='*70}")
        print(f"🔄 Bot draait nu 24/7. Druk CTRL+C om te stoppen.")
        print(f"{'='*70}\n")
        
        # Main loop
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check elke minuut
                
        except KeyboardInterrupt:
            print(f"\n\n{'='*70}")
            print(f"⛔ Bot gestopt door gebruiker")
            print(f"{'='*70}\n")
            
            stop_msg = f"⛔ <b>BOT GESTOPT</b>\n\n"
            stop_msg += f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            stop_msg += f"📊 Total scans: {self.scan_count}\n"
            stop_msg += f"🕐 Uptime: {int((datetime.now() - self.start_time).total_seconds() / 3600)} uur"
            
            self.send_telegram(stop_msg)
            sys.exit(0)
        
        except Exception as e:
            error_msg = f"❌ <b>BOT ERROR</b>\n\n"
            error_msg += f"Error: {str(e)}\n"
            error_msg += f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            self.send_telegram(error_msg)
            print(f"\n❌ ERROR: {e}\n")
            raise


def main():
    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║           🔥 24/7 CONTINUOUS TARGET MONITOR 🔥               ║
    ║                                                               ║
    ║   Bot draait non-stop en checkt elke 5 uur voor updates     ║
    ║   Je krijgt automatisch Telegram notificaties!               ║
    ║                                                               ║
    ║   🎯 Targets:                                                ║
    ║   • Nass - Luchten (30 jan)                                  ║
    ║   • Jojo Air - Before The Hype (29 jan)                      ║
    ║                                                               ║
    ║   📱 Updates elke 5 uur via Telegram                         ║
    ║   🚨 Instant alert bij vondst!                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)
    
    monitor = ContinuousMonitor()
    monitor.run_continuous()


if __name__ == "__main__":
    main()
