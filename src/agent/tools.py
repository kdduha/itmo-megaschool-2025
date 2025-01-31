import os
from src.clients.google import GoogleSearchClient
from src.clients.duckduckgo import DuckDuckGoClient
from crewai.tools import tool


@tool("Search")
def search_tool(search_query: str) -> dict:
    """
    Main logic for performing search queries through Google and DuckDuckGo.

    Args:
        search_query (str): The search query to be used in both search engines.

    Returns:
        dict: A dictionary containing the search results from Google and DuckDuckGo,
              with the keys 'google_results' and 'duckduckgo_results' respectively.
    """

    google_client = GoogleSearchClient(os.getenv("GOOGLE_SEARCH_API_KEY"), os.getenv("GOOGLE_SEARCH_CX"))
    duckduckgo_client = DuckDuckGoClient()

    def fetch_google_results():
        """
        Fetch search results from Google using the provided client.

        Returns:
            list: A list of search results returned by the Google search.
                  If an error occurs, an empty list is returned.
        """
        try:
            return google_client.search(query=search_query, num=3, language="lang_ru")
        except Exception as e:
            print(f"Error during Google search: {e}")
            return []

    def fetch_duckduckgo_results():
        """
        Fetch search results from DuckDuckGo using the provided client.

        Returns:
            list: A list of search results returned by the DuckDuckGo search.
                  If an error occurs, an empty list is returned.
        """
        try:
            return duckduckgo_client.search(query=search_query, num=5, language="ru-ru")
        except Exception as e:
            print(f"Error during DuckDuckGo search: {e}")
            return []

    google_results = fetch_google_results()
    duckduckgo_results = fetch_duckduckgo_results()

    return {
        "google_results": google_results,
        "duckduckgo_results": duckduckgo_results
    }
