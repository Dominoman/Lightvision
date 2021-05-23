import json
import os
from pathlib import Path
from typing import Optional

from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import ImageAnalysis
from msrest.authentication import CognitiveServicesCredentials
from msrest.pipeline import ClientRawResponse


class Vision:
    def __init__(self, endpoint: str, subscription_key: str) -> None:
        self.vision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))
        self.save_response = False

    def parse_image(self, filename, save_response: bool = False) -> Optional[ImageAnalysis]:
        if os.path.exists(filename):
            image = open(filename, "rb")
            # "Categories", "Tags", "Description","ImageType", "Color", "Objects","Brands"
            # "Celebrities", "Landmarks"
            analyze: ClientRawResponse = self.vision_client.analyze_image_in_stream(image,
                                                                                    ["Categories", "Tags",
                                                                                     "Description", "Brands"],
                                                                                    ["Celebrities", "Landmarks"],
                                                                                    raw=True)
            if save_response:
                file_name = Path(filename).with_suffix('.dump')
                file = open(file_name, "w")
                parsed = json.loads(analyze.response.content)
                file.write(json.dumps(parsed, indent=4, sort_keys=True))
                file.close()

            return analyze.output
        return None
