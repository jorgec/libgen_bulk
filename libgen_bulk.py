import os
import click
import requests
from tqdm import tqdm
from bs4 import BeautifulSoup
from termcolor import colored
from slugify import slugify

download_base_url = 'http://93.174.95.29'

def soupify(content):
    return BeautifulSoup(content, 'html.parser')

def dl(url: str, out_path: str):
    url = url.strip()
    if not url:
        return
    download_url = download_base_url + '/_ads/' + url.split("md5=")[1]
    response = requests.get(download_url)
    html_soup = soupify(response.content)
    file_url = download_base_url + html_soup.find(id='info').find('a').get('href')
    file_name = html_soup.select('tr h1')[0].text   

    ext = html_soup.find(id='info').find('a').get('href').split('.')[-1]

    sanitized = slugify(file_name)
    out_file = f'{sanitized}.{ext}'
    print(f"Downloading {out_file}")

    file = requests.get(file_url, stream=True)
    total_size = int(file.headers.get('content-length', 0))
    block_size = 1024
    t = tqdm(total=total_size, unit='iB', unit_scale=True)
    out_file_name = os.path.join(out_path, out_file)
    
    with open(out_file_name, 'wb') as f:
        for data in file.iter_content(block_size):
            t.update(len(data))
            f.write(data)
        # f.write(file.content)
    t.close()
    print(f'Downloaded book: {file_name}')

@click.command()
@click.option('--outdir', default='out', help='Location for where to store the downloaded files')
@click.option('--source', prompt='Source file', help='A file containing a list of links for books to download (one link per line)', default='sources.txt')
def libgen(source, outdir):
    base_path = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.join(base_path, outdir)

    if not os.path.exists(out_path):
        os.makedirs(out_path)

    with open(source, 'r') as src:
        for url in src:
            dl(url=url, out_path=out_path)
    

if __name__ == '__main__':
    libgen()