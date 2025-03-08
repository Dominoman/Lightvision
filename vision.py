import json
import os
from pathlib import Path
from tempfile import gettempdir
from typing import Optional

from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import ImageAnalysis
from msrest.authentication import CognitiveServicesCredentials
from msrest.pipeline import ClientRawResponse
from PIL import Image


class Vision:
    def __init__(self, endpoint: str, subscription_key: str) -> None:
        self.vision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))
        self.save_response = False

    def parse_image(self, filename, save_response: bool = False) -> Optional[ImageAnalysis]:
        if not os.path.exists(filename):
            return None
        stat = os.stat(filename)
        if stat.st_size > 4000000:
            temp_name = self.resize(filename)
            image = open(temp_name, "rb")
        else:
            image = open(filename, "rb")
        # "Categories", "Tags", "Description","ImageType", "Color", "Objects","Brands"
        # "Celebrities", "Landmarks"
        try:
            analyze: ClientRawResponse = self.vision_client.analyze_image_in_stream(image,
                                                                                    ["Categories", "Tags",
                                                                                     "Description", "Brands"],
                                                                                    ["Landmarks"],
                                                                                    raw=True)
        except Exception as e:
            print(e)
            return
        if save_response:
            file_name = Path(filename).with_suffix('.dump')
            with open(file_name, "w") as file:
                parsed = json.loads(analyze.response.content)
                file.write(json.dumps(parsed, indent=4, sort_keys=True))
        return analyze.output

    @staticmethod
    def resize(filename: str) -> str:
        new_name = os.path.join(gettempdir(), "temp.jpg")
        image = Image.open(filename)
        image.save(new_name, optimize=True)
        return new_name
