#!/usr/bin/env python3
"""
Test script voor continuous_monitor.py
Draait 1 scan en stopt dan
"""

import sys
from continuous_monitor import ContinuousMonitor

def test_monitor():
    print("="*70)
    print("🧪 TESTING CONTINUOUS MONITOR")
    print("="*70)
    
    monitor = ContinuousMonitor()
    
    print("\n1️⃣ Testing Telegram connection...")
    success = monitor.send_telegram("🧪 Test bericht van continuous monitor!", silent=True)
    if success:
        print("   ✅ Telegram works!")
    else:
        print("   ❌ Telegram failed!")
        return False
    
    print("\n2️⃣ Testing Spotify auth...")
    token = monitor.get_spotify_token()
    if token:
        print(f"   ✅ Spotify auth works! (Token: {token[:20]}...)")
    else:
        print("   ❌ Spotify auth failed!")
        return False
    
    print("\n3️⃣ Running one full scan...")
    monitor.run_full_scan()
    
    print("\n4️⃣ Sending status update...")
    monitor.send_status_update()
    
    print("\n" + "="*70)
    print("✅ ALL TESTS PASSED!")
    print("="*70)
    print("\n💡 Check je Telegram - je zou 2 berichten moeten hebben:")
    print("   1. Test bericht")
    print("   2. Status update")
    print("\n🚀 Als alles werkt, deploy naar Railway!")
    
    return True

if __name__ == "__main__":
    try:
        success = test_monitor()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
