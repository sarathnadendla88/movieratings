import streamlit as st
import requests
import json
import time
from datetime import datetime
import config

# Set page configuration
st.set_page_config(
    page_title=config.APP_TITLE,
    page_icon=config.APP_ICON,
    layout=config.DEFAULT_LAYOUT
)

# Function to fetch movie ratings from API with caching
@st.cache_data(ttl=config.CACHE_TTL, show_spinner=False)
def fetch_movie_ratings(movie_name):
    """Fetch movie ratings from the API with proper error handling and caching.

    Args:
        movie_name: Name of the movie to search for

    Returns:
        Movie ratings data or None if an error occurs
    """
    try:
        # API endpoint
        url = f"{config.API_BASE_URL}/movie-ratings"

        # Prepare request payload
        payload = {
            "movie_name": movie_name
        }

        # Log the request
        st.session_state.setdefault('api_logs', []).append({
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'request': payload,
            'endpoint': url
        })

        # Show a spinner while waiting for the API response
        with st.spinner(f"Searching for ratings for '{movie_name}'..."):
            # Set a timeout for the request to prevent hanging
            response = requests.post(url, json=payload, timeout=config.API_TIMEOUT)

            # Add response to logs
            st.session_state['api_logs'][-1]['status_code'] = response.status_code

            if response.status_code == 200:
                data = response.json()

                # Add successful response to logs
                st.session_state['api_logs'][-1]['response_size'] = len(str(data))

                # Check if the expected keys exist
                if "status" in data and "data" in data:
                    return data["data"]
                else:
                    # Log the error
                    st.session_state['api_logs'][-1]['error'] = "Invalid response structure"

                    # Show error in UI with collapsible details
                    st.error("😕 We couldn't process the movie data correctly.")
                    with st.expander("Technical Details"):
                        st.write("API response does not contain the expected data structure.")
                        st.write("Expected keys: status, data")
                        st.write("Actual response structure:")
                        st.json(data)
                    return None
            else:
                # Log the error
                st.session_state['api_logs'][-1]['error'] = f"HTTP {response.status_code}: {response.text}"

                # Show user-friendly error with technical details in expander
                st.error(f"😕 We're having trouble finding ratings for this movie right now. Please try again later.")
                with st.expander("Technical Details"):
                    st.write(f"Error: API returned status code {response.status_code}")
                    st.code(response.text)
                return None

    except requests.exceptions.Timeout:
        st.error("⏱️ The request timed out. Our rating service is taking longer than expected.")
        st.info("Please try again with a different movie name.")
        return None

    except requests.exceptions.ConnectionError:
        st.error("🔌 Connection error. We couldn't reach our rating service.")
        st.info("Please check your internet connection and try again.")
        return None

    except Exception as e:
        # Log the exception
        import traceback
        error_details = traceback.format_exc()
        st.session_state.setdefault('api_logs', []).append({
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'request': payload if 'payload' in locals() else "No payload",
            'error': str(e),
            'traceback': error_details
        })

        # Show user-friendly error with technical details in expander
        st.error("😕 Something went wrong while fetching movie ratings.")
        with st.expander("Technical Details"):
            st.write(f"Error connecting to API: {str(e)}")
            st.write(f"Exception type: {type(e).__name__}")
            st.code(error_details)
        return None

# Function to display movie ratings
def display_movie_ratings(ratings_data):
    """Display movie ratings in a visually appealing format.

    Args:
        ratings_data: List of movie ratings from different platforms
    """
    if not ratings_data or len(ratings_data) == 0:
        st.warning("No ratings found for this movie.")
        return

    # Add custom CSS for rating cards
    st.markdown("""
    <style>
    .rating-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        border-left: 4px solid #E50914;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .platform-name {
        font-size: 1.2em;
        font-weight: bold;
        margin-bottom: 5px;
        color: #221F1F;
    }
    .movie-title {
        font-size: 1.1em;
        margin-bottom: 10px;
    }
    .rating-value {
        font-size: 1.5em;
        font-weight: bold;
        color: #E50914;
    }
    .movie-type {
        font-style: italic;
        color: #555;
        margin-bottom: 10px;
    }
    .review-percentage {
        margin-top: 10px;
    }
    .positive {
        color: #4CAF50;
        font-weight: bold;
    }
    .negative {
        color: #F44336;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

    # Display each platform's rating in a card
    for rating in ratings_data:
        platform = rating.get("platform", "Unknown Platform")
        movie_title = rating.get("movie_title", "Unknown Title")
        movie_rating = rating.get("movie_rating", 0)
        movie_type = rating.get("type_of_movie", "")
        positive_percentage = rating.get("positive_review_percentage", 0)
        negative_percentage = rating.get("negative_review_percentage", 0)

        # Create star rating display
        stars = "★" * int(movie_rating) + "☆" * (5 - int(movie_rating))
        if movie_rating % 1 >= 0.5:
            stars = stars.replace("☆", "★", 1)

        # Create HTML for the card
        html = f"""
        <div class="rating-card">
            <div class="platform-name">{platform}</div>
            <div class="movie-title">{movie_title}</div>
            <div class="rating-value">{movie_rating}/5.0 {stars}</div>
            <div class="movie-type">{movie_type}</div>
            <div class="review-percentage">
                <span class="positive">👍 {positive_percentage}% Positive</span> | 
                <span class="negative">👎 {negative_percentage}% Negative</span>
            </div>
        </div>
        """
        st.markdown(html, unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    """Initialize session state variables."""
    if 'search_history' not in st.session_state:
        st.session_state.search_history = []
    if 'current_movie' not in st.session_state:
        st.session_state.current_movie = None
    if 'loading' not in st.session_state:
        st.session_state.loading = False

# Main app
def main():
    """Main application function."""
    # Initialize session state
    init_session_state()

    # App header
    st.title(f"{config.APP_ICON} Movie Rating Aggregator")
    st.markdown("Search for a movie to see ratings and reviews from multiple platforms.")

    # Search form
    with st.form(key="search_form"):
        movie_name = st.text_input("Enter movie name:", placeholder="e.g., Dune: Part Two")
        col1, col2 = st.columns([1, 5])
        with col1:
            search_button = st.form_submit_button("Search")
        with col2:
            st.markdown("")  # Empty space for alignment

    # Process search when button is clicked
    if search_button and movie_name:
        st.session_state.loading = True
        st.session_state.current_movie = movie_name
        
        # Add to search history if not already present
        if movie_name not in st.session_state.search_history:
            st.session_state.search_history.append(movie_name)
            # Keep only the last 5 searches
            if len(st.session_state.search_history) > 5:
                st.session_state.search_history.pop(0)

    # Display search history
    if st.session_state.search_history:
        st.sidebar.header("Recent Searches")
        for movie in st.session_state.search_history:
            if st.sidebar.button(movie, key=f"history_{movie}"):
                st.session_state.current_movie = movie
                st.session_state.loading = True
                st.experimental_rerun()

    # If loading or we have a current movie, fetch and display data
    if st.session_state.loading or st.session_state.current_movie:
        # Get movie name from session state if available
        if st.session_state.current_movie:
            movie_name = st.session_state.current_movie

        # Show a progress bar while loading
        if st.session_state.loading:
            progress_bar = st.progress(0)
            for i in range(100):
                # Update progress bar
                progress_bar.progress(i + 1)
                # Add a small delay for visual effect
                time.sleep(0.01)
            st.session_state.loading = False

        # Fetch data from API with error handling
        try:
            with st.spinner(f"Fetching ratings for '{movie_name}'..."):
                ratings_data = fetch_movie_ratings(movie_name)

            # Display the results
            if ratings_data:
                st.subheader(f"Ratings for '{movie_name}'")
                display_movie_ratings(ratings_data)
            else:
                st.error(f"No ratings found for '{movie_name}'. Please try another movie.")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

    # Add a footer
    st.markdown("---")
    st.markdown("### About")
    st.markdown(
        "This app aggregates movie ratings and reviews from multiple platforms "
        "to help you make informed decisions about what to watch."
    )
    st.markdown("© 2023 Movie Rating Aggregator | Powered by AI")

# Run the app
if __name__ == "__main__":
    main()
