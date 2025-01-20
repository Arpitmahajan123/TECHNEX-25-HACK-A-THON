import requests
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_women_news():
    # Get API key from environment variable
    api_key = os.getenv('NEWS_API_KEY')
    
    # Calculate date 30 days ago from today
    thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    # Base URL for News API
    base_url = "https://newsapi.org/v2/everything"
    
    # Parameters for the API request
    params = {
        'q': 'women',  # Search for women-related news
        'from': thirty_days_ago,
        'sortBy': 'publishedAt',
        'apiKey': api_key,
        'language': 'en'
    }
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        
        news_data = response.json()
        articles = news_data.get('articles', [])
        
        # Process each article to format the date
        for article in articles:
            if article.get('publishedAt'):
                # Convert ISO date to more readable format
                date = datetime.fromisoformat(article['publishedAt'].replace('Z', '+00:00'))
                article['publishedAt'] = date.strftime('%B %d, %Y %I:%M %p')
        
        return articles
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching news: {e}")
        return []

if __name__ == "__main__":
    news = get_women_news()
    for article in news:
        print(f"\nTitle: {article['title']}")
        print(f"Description: {article['description']}")
        print(f"Source: {article['source']['name']}")
        print(f"Published: {article['publishedAt']}")
        print(f"URL: {article['url']}")
        print("-" * 80)
