from typing_extensions import TypedDict, Annotated
from langchain_groq import ChatGroq
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langchain_core.messages import BaseMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
import os
from dotenv import load_dotenv
from backend.movie.system_prompt import MOVIE_RATING_SYSTEM_PROMPT

load_dotenv()
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")

class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# Using a more capable model for better movie rating information
model = ChatGroq(model="meta-llama/llama-4-scout-17b-16e-instruct")

def create_langgraph_agent():
    @tool
    def movie_serper_search(query: str):
        """Use Serper to search for real-time movie information with accurate ratings (out of 10) and reviews ONLY from ticket booking platforms like BookMyShow, Paytm, PVR, INOX, etc. DO NOT use data from general review sites like Times of India, 123 Telugu, etc."""
        import requests
        import json

        # Add keywords to focus on ticket booking platforms
        if "bookmyshow" in query.lower() and "site:" not in query.lower():
            query = f"{query} site:bookmyshow.com"
        elif "paytm" in query.lower() and "site:" not in query.lower():
            query = f"{query} site:paytm.com"
        elif "pvr" in query.lower() and "site:" not in query.lower():
            query = f"{query} site:pvrcinemas.com"
        elif "inox" in query.lower() and "site:" not in query.lower():
            query = f"{query} site:inoxmovies.com"
        elif "cinepolis" in query.lower() and "site:" not in query.lower():
            query = f"{query} site:cinepolisindia.com"
        else:
            # If no specific platform is mentioned, add ticket booking keywords
            query = f"{query} movie tickets booking showtimes"

        print(f"Searching with query: {query}")

        url = "https://google.serper.dev/search"

        payload = json.dumps({
            "q": query,
            "num": 15  # Increase number of results for better chances of finding relevant information
        })

        headers = {
            'X-API-KEY': os.getenv("SERPER_API_KEY"),
            'Content-Type': 'application/json'
        }

        try:
            response = requests.request("POST", url, headers=headers, data=payload)
            result = response.json()
            return result
        except Exception as e:
            return {"error": str(e)}

    # Create a more robust version of the search tool with retry logic
    @tool
    def multi_search(query: str):
        """Use multiple search engines to find accurate movie information with ratings (out of 10) ONLY from ticket booking platforms like BookMyShow, Paytm, PVR, INOX, etc. DO NOT use data from general review sites like Times of India, 123 Telugu, etc. This tool combines results from different sources for better accuracy."""
        import requests
        import json
        import time

        # Add keywords to focus on ticket booking platforms
        if "bookmyshow" in query.lower() and "site:" not in query.lower():
            query = f"{query} site:bookmyshow.com"
        elif "paytm" in query.lower() and "site:" not in query.lower():
            query = f"{query} site:paytm.com"
        elif "pvr" in query.lower() and "site:" not in query.lower():
            query = f"{query} site:pvrcinemas.com"
        elif "inox" in query.lower() and "site:" not in query.lower():
            query = f"{query} site:inoxmovies.com"
        elif "cinepolis" in query.lower() and "site:" not in query.lower():
            query = f"{query} site:cinepolisindia.com"
        else:
            # If no specific platform is mentioned, add ticket booking keywords and exclude non-ticket booking platforms
            query = f"{query} movie tickets booking showtimes"
            query = f"{query} -site:timesofindia.com -site:123telugu.com -site:ndtv.com -site:imdb.com -site:wikipedia.org"

        print(f"Multi-searching with query: {query}")

        max_retries = 3
        retry_delay = 2  # seconds
        results = {}

        # Try Serper first
        for attempt in range(max_retries):
            try:
                url = "https://google.serper.dev/search"

                payload = json.dumps({
                    "q": query,
                    "num": 15  # Increase number of results for better chances of finding relevant information
                })

                headers = {
                    'X-API-KEY': os.getenv("SERPER_API_KEY"),
                    'Content-Type': 'application/json'
                }

                response = requests.request("POST", url, headers=headers, data=payload)
                serper_result = response.json()

                # Check if the result contains meaningful data
                if serper_result and 'organic' in serper_result and len(serper_result['organic']) > 0:
                    print(f"Serper search successful on attempt {attempt + 1}")
                    results["serper"] = serper_result
                    break
                else:
                    print(f"Serper search returned empty results on attempt {attempt + 1}, retrying...")
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                    else:
                        results["serper"] = {"error": "No meaningful results found after multiple attempts"}
            except Exception as e:
                print(f"Serper search error on attempt {attempt + 1}: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    results["serper"] = {"error": f"Failed after {max_retries} attempts: {str(e)}"}

        return results

    # Function to filter search results to only include ticket booking platforms
    def filter_ticket_booking_results(search_results):
        """Filter search results to only include ticket booking platforms."""
        if not isinstance(search_results, dict) or 'organic' not in search_results:
            return search_results

        # List of ticket booking domains
        ticket_booking_domains = [
            'bookmyshow.com', 'paytm.com', 'pvrcinemas.com', 'inoxmovies.com', 'cinepolisindia.com',
            'bookmyshow', 'paytm', 'pvr', 'inox', 'cinepolis',
            'ticketnew.com', 'justickets.in', 'moviemax.in', 'easymovies.in', 'ticketplease.com',
            'movietickets.com', 'fandango.com', 'marcustheatres.com', 'amc', 'regal', 'cinemark',
            'ticket', 'booking', 'showtime', 'show time', 'movie ticket'
        ]

        # List of domains to exclude
        excluded_domains = [
            'timesofindia.com', '123telugu.com', 'ndtv.com', 'hindustantimes.com', 'indiatoday.in',
            'thehindu.com', 'indianexpress.com', 'imdb.com', 'rottentomatoes.com', 'filmfare.com',
            'bollywoodhungama.com', 'koimoi.com', 'pinkvilla.com', 'filmibeat.com', 'bollywoodlife.com',
            'zeenews.com', 'news18.com', 'republic.in', 'abplive.com', 'aajtak.in'
        ]

        # Filter organic results
        filtered_organic = []
        for result in search_results['organic']:
            link = result.get('link', '').lower()
            title = result.get('title', '').lower()
            snippet = result.get('snippet', '').lower()

            # Check if result is from a ticket booking platform
            is_ticket_booking = any(domain in link or domain in title or domain in snippet for domain in ticket_booking_domains)

            # Check if result is from an excluded domain
            is_excluded = any(domain in link or domain in title or domain in snippet for domain in excluded_domains)

            if is_ticket_booking and not is_excluded:
                filtered_organic.append(result)
                print(f"Including result: {title[:50]}... from {link}")
            else:
                print(f"Excluding result: {title[:50]}... from {link}")

        # Get the original count before updating
        original_count = len(search_results.get('organic', []))

        # If we have too few results after filtering, be less strict
        if len(filtered_organic) < 2 and original_count > 0:
            print("Too few results after filtering, being less strict...")
            # Try again with a less strict approach - include results that mention movies and ratings
            filtered_organic = []
            for result in search_results['organic']:
                link = result.get('link', '').lower()
                title = result.get('title', '').lower()
                snippet = result.get('snippet', '').lower()

                # Check if result is from an excluded domain
                is_excluded = any(domain in link for domain in excluded_domains)

                # Check if it's related to movies and ratings
                has_movie_keywords = ('movie' in title or 'movie' in snippet or 'rating' in title or 'rating' in snippet or 'review' in title or 'review' in snippet)

                if not is_excluded and has_movie_keywords:
                    filtered_organic.append(result)
                    print(f"Including result with less strict filtering: {title[:50]}... from {link}")

        # Update the search results with filtered organic results
        search_results['organic'] = filtered_organic
        print(f"Filtered results: {len(filtered_organic)} out of {original_count}")

        return search_results

    # Wrap the search tools to filter results
    @tool
    def filtered_movie_search(query: str):
        """Search for movie information with ratings (out of 10) from ticket booking platforms only."""
        results = movie_serper_search(query)
        return filter_ticket_booking_results(results)

    @tool
    def filtered_multi_search(query: str):
        """Search for movie information with ratings (out of 10) from multiple ticket booking platforms only."""
        results = multi_search(query)

        # Filter serper results if they exist
        if 'serper' in results:
            results['serper'] = filter_ticket_booking_results(results['serper'])

        return results

    # Create a tool node with all search tools
    tool_node = ToolNode([filtered_movie_search, filtered_multi_search])
    model_with_tools = model.bind_tools([filtered_movie_search, filtered_multi_search])

    def call_model(state: State):
        return {
            "messages": [
                model_with_tools.invoke([
                    SystemMessage(content=MOVIE_RATING_SYSTEM_PROMPT),
                    *state["messages"]
                ])
            ]
        }

    def should_continue(state: State):
        last = state["messages"][-1]
        return "tools" if last.tool_calls else END

    graph = StateGraph(State)
    graph.add_node("agent", call_model)
    graph.add_node("tools", tool_node)
    graph.add_edge("tools", "agent")
    graph.add_edge(START, "agent")
    graph.add_conditional_edges("agent", should_continue)

    return graph.compile()
