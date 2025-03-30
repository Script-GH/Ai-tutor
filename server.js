const express = require('express');
const path = require('path');

const app = express();
const PORT = 3000;

// Serve static files
app.use(express.static(__dirname));

// Route for the home page
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'login.html'));
});

// Route for dashboard (placeholder)
app.get('/dashboard.html', (req, res) => {
  res.send(`
    <!DOCTYPE html>
    <html>
    <head>
      <title>Dashboard</title>
      <style>
        body {
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
          padding: 20px;
          background: #2D1B69;
          color: white;
        }
        .container {
          max-width: 800px;
          margin: 0 auto;
          padding: 20px;
          background: rgba(255, 255, 255, 0.1);
          border-radius: 10px;
        }
        h1 {
          color: #8B5CF6;
        }
        .user-info {
          background: rgba(255, 255, 255, 0.05);
          padding: 15px;
          border-radius: 8px;
          margin-top: 20px;
        }
        .logout-btn {
          background: #8B5CF6;
          color: white;
          border: none;
          padding: 10px 15px;
          border-radius: 5px;
          cursor: pointer;
          margin-top: 20px;
        }
      </style>
    </head>
    <body>
      <div class="container">
        <h1>Dashboard</h1>
        <p>Welcome to your dashboard! You are now logged in.</p>
        
        <div class="user-info" id="userInfo">
          Loading user information...
        </div>
        
        <button class="logout-btn" id="logoutBtn">Logout</button>
      </div>
      
      <script>
        // Get user info from localStorage
        document.addEventListener('DOMContentLoaded', () => {
          const userInfo = document.getElementById('userInfo');
          const logoutBtn = document.getElementById('logoutBtn');
          
          // Check if user is logged in
          const token = localStorage.getItem('token');
          const user = JSON.parse(localStorage.getItem('user') || '{}');
          
          if (!token) {
            window.location.href = '/login.html';
            return;
          }
          
          // Display user info
          userInfo.innerHTML = \`
            <h3>User Information</h3>
            <p><strong>Email:</strong> \${user.email || 'Not available'}</p>
            <p><strong>User ID:</strong> \${user.id || 'Not available'}</p>
            <p><strong>Token:</strong> \${token.substring(0, 20)}...</p>
          \`;
          
          // Logout functionality
          logoutBtn.addEventListener('click', () => {
            localStorage.removeItem('token');
            localStorage.removeItem('user');
            window.location.href = '/login.html';
          });
        });
      </script>
    </body>
    </html>
  `);
});

// Placeholder for registration page
app.get('/register.html', (req, res) => {
  res.send(`
    <!DOCTYPE html>
    <html>
    <head>
      <title>Register</title>
      <style>
        body {
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
          padding: 20px;
          background: #2D1B69;
          color: white;
          display: flex;
          justify-content: center;
          align-items: center;
          min-height: 100vh;
          margin: 0;
        }
        .container {
          max-width: 800px;
          margin: 0 auto;
          padding: 20px;
          background: rgba(255, 255, 255, 0.1);
          border-radius: 10px;
        }
        h1 {
          color: #8B5CF6;
        }
        .form-group {
          margin-bottom: 20px;
        }
        label {
          display: block;
          margin-bottom: 8px;
        }
        input {
          width: 100%;
          padding: 12px;
          border: none;
          background: rgba(255, 255, 255, 0.1);
          border-radius: 8px;
          color: white;
          font-size: 1em;
          box-sizing: border-box;
        }
        button {
          background: #8B5CF6;
          color: white;
          border: none;
          padding: 12px;
          width: 100%;
          border-radius: 8px;
          cursor: pointer;
          font-size: 1em;
          margin-top: 10px;
        }
        .alert {
          padding: 10px;
          border-radius: 8px;
          margin-bottom: 20px;
          display: none;
        }
        .alert-success {
          background: rgba(34, 197, 94, 0.2);
          color: #22c55e;
        }
        .alert-error {
          background: rgba(239, 68, 68, 0.2);
          color: #ef4444;
        }
        .back-link {
          display: block;
          margin-top: 20px;
          text-align: center;
          color: #8B5CF6;
          text-decoration: none;
        }
      </style>
    </head>
    <body>
      <div class="container">
        <h1>Create an Account</h1>
        <div class="alert alert-success" id="successAlert"></div>
        <div class="alert alert-error" id="errorAlert"></div>
        
        <form id="registerForm">
          <div class="form-group">
            <label for="email">Email</label>
            <input type="email" id="email" placeholder="your@email.com" required>
          </div>
          <div class="form-group">
            <label for="password">Password</label>
            <input type="password" id="password" placeholder="••••••••" required>
          </div>
          <div class="form-group">
            <label for="confirmPassword">Confirm Password</label>
            <input type="password" id="confirmPassword" placeholder="••••••••" required>
          </div>
          <button type="submit">Create Account</button>
        </form>
        
        <a href="/login.html" class="back-link">Already have an account? Sign in</a>
      </div>
      
      <script>
        document.getElementById('registerForm').addEventListener('submit', async (e) => {
          e.preventDefault();
          
          const email = document.getElementById('email').value;
          const password = document.getElementById('password').value;
          const confirmPassword = document.getElementById('confirmPassword').value;
          const successAlert = document.getElementById('successAlert');
          const errorAlert = document.getElementById('errorAlert');
          
          // Hide any existing alerts
          successAlert.style.display = 'none';
          errorAlert.style.display = 'none';
          
          // Validate passwords match
          if (password !== confirmPassword) {
            errorAlert.textContent = 'Passwords do not match';
            errorAlert.style.display = 'block';
            return;
          }
          
          try {
            const response = await fetch('http://localhost:5001/api/auth/register', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({ email, password })
            });
            
            const data = await response.json();
            
            if (response.ok) {
              // Show success message
              successAlert.textContent = 'Account created successfully! Redirecting to login...';
              successAlert.style.display = 'block';
              
              // Redirect after a short delay
              setTimeout(() => {
                window.location.href = '/login.html';
              }, 2000);
            } else {
              // Show error message
              errorAlert.textContent = data.message || 'Error creating account';
              errorAlert.style.display = 'block';
            }
          } catch (error) {
            // Show network error
            errorAlert.textContent = 'Network error. Please try again.';
            errorAlert.style.display = 'block';
          }
        });
      </script>
    </body>
    </html>
  `);
});

app.listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT}`);
}); 