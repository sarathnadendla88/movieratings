import requests
import json

def test_movie_ratings_endpoint():
    """Test the movie ratings endpoint"""
    url = "http://127.0.0.1:8000/movie-ratings"

    # Test with a popular movie
    payload = {
        "movie_name": "Dune: Part Two"
    }

    try:
        # Make the request
        print(f"Sending request to {url} with payload: {payload}")
        response = requests.post(url, json=payload)

        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()
            print("Response status:", data.get("status"))

            if data.get("status") == "success":
                print("Number of platforms:", len(data.get("data", [])))

                # Print each platform's rating
                for rating in data.get("data", []):
                    print(f"\nPlatform: {rating.get('platform')}")
                    print(f"Movie Title: {rating.get('movie_title')}")
                    print(f"Rating: {rating.get('movie_rating')}/10.0")
                    print(f"Type: {rating.get('type_of_movie')}")
                    print(f"Positive Reviews: {rating.get('positive_review_percentage')}%")
                    print(f"Negative Reviews: {rating.get('negative_review_percentage')}%")
            else:
                print("Error message:", data.get("message"))
                # Try to make a direct request to see the raw response
                try:
                    print("\nAttempting direct request to see raw response...")
                    direct_response = requests.post(url, json=payload)
                    print(f"Status code: {direct_response.status_code}")
                    print(f"Raw response: {direct_response.text[:500]}...")
                except Exception as direct_error:
                    print(f"Error making direct request: {str(direct_error)}")
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Exception: {str(e)}")

if __name__ == "__main__":
    test_movie_ratings_endpoint()
