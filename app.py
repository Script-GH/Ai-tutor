import os
import logging
from datetime import datetime, timedelta
from functools import wraps
from logging.handlers import RotatingFileHandler
from urllib.parse import quote_plus

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_socketio import SocketIO
from pymongo import MongoClient
from gridfs import GridFS
from celery import Celery
from bson import ObjectId
import bcrypt

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configure CORS to accept requests from any frontend origin during development
CORS(app, resources={
    r"/api/*": {
        "origins": "*",  # In production, replace with your specific frontend URL
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "expose_headers": ["Authorization"],
        "supports_credentials": True
    }
})

app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(seconds=int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 3600)))
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))

# Configure logging
logging.basicConfig(
    filename=os.getenv('LOG_FILE', 'app.log'),
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize extensions
jwt = JWTManager(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=[os.getenv('RATE_LIMIT_DEFAULT', "100/hour")]
)

# MongoDB connection with proper escaping
username = "Script_DB"
password = "Adarsh@2006"
cluster_url = "cluster0.vriyoyl.mongodb.net"
username_escaped = quote_plus(username)
password_escaped = quote_plus(password)
mongodb_uri = f"mongodb+srv://{username_escaped}:{password_escaped}@{cluster_url}/?retryWrites=true&w=majority"

mongo_client = MongoClient(mongodb_uri)
db = mongo_client[os.getenv('DB_NAME')]
fs = GridFS(db)

# Celery configuration
celery = Celery(
    'tasks',
    broker=os.getenv('REDIS_URL'),
    backend=os.getenv('REDIS_URL')
)

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

# Authentication routes
@app.route('/api/auth/register', methods=['POST'])
@limiter.limit(os.getenv('RATE_LIMIT_AUTH', "3/minute"))
def register():
    """
    User registration endpoint
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            email:
              type: string
            password:
              type: string
    responses:
      201:
        description: User created successfully
      400:
        description: Invalid input
    """
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400

        if db.users.find_one({'email': email}):
            return jsonify({'error': 'Email already exists'}), 400

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        user = {
            'email': email,
            'password': hashed_password,
            'created_at': datetime.utcnow()
        }
        db.users.insert_one(user)

        return jsonify({'message': 'User created successfully'}), 201

    except Exception as e:
        logger.error(f"Registration error: {e}")
        return jsonify({'error': 'Registration failed'}), 500

@app.route('/api/auth/login', methods=['POST'])
@limiter.limit(os.getenv('RATE_LIMIT_AUTH', "3/minute"))
def login():
    """
    User login endpoint
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            email:
              type: string
            password:
              type: string
    responses:
      200:
        description: Login successful
      401:
        description: Invalid credentials
    """
    try:
        data = request.get_json()
        user = db.users.find_one({'email': data.get('email')})

        if user and bcrypt.checkpw(data.get('password').encode('utf-8'), user['password']):
            access_token = create_access_token(identity=str(user['_id']))
            return jsonify({
                'status': 'success',
                'access_token': access_token,
                'user': {
                    'email': user['email'],
                    'id': str(user['_id'])
                }
            }), 200

        return jsonify({
            'status': 'error',
            'message': 'Invalid email or password'
        }), 401

    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({
            'status': 'error',
            'message': 'An error occurred during login'
        }), 500

# File upload routes
@app.route('/api/upload/syllabus', methods=['POST'])
@jwt_required()
def upload_syllabus():
    """
    Upload syllabus file endpoint
    ---
    parameters:
      - name: file
        in: formData
        type: file
        required: true
    responses:
      200:
        description: File uploaded successfully
      400:
        description: Invalid file
    """
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        if not file.filename:
            return jsonify({'error': 'No file selected'}), 400

        # Store file in GridFS
        file_id = fs.put(file, filename=file.filename)
        
        # Store file metadata in MongoDB
        db.syllabi.insert_one({
            'file_id': file_id,
            'filename': file.filename,
            'uploaded_by': get_jwt_identity(),
            'uploaded_at': datetime.utcnow()
        })

        return jsonify({'message': 'File uploaded successfully', 'file_id': str(file_id)}), 200

    except Exception as e:
        logger.error(f"File upload error: {e}")
        return jsonify({'error': 'File upload failed'}), 500

# Test generation endpoint
@app.route('/api/generate/test', methods=['POST'])
@jwt_required()
def generate_test():
    """
    Generate test from syllabus
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            syllabus_id:
              type: string
            test_type:
              type: string
            difficulty:
              type: string
    responses:
      202:
        description: Test generation started
    """
    try:
        data = request.get_json()
        task = celery.send_task('tasks.generate_test', args=[data])
        return jsonify({'task_id': task.id, 'message': 'Test generation started'}), 202

    except Exception as e:
        logger.error(f"Test generation error: {e}")
        return jsonify({'error': 'Test generation failed'}), 500

# Analytics endpoints
@app.route('/api/analytics/usage', methods=['GET'])
@jwt_required()
def get_usage_analytics():
    """
    Get usage analytics
    ---
    responses:
      200:
        description: Analytics data
    """
    try:
        user_id = get_jwt_identity()
        analytics = db.analytics.find({'user_id': ObjectId(user_id)})
        return jsonify({'analytics': list(analytics)}), 200

    except Exception as e:
        logger.error(f"Analytics error: {e}")
        return jsonify({'error': 'Failed to retrieve analytics'}), 500

# Search functionality
@app.route('/api/search', methods=['GET'])
@jwt_required()
def search():
    """
    Search endpoint
    ---
    parameters:
      - name: q
        in: query
        type: string
        required: true
      - name: page
        in: query
        type: integer
        default: 1
      - name: per_page
        in: query
        type: integer
        default: 10
    responses:
      200:
        description: Search results
    """
    try:
        query = request.args.get('q', '')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))

        # Implement pagination
        skip = (page - 1) * per_page
        
        # Search in syllabi collection
        results = db.syllabi.find(
            {'$text': {'$search': query}},
            {'score': {'$meta': 'textScore'}}
        ).sort([('score', {'$meta': 'textScore'})]).skip(skip).limit(per_page)

        return jsonify({
            'results': list(results),
            'page': page,
            'per_page': per_page
        }), 200

    except Exception as e:
        logger.error(f"Search error: {e}")
        return jsonify({'error': 'Search failed'}), 500

# WebSocket for real-time notifications
@socketio.on('connect')
@jwt_required()
def handle_connect():
    user_id = get_jwt_identity()
    logger.info(f"User {user_id} connected to WebSocket")

@socketio.on('disconnect')
def handle_disconnect():
    logger.info("Client disconnected from WebSocket")

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    ---
    responses:
      200:
        description: Service is healthy
    """
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat()
    }), 200

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    socketio.run(app, debug=True, host='0.0.0.0', port=port)