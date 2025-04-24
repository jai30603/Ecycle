import feedparser
import requests
from flask import current_app

def get_ewaste_news(limit=5):
    """
    Fetch the latest e-waste news from Google News RSS feed
    
    Args:
        limit (int): Maximum number of news items to return
        
    Returns:
        list: List of news items with titles and links
    """
    try:
        url = "https://news.google.com/rss/search?q=e+waste+latest+news"
        feed = feedparser.parse(url)
        
        news_list = []
        for entry in feed.entries[:limit]:
            news_list.append({
                "title": entry.title,
                "link": entry.link,
                "published": entry.published if hasattr(entry, 'published') else None,
                "summary": entry.summary if hasattr(entry, 'summary') else None
            })
        
        return news_list
    except Exception as e:
        current_app.logger.error(f"Error fetching e-waste news: {str(e)}")
        return []

def calculate_carbon_footprint(ewaste_type, quantity=1):
    """
    Calculate the carbon footprint saved by recycling e-waste
    
    Args:
        ewaste_type (str): Type of e-waste
        quantity (int): Number of devices
        
    Returns:
        float: Estimated carbon footprint in kg CO2
    """
    # Comprehensive carbon savings estimates in kg CO2 equivalent per device
    carbon_savings = {
        # Computing Devices
        'Laptop': 140.0,
        'Desktop-PC': 200.0,
        'Server': 250.0,
        'Tablet': 80.0,
        'Calculator': 8.0,
        'Digital-Oscilloscope': 90.0,
        
        # Computer Peripherals
        'Computer-Keyboard': 8.0,
        'Computer-Mouse': 5.0,
        'HDD': 15.0,
        'SSD': 12.0,
        'PCB': 20.0,
        'Network-Switch': 25.0,
        'Router': 30.0,
        'USB-Flash-Drive': 6.0,
        
        # Phones & Communication
        'Smartphone': 60.0,
        'Bar-Phone': 30.0,
        'Telephone-Set': 25.0,
        'Smart-Watch': 20.0,
        'TV-Remote-Control': 5.0,
        
        # Displays & Visual Equipment
        'Flat-Panel-Monitor': 90.0,
        'CRT-Monitor': 150.0,
        'Flat-Panel-TV': 120.0,
        'CRT-TV': 180.0,
        'Projector': 70.0,
        
        # Major Appliances
        'Air-Conditioner': 300.0,
        'Washing-Machine': 240.0,
        'Refrigerator': 350.0,
        'Freezer': 300.0,
        'Microwave': 100.0,
        'Dishwasher': 150.0,
        'Oven': 120.0,
        'Stove': 100.0,
        'Range-Hood': 70.0,
        'Tumble-Dryer': 180.0,
        'Boiler': 200.0,
        
        # Small Appliances & Kitchen Equipment
        'Coffee-Machine': 50.0,
        'Vacuum-Cleaner': 80.0,
        'Toaster': 30.0,
        'Cooled-Dispenser': 90.0,
        'Non-Cooled-Dispenser': 40.0,
        'Hair-Dryer': 20.0,
        'Clothes-Iron': 25.0,
        
        # Audio & Visual Equipment
        'Speaker': 25.0,
        'Headphone': 15.0,
        'Camera': 40.0,
        'Music-Player': 30.0,
        'Electronic-Keyboard': 60.0,
        'Electric-Guitar': 45.0,
        'PlayStation-5': 80.0,
        'Xbox-Series-X': 80.0,
        
        # Medical Devices
        'Blood-Pressure-Monitor': 30.0,
        'Glucose-Meter': 25.0,
        'Pulse-Oximeter': 20.0,
        'Electrocardiograph-Machine': 100.0,
        'Patient-Monitoring-System': 120.0,
        
        # Lighting & Electrical
        'Battery': 10.0,
        'LED-Bulb': 5.0,
        'Compact-Fluorescent-Lamps': 8.0,
        'Straight-Tube-Fluorescent-Lamp': 10.0,
        'Table-Lamp': 15.0,
        'Street-Lamp': 60.0,
        'Ceiling-Fan': 40.0,
        'Floor-Fan': 35.0,
        'Exhaust-Fan': 30.0,
        'Neon-Sign': 25.0,
        'Christmas-Lights': 15.0,
        'Flashlight': 8.0,
        'Power-Adapter': 7.0,
        'Smoke-Detector': 12.0,
        
        # Specialty Electronics
        'Drone': 50.0,
        'Electric-Bicycle': 120.0,
        'Soldering-Iron': 15.0,
        'Photovoltaic-Panel': 100.0,
        'Cooling-Display': 130.0,
        'Rotary-Mower': 70.0,
        
        # Legacy compatibility and fallbacks
        'Mobile': 60.0,
        'Desktop': 200.0,
        'Monitor': 90.0,
        'Other': 40.0
    }
    
    # Return carbon savings or default to 40kg if type not in dictionary
    return carbon_savings.get(ewaste_type, 40.0) * quantity
