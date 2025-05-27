import requests

class ArxivAPI:
    BASE_URL = "http://export.arxiv.org/api/query?"

    def __init__(self, search_query="AI OR machine learning", max_results=5):
        self.search_query = search_query
        self.max_results = max_results

    def fetch_papers(self):
        query = f"search_query={self.search_query}&start=0&max_results={self.max_results}"
        response = requests.get(self.BASE_URL + query)
        
        if response.status_code == 200:
            return self.parse_response(response.text)
        else:
            raise Exception(f"Error fetching papers: {response.status_code}")

    def parse_response(self, response_text):
        from xml.etree import ElementTree as ET
        
        papers = []
        root = ET.fromstring(response_text)
        for entry in root.findall("{http://www.w3.org/2005/Atom}entry"):
            title = entry.find("{http://www.w3.org/2005/Atom}title").text
            authors = [author.find("{http://www.w3.org/2005/Atom}name").text for author in entry.findall("{http://www.w3.org/2005/Atom}author")]
            summary = entry.find("{http://www.w3.org/2005/Atom}summary").text
            papers.append({
                "title": title,
                "authors": authors,
                "summary": summary
            })
        return papers