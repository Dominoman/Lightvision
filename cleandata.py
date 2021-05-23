import config
from lrcat import LRCatalog

if __name__ == '__main__':
    catalog = LRCatalog(config.CATALOG)
    for image in catalog.get_all_image():
        image.set_caption("")
        for keyword in image.get_keywords():
            image.remove_keyword(keyword,True)