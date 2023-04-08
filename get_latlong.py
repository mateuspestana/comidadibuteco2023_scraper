import pandas as pd
import requests
import re
from tqdm import tqdm
tqdm.pandas()
def get_latlong(address, tipo='endereco'):
    if tipo == 'endereco':
        if re.match(r'.*\|.*', address):
            address, bairro = address.split('|')
        if re.match(r'.*–.*', address):
            address, _ = address.split('–')
        address = address.strip()
        if bairro:
            bairro = bairro.split(',')[0].strip()
            address = address + ',' + bairro + ', RJ'
        else:
            address = address + ', RJ'
    else:
        address = address + ',+RJ'
    # print(address)
    url ='https://nominatim.openstreetmap.org/search/?addressdetails=1&q='
    local = url + address + '&limit=1&format=json'
    r = requests.get(local).json()
    try:
        lat = r[0]['lat']
        lon = r[0]['lon']
        bairro = r[0]['address']['suburb']
        city = r[0]['address']['city']
    except:
        lat = ''
        lon = ''
        bairro = ''
        city = ''
    return lat, lon, bairro, city

def get_normal(address):
    url = 'https://nominatim.openstreetmap.org/search/?addressdetails=1&q='
    local = url + address + '&limit=1&format=json'
    r = requests.get(local).json()
    try:
        lat = r[0]['lat']
        lon = r[0]['lon']
        bairro = r[0]['address']['suburb']
        city = r[0]['address']['city']
    except:
        lat = ''
        lon = ''
        bairro = ''
        city = ''
    return lat, lon, bairro, city

def get_subregiao_by_lat_long(lat, lon):
    url = f'https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&addressdetails=1'
    r = requests.get(url).json()
    try:
        distrito = r['address']['city_district']
    except:
        distrito = ''
    return distrito

df = pd.read_excel('dados_restaurantes.xlsx')
df['latitude'], df['longitude'], df['bairro'], df['cidade'] = zip(*df['endereco'].progress_apply(lambda x: get_latlong(x, tipo='endereco')))
df['regiao'] = df.progress_apply(lambda x: get_subregiao_by_lat_long(x['latitude'], x['longitude']), axis=1)
df.to_excel('dados_restaurantes.xlsx', index=False)
