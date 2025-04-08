from typing import List

from baidusearch.baidusearch import search

from src.tool.search.base import SearchItem, WebSearchEngine


class BaiduSearchEngine(WebSearchEngine):
    def perform_search(
        self, query: str, num_results: int = 10, *args, **kwargs
    ) -> List[SearchItem]:

        raw_results = search(query, num_results=num_results)

        results = []
        for i, item in enumerate(raw_results):
            if isinstance(item, str):
                results.append(
                    SearchItem(title=f"Baidu Result {i+1}", url=item, description=None)
                )
            elif isinstance(item, dict):
                # If it's a dictionary with details
                results.append(
                    SearchItem(
                        title=item.get("title", f"Baidu Result {i+1}"),
                        url=item.get("url", ""),
                        description=item.get("abstract", None),
                    )
                )
            else:
                try:
                    results.append(
                        SearchItem(
                            title=getattr(item, "title", f"Baidu Result {i+1}"),
                            url=getattr(item, "url", ""),
                            description=getattr(item, "abstract", None),
                        )
                    )
                except Exception:
                    # Fallback to a basic result
                    results.append(
                        SearchItem(
                            title=f"Baidu Result {i+1}", url=str(item), description=None
                        )
                    )

        return results
