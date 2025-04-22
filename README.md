# Movie Rating Aggregator

A powerful movie rating and review aggregator that collects information from multiple platforms.

## Features

- Search for movies by name
- View ratings from multiple platforms:
  - BookMyShow
  - Paytm
  - PVR Cinemas
  - INOX Movies
  - Cinepolis
- See detailed information for each platform:
  - Movie title
  - Rating (out of 5)
  - Movie genre/type
  - Positive review percentage
  - Negative review percentage

## Installation

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set up environment variables (create a `.env` file):
   ```
   SERPER_API_KEY=your_serper_api_key
   ```

## Usage

1. Start the backend server:
   ```
   uvicorn backend.main:app --reload
   ```

2. Start the Streamlit frontend:
   ```
   streamlit run app.py
   ```

3. Open your browser and navigate to the URL shown in the terminal (typically http://localhost:8501)

4. Enter a movie name in the search box and click "Search"

## API Endpoints

- `POST /movie-ratings`: Get ratings for a movie from multiple platforms
  - Request body: `{"movie_name": "Movie Name"}`
  - Response: JSON array of platform ratings

## Technologies Used

- FastAPI: Backend API framework
- Streamlit: Frontend web application
- Serper API: Web search for gathering movie data
- Python: Programming language

## License

MIT License
