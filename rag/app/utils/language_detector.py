from langdetect import detect

lang_map = {
    'en': 'English',
    'de': 'German'
}


class LanguageDetector:
    @staticmethod
    def get_language(text):
        try:
            lang = detect(text)
            return lang_map.get(lang, 'English')
        except Exception as e:
            return 'English'
