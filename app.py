import os
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS

# Import the local package
# Assuming 'moviebox_api' is a folder in the same directory
try:
    from moviebox_api import MovieBox
except ImportError:
    # Fallback if the folder structure is slightly different
    sys.path.append(os.path.join(os.path.dirname(__file__), 'moviebox_api'))
    from moviebox_api.main import MovieBox 

app = Flask(__name__)
CORS(app) # Enable CORS for all routes

# Initialize the MovieBox engine
# Most versions of this API require an instance to maintain session/headers
mb = MovieBox()

@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "status": "online",
        "message": "MovieBox API Backend is running",
        "version": "1.0.0"
    })

@app.route("/search", methods=["GET"])
def search():
    query = request.args.get("q")
    if not query:
        return jsonify({"error": "Missing query parameter 'q'"}), 400

    try:
        # search_movies returns a list of results
        results = mb.search_movies(query)
        
        output = []
        for item in results:
            output.append({
                "id": item.get("id"),
                "title": item.get("title"),
                "poster": item.get("poster"),
                "type": item.get("type", "movie") # movie or series
            })
        
        if not output:
            return jsonify({"message": "No results found"}), 404
            
        return jsonify(output)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/stream", methods=["GET"])
def stream():
    movie_id = request.args.get("id")
    if not movie_id:
        return jsonify({"error": "Missing movie ID"}), 400

    try:
        # Fetching details and extracting the stream URL
        # The library typically returns a dictionary containing 'stream_url' or similar
        details = mb.get_movie_details(movie_id)
        
        if not details:
            return jsonify({"error": "Invalid ID or movie not found"}), 404

        # Extracting the actual video URL
        stream_url = details.get("stream_url") or details.get("video_url")
        
        if not stream_url:
            return jsonify({"error": "Streaming URL not available"}), 404

        return jsonify({
            "stream": stream_url
        })

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

if __name__ == "__main__":
    # Use port from environment variable for Render compatibility
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
