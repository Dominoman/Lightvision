import config
from lrcat import LRCatalog

if __name__=="__main__":
    catalog = LRCatalog(config.CATALOG, config.ALTERNATEROOT)
    visioned = 0
    for i,image in enumerate(catalog.get_all_image()):
        if image.has_keyword("Visioned"):
            visioned += 1
    print(f"Total images:{i+1}")
    print(f"Visioned images:{visioned}")
    print(f"Percentage:{visioned/(i+1)*100:.2f}%")
    print(f"Not visioned:{(i+1)-visioned}")