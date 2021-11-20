# -*- coding:utf-8 -*-
from google.cloud import translate_v3 as translate


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
        location = 'us-central1'
        parent = f'projects/{Translator.__project_id}/locations/{location}'
        glossary = self.client.glossary_path(Translator.__project_id, "us-central1", 'assault_lily')
        glossary_config = translate.TranslateTextGlossaryConfig(glossary=glossary)

        response = self.client.translate_text(
            request={
                'contents': [text],
                'target_language_code': self.target_language,
                'source_language_code': self.source_language,
                'parent': parent,
                'glossary_config': glossary_config}
        )
        return response.glossary_translations[0].translated_text

    def google_list_language_code(self):
        parent = f'projects/{Translator.__project_id}'
        response = self.client.get_supported_languages(parent=parent)
        for language in response.languages:
            print(f'Language Code: {language.language_code}')

    def create_glossary(self, glossary_id, input_uri):
        location = 'us-central1'
        name = self.client.glossary_path(Translator.__project_id, location, glossary_id)
        language_codes_set = translate.types.Glossary.LanguageCodesSet(
            language_codes=[self.source_language, self.target_language]
        )
        gcs_source = translate.types.GcsSource(input_uri=input_uri)
        input_config = translate.types.GlossaryInputConfig(gcs_source=gcs_source)
        glossary = translate.types.Glossary(
            name=name, language_codes_set=language_codes_set, input_config=input_config
        )
        parent = f'projects/{Translator.__project_id}/locations/{location}'
        operation = self.client.create_glossary(parent=parent, glossary=glossary)
        result = operation.result(timeout=180)
        print("Created: {}".format(result.name))
        print("Input Uri: {}".format(result.input_config.gcs_source.input_uri))
