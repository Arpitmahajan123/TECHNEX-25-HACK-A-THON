from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_restful import Api, Resource
import json
from datetime import datetime
import os

app = Flask(__name__, static_folder='static', static_url_path='/static')
api = Api(app)

# Ensure directories exist
os.makedirs('data', exist_ok=True)
os.makedirs('static/images', exist_ok=True)
os.makedirs('static/css', exist_ok=True)

# Load data from JSON files
def load_json_data(filename):
    try:
        with open(f'data/{filename}', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

# API Resources
class NewsAPI(Resource):
    def get(self):
        location = request.args.get('location', '')
        start_date = request.args.get('start_date', '')
        end_date = request.args.get('end_date', '')
        
        news_data = load_json_data('news.json')
        filtered_news = []
        
        for news in news_data:
            if location.lower() in news['location'].lower():
                if start_date and end_date:
                    news_date = datetime.strptime(news['date'], '%Y-%m-%d')
                    start = datetime.strptime(start_date, '%Y-%m-%d')
                    end = datetime.strptime(end_date, '%Y-%m-%d')
                    if start <= news_date <= end:
                        filtered_news.append(news)
                else:
                    filtered_news.append(news)
                    
        return jsonify(filtered_news)

class LeaderboardAPI(Resource):
    def get(self):
        leaderboard_data = load_json_data('leaderboard.json')
        return jsonify(sorted(leaderboard_data, key=lambda x: x['points'], reverse=True))

class GadgetsAPI(Resource):
    def get(self):
        gadgets_data = load_json_data('gadgets.json')
        return jsonify(gadgets_data)

class BadgesAPI(Resource):
    def get(self):
        badges_data = load_json_data('badges.json')
        return jsonify(badges_data)

# Register API resources
api.add_resource(NewsAPI, '/api/news')
api.add_resource(LeaderboardAPI, '/api/leaderboard')
api.add_resource(GadgetsAPI, '/api/gadgets')
api.add_resource(BadgesAPI, '/api/badges')

# Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/news')
def news():
    return render_template('news.html')

@app.route('/leaderboard')
def leaderboard():
    return render_template('leaderboard.html')

@app.route('/gadgets')
def gadgets():
    return render_template('gadgets.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
