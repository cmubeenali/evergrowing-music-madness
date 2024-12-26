from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/callback', methods=['GET'])
def spotify_callback():
    # Extract authorization code or error from the query parameters
    error = request.args.get('error')
    code = request.args.get('code')
    
    if error:
        return jsonify({"status": "error", "message": error}), 400
    
    if code:
        # Handle the authorization code (e.g., exchange it for a token)
        return jsonify({"status": "success", "code": code}), 200
    
    return jsonify({"status": "error", "message": "Missing parameters"}), 400

if __name__ == '__main__':
    # Run Flask app on localhost at port 8888
    app.run(host='localhost', port=8888)
