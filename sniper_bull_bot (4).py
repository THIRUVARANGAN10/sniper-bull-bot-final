#!/usr/bin/env python3
"""
SNIPER BULL BOT - FINAL VERSION
Uses JSON method for Telegram API
"""

import sys
import urllib.request
import json
import yfinance as yf
from datetime import datetime
import time
from collections import defaultdict

TOKEN = "8641975809:AAEi00c0QhsPkuFpPDmuLe7eM8iPynlOsIM"
CHAT_ID = "6408770437"

PAIRS = {
    "EUR/USD": "EURUSD=X",
    "GBP/USD": "GBPUSD=X",
    "USD/JPY": "JPYUSD=X",
    "AUD/USD": "AUDUSD=X",
    "CAD/USD": "CADUSD=X",
    "NZD/USD": "NZDUSD=X",
    "USD/CHF": "CHFUSD=X",
    "GOLD": "GC=F",
    "MNQ": "MNQ=F"
}

ALERTS_SENT = defaultdict(set)

def send_alert(msg):
    """Send alert using JSON method"""
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        
        payload = {
            "chat_id": int(CHAT_ID),
            "text": msg
        }
        
        data = json.dumps(payload).encode('utf-8')
        
        req = urllib.request.Request(
            url,
            data=data,
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
            
            if result.get('ok'):
                print(f"   ✅ Alert sent")
                return True
    except:
        pass
    
    return False

def get_data(symbol, tf="5m"):
    try:
        return yf.download(symbol, interval=tf, period="30d", progress=False, repair=False)
    except:
        return None

def find_swings(data, lookback=3):
    if data is None or len(data) < lookback + 2:
        return [], []
    
    highs, lows = [], []
    
    try:
        high_vals = data['High'].values
        low_vals = data['Low'].values
        
        for i in range(lookback, len(data) - 1):
            curr_high = high_vals[i]
            curr_low = low_vals[i]
            
            prev_high_max = high_vals[i-lookback:i].max()
            next_high_max = high_vals[i+1:i+2].max()
            
            prev_low_min = low_vals[i-lookback:i].min()
            next_low_min = low_vals[i+1:i+2].min()
            
            if curr_high > prev_high_max and curr_high > next_high_max:
                highs.append(float(curr_high))
            
            if curr_low < prev_low_min and curr_low < next_low_min:
                lows.append(float(curr_low))
    except:
        pass
    
    return highs, lows

def check_level(symbol, pair, data, level_type, level, tf):
    if data is None or len(data) == 0:
        return
    
    try:
        high = float(data['High'].iloc[-1])
        low = float(data['Low'].iloc[-1])
        close = float(data['Close'].iloc[-1])
        time_str = data.index[-1].strftime('%H:%M')
        
        key = f"{pair}_{tf}_{level_type}_{level:.5f}_{datetime.now().date()}"
        if key in ALERTS_SENT[pair]:
            return
        
        triggered = False
        
        if "High" in level_type or "PDH" in level_type or "London High" in level_type:
            if high >= level * 0.9999 or close > level:
                triggered = True
        else:
            if low <= level * 1.0001 or close < level:
                triggered = True
        
        if triggered:
            msg = f"ALERT {level_type}\n{pair} {tf}\nLevel: {level:.5f}\nPrice: {close:.5f}\nTime: {time_str}"
            print(f"   🎯 {level_type}")
            send_alert(msg)
            ALERTS_SENT[pair].add(key)
    except:
        pass

def scan(pair, symbol):
    print(f"  {pair}...", end="", flush=True)
    
    try:
        for tf in ["5m", "1h"]:
            try:
                data = get_data(symbol, tf)
                if data is None or len(data) < 10:
                    continue
                
                highs, lows = find_swings(data)
                
                if len(highs) > 0:
                    check_level(symbol, pair, data, "Liquidity High", highs[-1], tf)
                if len(lows) > 0:
                    check_level(symbol, pair, data, "Liquidity Low", lows[-1], tf)
                
                try:
                    daily = get_data(symbol, "1d")
                    if daily is not None and len(daily) >= 2:
                        london_high = float(daily['High'].iloc[-2])
                        london_low = float(daily['Low'].iloc[-2])
                        pdh = float(daily['High'].iloc[-2])
                        pdl = float(daily['Low'].iloc[-2])
                        
                        check_level(symbol, pair, data, "London High", london_high, tf)
                        check_level(symbol, pair, data, "London Low", london_low, tf)
                        check_level(symbol, pair, data, "PDH", pdh, tf)
                        check_level(symbol, pair, data, "PDL", pdl, tf)
                except:
                    pass
            except:
                continue
        
        print(" ✓")
    except:
        print(f" ✗")

def main():
    print("\n" + "="*70)
    print("🚀 SNIPER BULL TRADING ALERT BOT")
    print("="*70)
    print(f"Chat ID: {CHAT_ID}")
    print(f"Pairs: {', '.join(PAIRS.keys())}")
    print("="*70)
    
    print("\n📤 Sending test alert...")
    send_alert("Sniper Bull Bot Online - All Systems Ready!")
    
    count = 0
    while True:
        try:
            count += 1
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Scan #{count}")
            
            for pair, symbol in PAIRS.items():
                scan(pair, symbol)
            
            print(f"\n⏳ Next scan in 300s...")
            time.sleep(300)
        
        except KeyboardInterrupt:
            print("\n\n✓ Bot stopped")
            break
        except Exception as e:
            print(f"\n⚠️  Continuing...")
            time.sleep(5)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n\n❌ ERROR: {e}")
