import os
from PIL import Image
import requests
from bs4 import BeautifulSoup
import numpy as np

# --------- crawler part ---------------

r = requests.get("http://colorlisa.com/")

soup = BeautifulSoup(r.text, "html.parser")

artist_nodes = soup.find_all("section", class_="artist")

print("colorlisa provides color palette of", len(artist_nodes), "artists.")

artists = {}

for artist_node in artist_nodes:
    items = artist_node.find_all("div", class_="artist__item")
    first_name = items[0].h2.em.string
    last_name = items[0].h2.strong.string
    name = first_name + " " + last_name
    artists[name] = []
    for item in items[1:-1]:
        paint_name = item.find("h3", class_="palette__author").strong.string
        paint_link = item.find("h3", class_="palette__author").a["href"]
        palettes = [color.string for color in item.find_all("span", class_="palette__code")]
        artists[name].append({
          "name": paint_name,
          "link": paint_link,
          "palette": palettes
        })

# --------- markdown generation part ---------------

paint_template = """
### [{paint_name}]({paint_link})
|![{c1}]({i1})|![{c2}]({i2})|![{c3}]({i3})|![{c4}]({i4})|![{c5}]({i5})|
|:-:|:-:|:-:|:-:|:-:|
|{c1}|{c2}|{c3}|{c4}|{c5}|
"""

artist_template = """
## {artist_name}
{content}
"""

markdown = """
# color lisa palettes

This repo crawled the beautiful palettes from [colorlisa](http://colorlisa.com/) as for the original page may not suit to laptop or PC screen.

"""

created_imgs = [f.split(".")[0] for f in os.listdir("img")]

def create_img(color, h, w):
    if color in created_imgs:
        # print(color, "img already created")
        return
    r, g, b = tuple(int(color[i+1:i+3], 16) for i in (0, 2, 4))
    data = np.zeros((h, w, 3))
    data[:, :, 0] = r
    data[:, :, 1] = g
    data[:, :, 2] = b
    img = Image.fromarray(data.astype("uint8")).convert("RGB")
    img.save("img/{}.png".format(color))


for name, paints in artists.items():
    paint_md = ""
    for paint in paints:
        palette_table_md = ""
        p = paint["palette"]
        assert len(p) == 5
        for color in p:
            create_img(color, 50, 100)
        imgs = ["img/{}.png".format(color) for color in p]
        paint_md += paint_template.format(paint_name=paint["name"], paint_link=paint["link"],
                                          c1=p[0], c2=p[1], c3=p[2], c4=p[3], c5=p[4],
                                          i1=imgs[0], i2=imgs[1], i3=imgs[2], i4=imgs[3], i5=imgs[4])
    markdown += artist_template.format(artist_name=name, content=paint_md)

with open("README.md", "w") as f:
    f.write(markdown)
