import pprint
import requests
import sys
import pandas as pd
from datetime import datetime

api_key = "9b656c6f5237727cdf1e35288a7afa8c"
geo_URL = 'http://api.openweathermap.org/geo/1.0/direct'

loc = [
  'Buenos Aires, Argentina',
  'Guangzhou, China',
  'Wichita, Kansas',
  'Niskayuna, New York',
  'Gwangmyeong, South Korea',
  'Taipei, Taiwan',
  'Nanaimo, British Columbia',
  'Chennai, India',
  'Barrington, Illinois',
  'Littleton, Colorado',
  'Peterhead, Scotland',
  'Vizag, India',
  'Des Moines, Iowa',
  'Beijing, China',
  'Killeen, Texas',
  'Morehead City, North Carolina'
]

df_wide = pd.DataFrame(index=loc)
######

for city in loc:
    geo = f'{geo_URL}?q={city}&limit=5&appid={api_key}'
    resp = requests.get( geo )

    if resp.status_code != 200: # Failure?
        print( f'Error geocoding {city}: {resp.status_code}' )
        sys.exit( 1 )

    # OpenWeatherMap returns a list of matching cities, up to the limit specified
    # in the API call; even if you only ask for one city (limit=5), it's still
    # returned as a 1-element list

    if len( resp.json() ) == 0: # No such city?
        print( f'Error locating city {city}; {resp.status_code}' )
        sys.exit( 2 )

    json = resp.json()
    if type( json ) == list: # List of cities?
        lat = json[ 0 ][ 'lat' ]
        lon = json[ 0 ][ 'lon' ]
    else: # Unknown city?
        print( f'Error, invalid data returned for city {city}, {resp.status_code}' )
        sys.exit( 3 )

    # Use Peterhead's latitude and longitude to get its 5-day forecast in 3-hour blocks

    forecast_URL = 'http://api.openweathermap.org/data/2.5/forecast'
    forecast = f'{forecast_URL}?lat={lat}&lon={lon}&appid={api_key}'
    resp = requests.get( forecast )

    if resp.status_code != 200: # Failure?
        print( f'Error retrieving data: {resp.status_code}' )
        sys.exit( 4 )

    data = resp.json()
##### 

    data_list = []
    for i in range(len(data['list'])):
        forecast_data = data[ 'list' ][ i ]
        dt = datetime.strptime(forecast_data['dt_txt'], '%Y-%m-%d %H:%M:%S')
        temp_max = forecast_data['main']['temp_max']
        temp_min = forecast_data['main']['temp_min']
        data_list.append({
            'city': city,
            'datetime': dt,
            'temp_max': temp_max,
            'temp_min': temp_min
        })

    df = pd.DataFrame(data_list)
#####

    df_grouped = df.groupby(pd.Grouper(key='datetime', axis=0, freq='D')).aggregate({
        'city': lambda x: x.iloc[0],
        'temp_max': 'max',
        'temp_min': 'min'})
    
#####

    for i, day in enumerate(df_grouped.index, start=0):
        if i>4:
            break
        df_wide.loc[city, f'Min_{i}'] = df_grouped.loc[day, 'temp_min']
        df_wide.loc[city, f'Max_{i}'] = df_grouped.loc[day, 'temp_max']   

#####

df_wide = df_wide.drop(columns=['Min_0', 'Max_0'])
df_wide = df_wide.iloc[:] - 273.15
df_wide = df_wide.reset_index()
df_wide = df_wide.rename({'index': 'City'}, axis='columns')
df_wide['Min_Avg'] = df_wide[['Min_1', 'Min_2', 'Min_3', 'Min_4']].mean(axis=1).round(2)
df_wide['Max_Avg'] = df_wide[['Max_1', 'Max_2', 'Max_3', 'Max_4']].mean(axis=1).round(2)


df_wide.columns = df_wide.columns.str.replace('_', ' ')
df_wide.to_csv('temp.csv', index=False, float_format='%.2f')