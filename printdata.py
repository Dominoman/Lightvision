#!/usr/bin/env python3

import config
from lrcat import LRCatalog

if __name__ == '__main__':
    catalog = LRCatalog(config.CATALOG, config.ALTERNATEROOT)
    print("Keywords:")
    for keyword in catalog.get_keywords():
        print(f'{catalog.get_keyword_id(keyword)} {keyword}')
    print(f'Max id:{catalog.get_max_id()}')
    for image in catalog.get_all_image():
        print(f'ID:{image.id}')
        print(image.get_file_path())
        print(image.get_caption())
        print(image.get_keywords())
        print()
