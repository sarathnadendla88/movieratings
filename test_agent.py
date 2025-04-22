from backend.movie.planner import create_langgraph_agent
from langchain_core.messages import HumanMessage
import json

def test_agent():
    """Test the agent directly to see if it's returning valid JSON"""
    print("Creating agent...")
    agent_executor = create_langgraph_agent()
    
    # Test with a popular movie
    movie_name = "Dune: Part Two"
    print(f"Testing agent with movie: {movie_name}")
    
    # Create a user prompt with the movie name
    user_prompt = HumanMessage(content=movie_name)
    
    try:
        # Invoke the agent
        print("Invoking agent...")
        result = agent_executor.invoke({"messages": [user_prompt]})
        final_message = result["messages"][-1]
        
        # Print the response
        content = final_message.content
        print(f"Response length: {len(content)}")
        print(f"Response content: {content[:1000]}...")
        
        # Try to parse the JSON
        try:
            print("\nAttempting to parse JSON directly...")
            ratings = json.loads(content)
            print(f"Successfully parsed JSON, found {len(ratings)} platform(s)")
            
            # Print each platform's rating
            for rating in ratings:
                print(f"\nPlatform: {rating.get('platform')}")
                print(f"Movie Title: {rating.get('movie_title')}")
                print(f"Rating: {rating.get('movie_rating')}/10.0")
                print(f"Type: {rating.get('type_of_movie')}")
                print(f"Positive Reviews: {rating.get('positive_review_percentage')}%")
                print(f"Negative Reviews: {rating.get('negative_review_percentage')}%")
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {str(e)}")
            
            # Try to find a JSON array in the content
            try:
                # Find the first '[' and the last ']'
                start_idx = content.find('[')
                end_idx = content.rfind(']')
                
                if start_idx != -1 and end_idx != -1 and start_idx < end_idx:
                    json_str = content[start_idx:end_idx+1]
                    print(f"Found potential JSON array: {json_str[:500]}...")
                    ratings = json.loads(json_str)
                    print(f"Successfully parsed JSON array, found {len(ratings)} platform(s)")
                    
                    # Print each platform's rating
                    for rating in ratings:
                        print(f"\nPlatform: {rating.get('platform')}")
                        print(f"Movie Title: {rating.get('movie_title')}")
                        print(f"Rating: {rating.get('movie_rating')}/10.0")
                        print(f"Type: {rating.get('type_of_movie')}")
                        print(f"Positive Reviews: {rating.get('positive_review_percentage')}%")
                        print(f"Negative Reviews: {rating.get('negative_review_percentage')}%")
                else:
                    print("Could not find JSON array in content")
            except (json.JSONDecodeError, ValueError) as e2:
                print(f"Error parsing JSON array: {str(e2)}")
    except Exception as e:
        print(f"Error invoking agent: {str(e)}")

if __name__ == "__main__":
    test_agent()
