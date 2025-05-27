import unittest
from src.services.translator import Translator

class TestTranslator(unittest.TestCase):

    def setUp(self):
        self.translator = Translator()

    def test_translate_summary(self):
        english_summary = "This paper discusses the advancements in AI and machine learning."
        expected_japanese_summary = "この論文はAIと機械学習の進展について論じています。"
        translated_summary = self.translator.translate(english_summary)
        self.assertEqual(translated_summary, expected_japanese_summary)

    def test_translate_empty_string(self):
        english_summary = ""
        expected_japanese_summary = ""
        translated_summary = self.translator.translate(english_summary)
        self.assertEqual(translated_summary, expected_japanese_summary)

    def test_translate_invalid_input(self):
        with self.assertRaises(ValueError):
            self.translator.translate(None)

if __name__ == '__main__':
    unittest.main()