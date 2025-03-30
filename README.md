# SCRIPTx Authentication System

This project consists of a Flask backend API and a frontend web application for user authentication.

## Project Structure

- Backend: Flask REST API with MongoDB and JWT authentication
- Frontend: HTML/CSS/JavaScript web application

## Backend Setup

1. Make sure you have Python 3.8+ installed
2. Install backend dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Configure environment variables in `.env` file
4. Start the Flask server:
   ```
   python app.py
   ```

The backend runs on port 5001 by default.

## Frontend Setup

1. Make sure you have Node.js installed
2. Install frontend dependencies:
   ```
   npm install
   ```
3. Start the frontend server:
   ```
   npm run dev
   ```

The frontend runs on port 3000 by default.

## API Endpoints

### Authentication

- `POST /api/auth/register` - Register a new user
  - Body: `{ "email": "user@example.com", "password": "password123" }`
  - Response: `{ "message": "User created successfully" }`

- `POST /api/auth/login` - Login a user
  - Body: `{ "email": "user@example.com", "password": "password123" }`
  - Response: `{ "status": "success", "access_token": "JWT_TOKEN", "user": { "email": "user@example.com", "id": "user_id" } }`

### Health Check

- `GET /api/health` - Check if the API is running
  - Response: `{ "status": "healthy", "timestamp": "ISO_TIMESTAMP" }`

## Testing the Application

1. Start both backend and frontend servers
2. Open your browser to `http://localhost:3000`
3. Use the register page to create a new account
4. Log in with your credentials
5. You will be redirected to the dashboard upon successful login 