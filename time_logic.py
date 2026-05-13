from datetime import datetime
import pytz

#Logik für Öffnungszeiten
local_tz = pytz.timezone("Europe/Berlin")
aktuell = datetime.now(local_tz)
std_min = aktuell.strftime("%H:%M")  #Format 10:00

#Logik für Begrüssung doppelt da andere Format notwendig
jetzt = datetime.now()
stunde = jetzt.hour

#Begrüssung

if 5 <= stunde < 11:
    begruessung = "Good morning"
elif 11 <= stunde < 18:
    begruessung = "Good afternoon"
else:
    begruessung = "Good evening"

#Börseöffnungszeiten

nyse_nasdaq = "15:30" <= std_min <= "22:00"
lse = "09:30" <= std_min <= "17:30"
tse = "02:00" <= std_min <= "08:00"
crypto = True


