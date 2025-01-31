import asyncio
from src.clients.google import GoogleSearchClient
from src.clients.duckduckgo import DuckDuckGoClient
from src.clients.gpt import OpenAIClient
from src.constants import SYSTEM_PROMPT, USER_PROMPT
from dotenv import load_dotenv
import os

load_dotenv()


def fetch_google_results(google_client, query):
    try:
        return google_client.search(query=query, num=3, language="lang_ru")
    except Exception as e:
        print(f"Ошибка при выполнении запроса к Google: {e}")
        return []


def fetch_duckduckgo_results(duckduckgo_client, query):
    try:
        return duckduckgo_client.search(query=query, num=5, language="ru-ru")
    except Exception as e:
        print(f"Ошибка при выполнении запроса к DuckDuckGo: {e}")
        return []  # Возвращаем пустой список в случае ошибки


async def main():
    google_search_api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
    google_search_cx = os.getenv("GOOGLE_SEARCH_CX")

    openai_api_key = os.getenv("OPENAI_API_KEY")
    openai_tunnel_url = os.getenv("OPENAI_TUNNEL_URL")
    model = os.getenv("OPENAI_MODEL")

    query = "В каком году Университет ИТМО был включён в число Национальных исследовательских университетов России?\n1. 2007\n2. 2009\n3. 2011\n4. 2015"
    search_query = query.split("\n")[0]

    google_client = GoogleSearchClient(google_search_api_key, google_search_cx)
    duckduckgo_client = DuckDuckGoClient()

    google_results, duckduckgo_results = await asyncio.gather(
        asyncio.to_thread(fetch_google_results, google_client, search_query),
        asyncio.to_thread(fetch_duckduckgo_results, duckduckgo_client, search_query)
    )

    gpt_query = USER_PROMPT.format(duckduckgo_results, google_results, query)

    gpt_client = OpenAIClient(openai_api_key, openai_tunnel_url, SYSTEM_PROMPT)
    response = gpt_client.chat_completion(query, model)
    print(response)

if __name__ == "__main__":
    asyncio.run(main())
