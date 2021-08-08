import os
import yaml
from screen_translation_service import ScreenTranslationService
from text_detection import TextDetector
from text_translation import Translator


if __name__ == '__main__':
    with open('base/config.yml', 'r') as f:
        cfg = yaml.safe_load(f)

    project_id = os.environ.get('GOOGLE_APPLICATION_PROJECT_ID')
    api_key = os.environ.get('API8_API_KEY')

    text_detector = TextDetector(cfg['text_detection'], api_key)
    translator = Translator(cfg['text_translation'], project_id)
    screen_translation = ScreenTranslationService(cfg['screen_capture'], text_detector, translator)
