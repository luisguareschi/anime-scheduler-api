from flask import Flask, request, jsonify

from scrape_anime_schedule import scrape_anime_schedule

app = Flask(__name__)


# disable cors
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Welcome to the anime schedule API"}), 200


@app.route('/schedule', methods=['GET'])
def get_anime_schedule():
    # Get the date from the query parameters
    year = request.args.get('year')
    week = request.args.get('week')
    if not week:
        return jsonify({"error": "week parameter is required"}), 400
    if not year:
        return jsonify({"error": "year parameter is required"}), 400

    # Scrape the data
    try:
        schedule = scrape_anime_schedule(year, week)
        return jsonify(schedule), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
