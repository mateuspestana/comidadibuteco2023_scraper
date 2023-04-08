# Script de raspagem do Comida di Buteco 2023
# Autor: Matheus C. Pestana <matheus.pestana@iesp.uerj.br>

import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from tqdm import tqdm

# URL da página
url = 'https://comidadibuteco.com.br/category/butecos/rio-de-janeiro/page/'
links_restaurantes = []
dados_restaurantes = []

# Cria uma sessão
session = requests.Session()
# Tem 11 páginas de restaurantes
for pagina in range(1, 12):
    # Faz a requisição
    # print(f'Pegando página {pagina}')
    r = session.get(url + str(pagina) + '/')
    # Cria o objeto BeautifulSoup
    soup = BeautifulSoup(r.text, 'lxml')
    # Encontra o elemento que contém o link para a próxima página
    restaurantes_container = soup.find_all('div', {'class': 'col-12'})
    for i, restaurantes in enumerate(restaurantes_container):
        if i < 12:
            links_restaurantes.append(restaurantes.find_all('a')[0].get('href'))

# Agora abre cada restaurante e pega os dados
session = requests.Session()
for restaurante in links_restaurantes:
    # Faz a requisição
    r = session.get(restaurante)
    # Cria o objeto BeautifulSoup
    soup = BeautifulSoup(r.text, 'lxml')
    # Pega os dados de cada restaurante
    titulo = soup.find('h2', {'class': 'title'})
    foto = soup.find('img', {'title': 'Buteco'}).get('src')
    infos = soup.find('div', {'class': 'col-8 text-left'})
    nome_prato = infos.p.strong
    nome_prato = str(nome_prato.text).replace('Prato: ', '')
    print(f"Raspando o restaurante {soup.title.text.split('–')[0].strip()}")
    print(f"--- Prato: {nome_prato}")
    escaped_prato = re.sub(r'([^\w\s])', r'\\\1', nome_prato)
    descricao_prato = re.search(f"(?<={escaped_prato}).*?(?=\n)", infos.text).group()
    endereco = re.search("(?<=Endereço:).*?(?=\n)", infos.text).group()
    if re.match(r'.*\|.*', endereco):
        bairro = endereco.split('|')[1].strip()
    else:
        bairro = ''
    # bairro = endereco.split('|').strip()
    telefone = re.search('\(\d+\) \d{4,5}-\d+', infos.text).group()
    horario = re.search("(?<=Horário:).*", infos.text).group()

    dados = {'restaurante': titulo.text,
                'foto': foto,
                'nome_prato': nome_prato,
                'descricao_prato': descricao_prato,
                'endereco': endereco,
                'bairro': bairro,
                'telefone': telefone,
                'horario': horario,
             'link': restaurante}
    dados_restaurantes.append(dados)

pd.DataFrame(dados_restaurantes).to_excel('dados_restaurantes.xlsx', index=False)
