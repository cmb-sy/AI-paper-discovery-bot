class Paper:
    def __init__(self, title, authors, abstract):
        self.title = title
        self.authors = authors
        self.abstract = abstract

    def __repr__(self):
        return f"Paper(title={self.title}, authors={self.authors}, abstract={self.abstract})"