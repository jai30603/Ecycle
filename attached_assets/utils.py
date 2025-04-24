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
    # Updated carbon savings estimates in kg CO2 equivalent per device
    carbon_savings = {
        # Computers & Accessories
        'Laptop': 140.0,
        'Desktop-PC': 200.0,
        'Tablet': 80.0,
        'Computer-Keyboard': 8.0,
        'Computer-Mouse': 5.0,
        
        # Phones & Wearables
        'Smartphone': 60.0,
        'Smart-Watch': 20.0,
        
        # Displays
        'Flat-Panel-Monitor': 90.0,
        'CRT-Monitor': 150.0,
        'Flat-Panel-TV': 120.0,
        'CRT-TV': 180.0,
        'Projector': 70.0,
        
        # Appliances
        'Air-Conditioner': 300.0,
        'Washing-Machine': 240.0,
        'Refrigerator': 350.0,
        'Freezer': 300.0,
        'Microwave': 100.0,
        'Dishwasher': 150.0,
        'Coffee-Machine': 50.0,
        'Vacuum-Cleaner': 80.0,
        
        # Electronics
        'Printer': 50.0,
        'Camera': 40.0,
        'Router': 30.0,
        'Speaker': 25.0,
        'Headphone': 15.0,
        'Battery': 10.0,
        'LED-Bulb': 5.0,
        'USB-Flash-Drive': 6.0,
        
        # Legacy compatibility
        'Mobile': 60.0,
        'Desktop': 200.0,
        'Monitor': 90.0,
        'Other': 40.0
    }
    
    # Return carbon savings or default to 40kg if type not in dictionary
    return carbon_savings.get(ewaste_type, 40.0) * quantity
