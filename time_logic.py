from datetime import datetime
from zoneinfo import ZoneInfo
 
local_tz = ZoneInfo("Europe/Berlin")
aktuell = datetime.now(local_tz)
std_min = aktuell.strftime("%H:%M")
 
# 0 = Montag, 6 = Sonntag
wochentag = aktuell.weekday()
ist_wochentag = wochentag < 5  # Montag–Freitag
 
# Begrüssung
jetzt = aktuell  # kein zweites datetime.now() nötig
stunde = jetzt.hour
 
if 5 <= stunde < 11:
    begruessung = "Good morning"
elif 11 <= stunde < 18:
    begruessung = "Good afternoon"
else:
    begruessung = "Good evening"
 
# Börseöffnungszeiten (nur Wochentags)
nyse_nasdaq = ist_wochentag and "15:30" <= std_min <= "22:00"
lse         = ist_wochentag and "09:30" <= std_min <= "17:30"
tse         = ist_wochentag and "02:00" <= std_min <= "08:00"
dax_six     = ist_wochentag and "09:00" <= std_min <= "17:30"
crypto      = True  # Crypto 24/7
