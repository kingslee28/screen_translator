import os
import yaml
import logging

from screen_translation_service import ScreenTranslationService
from text_detection import TextDetector
from text_translation import Translator


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S',
                        handlers=[logging.FileHandler('logs/info.log', encoding='utf-8'), logging.StreamHandler()])
    with open('base/config.yml', 'r') as f:
        cfg = yaml.safe_load(f)

    project_id = os.environ.get('GOOGLE_APPLICATION_PROJECT_ID')
    api_key = os.environ.get('API8_API_KEY')

    text_detector = TextDetector(cfg['text_detection'], api_key)
    translator = Translator(cfg['text_translation'], project_id)
    screen_translation = ScreenTranslationService(cfg['screen_capture'], text_detector, translator, 'dictionary.csv')
