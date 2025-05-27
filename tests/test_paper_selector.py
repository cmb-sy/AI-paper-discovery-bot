import unittest
from src.services.paper_selector import select_papers
from src.models.paper import Paper

class TestPaperSelector(unittest.TestCase):

    def setUp(self):
        self.papers = [
            Paper(title="AI in Healthcare", authors=["Author A"], summary="A study on AI applications in healthcare."),
            Paper(title="Machine Learning for Finance", authors=["Author B"], summary="Exploring ML techniques in finance."),
            Paper(title="Deep Learning Advances", authors=["Author C"], summary="Recent advancements in deep learning.")
        ]

    def test_select_papers_by_keyword(self):
        selected = select_papers(self.papers, keyword="AI")
        self.assertEqual(len(selected), 1)
        self.assertEqual(selected[0].title, "AI in Healthcare")

    def test_select_papers_empty_list(self):
        selected = select_papers([], keyword="AI")
        self.assertEqual(selected, [])

    def test_select_papers_no_match(self):
        selected = select_papers(self.papers, keyword="Blockchain")
        self.assertEqual(selected, [])

if __name__ == '__main__':
    unittest.main()