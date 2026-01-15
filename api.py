from flask import Flask, request, jsonify
from flask_cors import CORS
from Backend.auth import login_user, create_user
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# ==================== ROUTES ====================

@app.route('/api/login', methods=['POST'])
def api_login():
    """Handle login requests from the frontend."""
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'success': False, 'message': 'Username and password are required'}), 400
        
        result = login_user(username, password)
        
        if result['success']:
            return jsonify({
                'success': True, 
                'message': 'Login successful',
                'user': result['user']
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': result['message']
            }), 401
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/signup', methods=['POST'])
def api_signup():
    """Handle signup requests from the frontend."""
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        full_name = data.get('full_name')
        email = data.get('email')
        
        if not all([username, password, full_name, email]):
            return jsonify({'success': False, 'message': 'All fields are required'}), 400
        
        result = create_user(username, password, full_name, email)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': result['message']
            }), 201
        else:
            return jsonify({
                'success': False,
                'message': result['message']
            }), 400
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({'status': 'ok', 'message': 'API is running'}), 200


# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'message': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'message': 'Internal server error'}), 500


# ==================== MAIN ====================

if __name__ == '__main__':
    print("🚀 Starting Flask API on http://localhost:5000")
    print("📝 Make sure the Streamlit app is running on http://localhost:8501")
    app.run(debug=True, port=5000, host='0.0.0.0')
