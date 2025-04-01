from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
from lbsolver import solve_puzzle, DEFAULT_PUZZLE
import os

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)  # Enable CORS for all routes

@app.after_request
def add_security_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

@app.route('/')
def index():
    return render_template('index.html', default_puzzle=DEFAULT_PUZZLE)

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

@app.route('/solve', methods=['POST'])
def solve():
    puzzle = request.json.get('puzzle', DEFAULT_PUZZLE)
    try:
        solutions = solve_puzzle(puzzle)
        return jsonify({
            'success': True,
            'solutions': solutions
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

if __name__ == '__main__':
    # Ensure the static and templates directories exist
    os.makedirs('static', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    
    # Get port from environment variable or use 8080
    port = int(os.environ.get('PORT', 8080))
    
    # Run the app
    app.run(host='0.0.0.0', port=port, debug=False) 