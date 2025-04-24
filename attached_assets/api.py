import os
from inference_sdk import InferenceHTTPClient

# Initialize the Roboflow client with the API key from environment variables
api_key = os.environ.get('ROBOFLOW_API_KEY')
if not api_key:
    raise ValueError("ROBOFLOW_API_KEY environment variable is not set")

CLIENT = InferenceHTTPClient(
    api_url="https://detect.roboflow.com",
    api_key=api_key
)

def classify_image(image_path):
    """
    Classify an e-waste image using Roboflow API
    
    Args:
        image_path (str): Path to the image file
        
    Returns:
        dict: Classification results from Roboflow
    """
    try:
        # Using the new model ID provided
        result = CLIENT.infer(image_path, model_id="e-waste-dataset-r0ojc/43")
        return result
    except Exception as e:
        print(f"Error classifying image: {str(e)}")
        raise Exception(f"Classification failed: {str(e)}")
