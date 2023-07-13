class SearchResult:
    def __init__(self, results=list()):
        self.results = results

    def append(self, title, link, description):
	    self.results.append((title, link, description))

    def rows(self):
        for title, link, description in self.results:
            yield f"- [{title}]({link}) {description}"

    def __repr__(self):
        return "\n".join([ row for row in self.rows() ])

class Searcher:
    def search(self, query):
        return SearchResult()
