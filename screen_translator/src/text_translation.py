# -*- coding:utf-8 -*-
from google.cloud import translate


class Translator:
    __project_id = None

    def __init__(self, cfg, project_id):
        self.backend = cfg['backend']
        self.source_language = cfg['src_language']
        self.source_word_split = cfg['src_word_split']
        self.target_language = cfg['target_language']
        self.target_word_split = cfg['target_word_split']
        self.client = None
        if self.backend == 'Google':
            self.client = translate.TranslationServiceClient()
            Translator.__project_id = project_id

    def translate_text(self, text, **kwargs):
        if self.backend == 'Google':
            return self.google_translate_text(text)

    def google_translate_text(self, text):
        location = 'global'
        parent = f'projects/{Translator.__project_id}/locations/{location}'

        response = self.client.translate_text(
            contents=[text],
            parent=parent,
            target_language_code=self.target_language,
            source_language_code=self.source_language,
            mime_type='text/plain'
        )
        return response.translations[0].translated_text

    def google_list_language_code(self):
        parent = f'projects/{Translator.__project_id}'
        response = self.client.get_supported_languages(parent=parent)
        for language in response.languages:
            print(f'Language Code: {language.language_code}')
