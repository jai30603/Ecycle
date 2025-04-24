import os
import uuid
import feedparser
import requests
from io import BytesIO
from datetime import datetime
from flask import current_app, url_for
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm

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

def generate_disposal_certificate(user, ewaste, schedule):
    """
    Generate a PDF disposal certificate for a completed e-waste pickup
    
    Args:
        user (User): User who scheduled the pickup
        ewaste (Ewaste): The e-waste item collected
        schedule (Schedule): The schedule/pickup record
        
    Returns:
        BytesIO: PDF document as a byte stream
    """
    # Create a PDF buffer to store the PDF
    buffer = BytesIO()
    
    # Set up the PDF document
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    # Styles for the document
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='CertificateTitle',
        fontName='Helvetica-Bold',
        fontSize=16,
        alignment=1,
        spaceAfter=12
    ))
    styles.add(ParagraphStyle(
        name='CertificateSubTitle',
        fontName='Helvetica-Bold',
        fontSize=12,
        alignment=1,
        spaceAfter=12
    ))
    styles.add(ParagraphStyle(
        name='Normal-Center',
        parent=styles['Normal'],
        alignment=1
    ))
    styles.add(ParagraphStyle(
        name='Bold-Center',
        parent=styles['BodyText'],
        fontName='Helvetica-Bold',
        alignment=1
    ))
    
    # Generate a unique certificate number
    certificate_number = f"ECO-{uuid.uuid4().hex[:8].upper()}-{schedule.id}"
    
    # Format dates
    pickup_date = schedule.pickup_date.strftime("%B %d, %Y")
    issued_date = datetime.now().strftime("%B %d, %Y")
    
    # Calculate environmental impact
    carbon_saved = calculate_carbon_footprint(ewaste.ewaste_type)
    
    # Build the document content
    elements = []
    
    # Add logo (if available) or title
    try:
        # Specify the correct path to your logo
        logo_path = os.path.join('static', 'img', 'ecycle-logo.png')
        if os.path.exists(logo_path):
            logo = Image(logo_path)
            logo.drawHeight = 1.5*inch
            logo.drawWidth = 1.5*inch
            elements.append(logo)
        else:
            # If logo doesn't exist, just use text
            elements.append(Paragraph('E-CYCLE', styles['CertificateTitle']))
    except Exception as e:
        current_app.logger.error(f"Error adding logo to certificate: {str(e)}")
        elements.append(Paragraph('E-CYCLE', styles['CertificateTitle']))
    
    # Certificate Title
    elements.append(Paragraph('E-WASTE DISPOSAL CERTIFICATE', styles['CertificateTitle']))
    elements.append(Spacer(1, 0.25*inch))
    
    # Certificate Number and Date
    elements.append(Paragraph(f'Certificate Number: {certificate_number}', styles['Bold-Center']))
    elements.append(Paragraph(f'Issued: {issued_date}', styles['Normal-Center']))
    elements.append(Spacer(1, 0.5*inch))
    
    # Introduction Text
    intro_text = f'''
    This is to certify that <b>{user.username}</b> has responsibly disposed of electronic waste 
    through the Ecycle platform, contributing to environmental sustainability and proper e-waste management.
    '''
    elements.append(Paragraph(intro_text, styles['Normal-Center']))
    elements.append(Spacer(1, 0.25*inch))
    
    # Device Information
    device_data = [
        ['DEVICE INFORMATION', ''],
        ['E-Waste Type:', ewaste.ewaste_type.replace('-', ' ')],
        ['Model/Brand:', ewaste.model if ewaste.model else 'Not specified'],
        ['Condition:', ewaste.condition],
        ['Pickup Date:', pickup_date],
        ['Pickup Reference:', f'#{schedule.id}']
    ]
    
    device_table = Table(device_data, colWidths=[2*inch, 3*inch])
    device_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (1, 0), colors.green),
        ('TEXTCOLOR', (0, 0), (1, 0), colors.white),
        ('ALIGN', (0, 0), (1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (1, 0), 8),
        ('BACKGROUND', (0, 1), (1, 5), colors.white),
        ('GRID', (0, 0), (1, 5), 1, colors.black),
        ('VALIGN', (0, 0), (1, 5), 'MIDDLE'),
    ]))
    elements.append(device_table)
    elements.append(Spacer(1, 0.25*inch))
    
    # Environmental Impact
    impact_data = [
        ['ENVIRONMENTAL IMPACT', ''],
        ['Carbon Footprint Saved:', f'{carbon_saved:.1f} kg CO₂e'],
        ['Eco Points Earned:', f'{ewaste.eco_points} points'],
        ['Recycling Method:', 'Responsible Recycling & Resource Recovery']
    ]
    
    impact_table = Table(impact_data, colWidths=[2*inch, 3*inch])
    impact_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (1, 0), colors.blue),
        ('TEXTCOLOR', (0, 0), (1, 0), colors.white),
        ('ALIGN', (0, 0), (1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (1, 0), 8),
        ('BACKGROUND', (0, 1), (1, 3), colors.white),
        ('GRID', (0, 0), (1, 3), 1, colors.black),
        ('VALIGN', (0, 0), (1, 3), 'MIDDLE'),
    ]))
    elements.append(impact_table)
    elements.append(Spacer(1, 0.25*inch))
    
    # Certification Statement
    certification_text = '''
    <b>CERTIFICATION STATEMENT</b><br/><br/>
    This is to certify that the above-mentioned electronic waste item was collected and 
    processed in accordance with responsible e-waste management practices and applicable 
    environmental regulations. All data storage devices have been securely wiped or physically 
    destroyed as appropriate.
    '''
    elements.append(Paragraph(certification_text, styles['Normal-Center']))
    elements.append(Spacer(1, 0.5*inch))
    
    # Signature
    signature_data = [
        ['', ''],
        ['_______________________', '_______________________'],
        ['Authorized Signature', 'Date'],
        ['Ecycle Recycling Officer', '']
    ]
    
    signature_table = Table(signature_data, colWidths=[2.5*inch, 2.5*inch])
    signature_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (1, 3), 'CENTER'),
        ('VALIGN', (0, 0), (1, 3), 'MIDDLE'),
    ]))
    elements.append(signature_table)
    elements.append(Spacer(1, 0.25*inch))
    
    # Footer
    footer_text = '''
    <i>Thank you for contributing to a sustainable future by responsibly recycling your electronic waste.</i>
    '''
    elements.append(Paragraph(footer_text, styles['Normal-Center']))
    
    # Build the PDF
    doc.build(elements)
    
    # Reset buffer position to the beginning
    buffer.seek(0)
    
    return buffer
