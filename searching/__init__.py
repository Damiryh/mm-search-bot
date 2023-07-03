class SearchResult:
    def __init__(self, results=list()):
        self.results = results

    def append(self, title, link, description):
	    self.results.append((title, link, description))

    def __repr__(self):
        return "\n".join([
            f"- [{title}]({link}) {description}"
            for title, link, description in self.results
        ])

class Searcher:
    def search(self, query):
        return SearchResult()
