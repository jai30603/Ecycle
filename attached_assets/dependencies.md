# Project Dependencies

The Ecycle - Smart E-waste Pickup Service requires the following dependencies:

## Python Packages
- Flask==2.3.3
- Flask-Login==0.6.2
- Flask-SQLAlchemy==3.1.1
- Flask-WTF==1.2.1
- Werkzeug==2.3.7
- SQLAlchemy==2.0.23
- gunicorn==23.0.0
- psycopg2-binary==2.9.9
- requests==2.31.0
- email-validator==2.1.0
- feedparser==6.0.10
- inference-sdk==0.3.7
- pillow==10.1.0
- python-dotenv==1.0.0

## External Requirements
- PostgreSQL database
- Roboflow API for e-waste image classification

## Environment Variables
- DATABASE_URL: PostgreSQL database connection string
- ROBOFLOW_API_KEY: API key for accessing the Roboflow image classification service

## Frontend Dependencies
- Bootstrap 5.3.0
- Font Awesome 5
- Chart.js (for admin analytics)
- Chatbase integration for user assistance chatbot