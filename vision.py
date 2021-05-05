import os
from typing import Optional

from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import ImageAnalysis
from msrest.authentication import CognitiveServicesCredentials


class Vision:
    def __init__(self, endpoint: str, subscription_key: str) -> None:
        self.vision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))

    def parse_image(self, filename) -> Optional[ImageAnalysis]:
        if os.path.exists(filename):
            image = open(filename, "rb")
            # "Categories", "Tags", "Description","ImageType", "Color", "Objects","Brands"
            # "Celebrities", "Landmarks"
            analyze = self.vision_client.analyze_image_in_stream(image,
                                                                 ["Categories", "Tags", "Description", "Brands"],
                                                                 ["Celebrities", "Landmarks"])
            return analyze
        return None
