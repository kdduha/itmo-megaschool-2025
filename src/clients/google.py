import requests
from typing import List, Dict, Optional

BASE_URL: str = "https://www.googleapis.com/customsearch/v1"


class GoogleSearchClientError(Exception):
    """
    Exception raised for errors occurring in the GoogleSearchClient.
    """
    pass


def _parse_search_result(response: Dict) -> Dict:
    """
    Parses an individual search result from the API response.

    Parameters
    ----------
    response : Dict
        The raw search result dictionary from the API response.

    Returns
    -------
    Dict
        A formatted dictionary containing the title, description, source URL, and additional metadata.
    """
    return {
        "title": response.get("title", ""),
        "description": response.get("snippet", ""),
        "source": response.get("link", ""),
        "metainfo": response.get("pagemap", {})
    }


class GoogleSearchClient:
    """
    A client for interacting with the Google Custom Search API.

    Methods
    -------
    search(query: str, num: int, language: str) -> List[Dict]
        Executes a search query and returns a list of formatted search results.
    """

    def __init__(self, api_key: str, cx: str) -> None:
        """
        Initializes the GoogleSearchClient with the given API key and search engine ID.

        Parameters
        ----------
        api_key : str
            The API key used for authenticating requests to the Google API.
        cx : str
            The Programmable Search Engine ID used to specify the search engine for queries.
        """
        self._api_key = api_key
        self._cx = cx
        self._base_url = BASE_URL

    def search(self, query: str, num: int, language: str) -> List[Dict]:
        """
        Executes a search query and returns a list of formatted search results.

        Parameters
        ----------
        query : str
            The search query string.
        num : int
            The number of search results to return (maximum of 10).
        language : str
            The language filter for search results (e.g., 'lang_en' for English).

        Returns
        -------
        List[Dict]
            A list of dictionaries containing the search results. Each dictionary includes
            the title, description, source URL, and metadata of the result.
            Returns an empty list if no results are found.

        Raises
        ------
        GoogleSearchClientError
            If the API request fails or returns an error.
        """
        params = {
            "key": self._api_key,
            "cx": self._cx,
            "q": query,
            "lr": language,
            "num": num
        }

        try:
            response = requests.get(self._base_url, params=params)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise GoogleSearchClientError(f"Error during the API request: {str(e)}")

        data = response.json()
        if "items" in data:
            return [_parse_search_result(item) for item in data["items"]]
        else:
            return []
