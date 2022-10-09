import hashlib
import os
import shutil

import bs4
import requests

resolution = "3440x1440"
save_path: str = os.environ["USERPROFILE"] + "/Pictures/Wallpapperaccess.com/"
headurl = "https://wallpaperaccess.com"


def main():
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    page = "/search?q=" + resolution
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'}
    html = requests.get(headurl + page, headers=header).text
    soup_page = bs4.BeautifulSoup(html, 'html.parser')
    dir = {}
    imgs = {}
    for p in soup_page.find_all('a'):
        cell = p.get("class")
        if isinstance(cell, list) and len(cell) == 3 and " ".join(cell) == "ui fluid image":
            print("====================")
            name_collection = p.get("title")
            print(name_collection)
            html_collection = requests.get(headurl + p.get("href"), headers=header).text
            soup_collection = bs4.BeautifulSoup(html_collection, 'html.parser')
            for pict in soup_collection.find_all("div"):
                img = pict.get("data-fullimg")
                if img is not None and pict.get("data-or") == resolution and imgs.get(img) is None:
                    imgs[img] = True
                    r = requests.get(headurl + img, headers=header, stream=True)
                    r.raise_for_status()
                    r.raw.decode_content = True  # support Content-Encoding e.g., gzip
                    name = save_path + name_collection + " " + img.split("/")[2]
                    print(name)
                    with open(name, 'wb') as file:
                        shutil.copyfileobj(r.raw, file)
                    with open(name, 'rb') as f:
                        m = hashlib.md5()
                        while True:
                            data = f.read(8192)
                            if not data:
                                break
                            m.update(data)
                    key = m.hexdigest()
                    if dir.get(key) is None:
                        dir[key] = [name]
                    else:
                        print("duplicate", key, dir[key])
                        dir[key].append(name)
    for d in dir:  # move of duplicates for further manual analysis
        if len(dir[d]) > 1:
            if not os.path.exists(save_path + "Dublicate"):
                os.makedirs(save_path + "Dublicate")
            print(d)
            dupdir = save_path + 'Dublicate/' + d
            os.makedirs(dupdir)
            for p in dir[d]:
                shutil.move(p, dupdir)
                print(p)


if __name__ == '__main__':
    main()
