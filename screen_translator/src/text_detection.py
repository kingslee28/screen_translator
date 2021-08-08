import requests
from google.cloud import vision


class TextDetector:
    __api_key = None

    def __init__(self, cfg, api_key):
        self.backend = cfg['backend']
        self.language = None
        self.client = None
        if self.backend == 'Google':
            self.client = vision.ImageAnnotatorClient()
        elif self.backend == 'api8':
            TextDetector.__api_key = api_key
            self.language = cfg['language']

    def detect_text_from_image(self, path, **kwargs):
        if self.backend == 'Google':
            return self.google_detect_text(path, **kwargs)
        elif self.backend == 'api8':
            return self.api8_detect_text(path)

    def google_detect_text(self, path, vertex=False):
        with open(path, 'rb') as image_file:
            content = image_file.read()

        image = vision.Image(content=content)
        response = self.client.text_detection(image=image)
        if response.error.message:
            raise Exception(response.error.message)

        texts = response.text_annotations
        detection = texts[0].description.replace('\n', '').replace(' ', '')
        if vertex:
            for text in texts:
                vertices = ([f'({vertex.x},{vertex.y})' for vertex in text.bounding_poly.vertices])
                print(f'label: {text.description} bounds: {",".join(vertices)}')
        return detection

    def api8_detect_text(self, path):
        payload = {
            'apikey': TextDetector.__api_key,
            'isOverlayRequired': False,
            'FileType': '.png',
            'IsCreateSearchablePDF': False,
            'detectOrientation': True,
            'language': self.language,
        }
        response = requests.post(
            'https://api8.ocr.space/parse/image', data=payload, files={'img': open(path, 'rb')})
        detection = response.content.decode()
        start = detection.find('ParsedText') + 13
        end = detection.find('ErrorMessage', start) - 3
        detection = detection[start:end]
        detection = detection.replace('\\n', '').replace('\\r', '')
        return detection
