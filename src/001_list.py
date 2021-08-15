import pandas as pd
import hashlib
import json
import requests
import os
from PIL import Image
import datetime
today = datetime.datetime.now()

prefix = "https://hi-ut.github.io/chukaizuhen_data"

df = pd.read_csv('data/data.csv')

p_category = ""

items = []

images = {
    "https://diyhistory.org/hi/omekac/oa/collections/42/manifest.json" : "/Users/nakamurasatoru/git/d_dzi/iiif0/docs/files/original/chukaizuhen/4256312/4256312-",
    "https://diyhistory.org/hi/omekac/oa/collections/43/manifest.json" : "/Users/nakamurasatoru/git/d_dzi/iiif0/docs/files/original/chukaizuhen/4256313/4256313-"
}

for index, row in df.iterrows():
    category = df.iloc[index]["分類"]
    if not pd.isnull(category):
        p_category = category
    else:
        category = p_category
    print(category)

    label = df.iloc[index]["タイトル"]

    if pd.isnull(label):
        label = "[タイトルなし]"

    url = df.iloc[index]["画像"]
    id = hashlib.md5(url.encode('utf-8')).hexdigest()

    item = {
        "objectID": id,
        "label" : label,
        "分類" : [category],
        "_updated": format(today, '%Y-%m-%d')
    }

    curation_uri = url.split("=")[1].split("&")[0]

    print(curation_uri)

    id2 = hashlib.md5(curation_uri.encode('utf-8')).hexdigest()

    path = "data/curation/" + id2 + ".json"

    if not os.path.exists(path):

        curation = requests.get(curation_uri).json()

        with open(path, 'w') as outfile:
            json.dump(curation, outfile, ensure_ascii=False,
                indent=4, sort_keys=True, separators=(',', ': '))

    with open(path) as f:
        curation = json.load(f)

    pos = int(df.iloc[index]["pos"])

    manifest = curation["selections"][0]["within"]["@id"]
    member = curation["selections"][0]["members"][pos-1]["@id"]

    item["manifest"] = manifest
    item["member"] = member

    img_opath = '../docs/files/medium/' + id + ".jpg"

    if not os.path.exists(img_opath):

        xywh = member.split("=")[1].split(",")

        x = int(xywh[0])
        y = int(xywh[1])
        w = int(xywh[2])
        h = int(xywh[3])

        page = int(member.split("canvas/p")[1].split("#")[0])

        img = images[manifest] + str(page).zfill(2) + ".jp2"
        im = Image.open(img)
        im_crop = im.crop((x, y, x+w, y+h))

        w, h = im_crop.size

        width = 200
        height = int(h * 200 / w)

        im_crop = im_crop.resize((width, height))

        im_crop.save(img_opath)

    item["thumbnail"] = prefix + "/files/medium/" + id + ".jpg"

    with open("../../chukaizuhen/static/data/item/{}.json".format(id), 'w') as outfile:
        json.dump(item, outfile, ensure_ascii=False,
            indent=4, sort_keys=True, separators=(',', ': '))

    fulltext = label + " " + category
    item["fulltext"] = fulltext

    items.append(item)


with open("../../chukaizuhen/static/data/index.json", 'w') as outfile:
    json.dump(items, outfile, ensure_ascii=False,
            indent=4, sort_keys=True, separators=(',', ': '))
