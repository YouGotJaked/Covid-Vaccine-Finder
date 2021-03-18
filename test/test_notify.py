import pandas as pd

import context
from covid.notify.msg import email, text

ts_old = '2021-03-14 21:19:00-05:00'
ts_new = '2021-03-18 09:21:00-05:00'
rows = [['San Jose', 'Fully Booked', ts_old],
        ['Campbell', 'Fully Booked', ts_old],
        ['Los Gatos', 'Available', ts_old],
        ['Santa Clara', 'Fully Booked', ts_old],
        ['Yorba Linda', 'Available', ts_old],
        ['San Jose', 'Available', ts_new],
        ['Campbell', 'Fully Booked', ts_new],
        ['Los Gatos', 'Available', ts_new],
        ['Santa Clara', 'Fully Booked', ts_new],
        ['Yorba Linda', 'Available', ts_new]]
df = pd.DataFrame(rows, columns=['city', 'status', 'timestamp'])
city_filter = (((df.city=='San Jose') | (df.city=='Santa Clara') |
                (df.city=='Campbell') | (df.city=='Los Gatos'))
               & (df.timestamp==ts_new))
df_avail = df[city_filter & (df.status=='Available')]
cities = (', ').join(df_avail.city.values)
msg = "Vaccines available in the following cities: " + cities
email(msg)
text(msg)
