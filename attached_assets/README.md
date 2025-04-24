# Ecycle - Smart E-Waste Pickup Service

A comprehensive e-waste management platform that streamlines electronic waste recycling through intelligent technologies and user engagement.

## Features

### User Features
- **User Registration & Authentication**: Secure login and registration system
- **E-waste Image Classification**: AI-powered identification of 77 different e-waste types
- **Pickup Scheduling**: Easy scheduling for e-waste collection
- **Eco Points System**: Earn points for recycling that can be redeemed for rewards
- **Recycling Information**: Detailed information about proper e-waste disposal
- **User Dashboard**: Monitor recycling history and environmental impact
- **Rewards Marketplace**: Redeem eco points for refurbished products and discount coupons

### Admin Features
- **Admin Dashboard**: Comprehensive overview of system activities
- **User Management**: View and manage user accounts and eco points
- **Pickup Management**: Track and update pickup statuses
- **E-waste Inventory**: Add and manage e-waste items
- **Rewards Management**: Create, edit, and manage reward items
- **Redemption Processing**: Process user reward redemptions

## Technologies Used

### Backend
- **Flask**: Web framework for building the application
- **SQLAlchemy**: ORM for database interactions
- **PostgreSQL**: Relational database for data storage
- **Roboflow API**: AI-powered image classification for e-waste identification
- **Gunicorn**: WSGI HTTP server for deployment

### Frontend
- **Bootstrap 5**: Responsive design framework
- **JavaScript**: Client-side interactivity
- **Chart.js**: Data visualization for analytics
- **Chatbase**: Integrated chatbot for user assistance

## Installation

1. Clone the repository
2. Install required packages listed in dependencies.md
3. Set up environment variables:
   - DATABASE_URL: PostgreSQL database connection string
   - ROBOFLOW_API_KEY: API key for accessing the e-waste classification model

## Running the Application

```bash
gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
```

## Database Schema

The application uses a PostgreSQL database with the following models:
- User: Stores user information and eco points
- Admin: Admin user accounts for system management
- Ewaste: E-waste item details and classification results
- Schedule: Pickup scheduling information
- Reward: Available rewards in the marketplace
- Redemption: Record of user reward redemptions

## E-waste Classification

The application uses Roboflow's API to classify e-waste images into 77 different categories, providing users with proper recycling information for each type.

## Environmental Impact

Users can track their environmental impact through:
- Eco points earned through recycling
- Carbon footprint reduction estimation
- Total materials diverted from landfills