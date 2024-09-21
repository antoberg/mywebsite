import time

ts=int(time.time())

print(ts)
from datetime import datetime

today = datetime.now()

day=today.day
month=today.month
year=today.year
hour=today.hour
minute=today.minute

new=today


d = new.strftime("%m/%d/%Y, %Hh%M:%S")
print(d)