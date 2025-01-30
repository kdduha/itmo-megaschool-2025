from duckduckgo_search import DDGS
from typing import List, Dict


class DuckDuckGoClientError(Exception):
    """
    Exception raised for errors occurring in the DuckDuckGoClient.
    """
    pass


class DuckDuckGoClient:
    """
    A client for interacting with the DuckDuckGo search API.

    Methods
    -------
    search(query: str, num: int, language: str) -> List[Dict]
        Executes a search query and returns a list of search results.
    """

    def __init__(self) -> None:
        """
        Initializes the DuckDuckGoClient.
        """
        self._client = DDGS()

    def search(self, query: str, num: int, language: str) -> List[Dict]:
        """
        Executes a search query and returns a list of search results.

        Parameters
        ----------
        query : str
            The search query string.
        num : int
            The number of search results to return.
        language : str
            The region/language filter for search results (e.g., 'us-en' for English in the US).

        Returns
        -------
        List[Dict]
            A list of dictionaries containing the search results.

        Raises
        ------
        DuckDuckGoClientError
            If the API request fails or an error occurs during the search.
        """
        try:
            response = self._client.text(query, max_results=num, region=language)
            return response
        except Exception as e:
            raise DuckDuckGoClientError(f"Error during the API request: {str(e)}")
