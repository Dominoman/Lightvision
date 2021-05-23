#!/usr/bin/env python3

import config

from lrcat import LRCatalog
from vision import Vision

if __name__ == '__main__':
    catalog = LRCatalog(config.CATALOG, config.ALTERNATEROOT)
    vision = Vision(config.endpoint, config.subscription_key)
    for image in catalog.get_all_image():
        if not image.has_keyword("Visioned"):
            if image.file_format == "JPG":
                result = vision.parse_image(image.get_file_path(), True)
            elif image.file_format == "RAW":
                filename = catalog.get_converted_root_path(image.root_path) + image.path + image.base_name + ".jpg"
                result = vision.parse_image(filename, True)
            else:
                print(f"Skip file:{image.get_file_path()}")
                result = None
            if result is not None:
                image.set_caption(result.description.captions[0].text)
                for tag in result.description.tags:
                    image.set_keyword(tag)

                for imagetag in result.tags:
                    image.set_keyword(imagetag.name)

                for category in result.categories:
                    if category.detail is not None:
                        if category.detail.celebrities is not None:
                            for celebrity in category.detail.celebrities:
                                image.set_keyword(celebrity.name, True)
                        if category.detail.landmarks is not None:
                            for landmark in category.detail.landmarks:
                                image.set_keyword(landmark.name)

                image.set_keyword("Visioned")
    print("Done")
