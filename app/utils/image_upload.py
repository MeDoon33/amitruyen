"""
Image upload utilities for ImgBB
"""
import requests
import base64
import os
from flask import current_app

def upload_to_imgbb(file):
    """
    Upload image to ImgBB cloud storage
    
    Args:
        file: FileStorage object from request.files
        
    Returns:
        str: Image URL if successful, None otherwise
    """
    try:
        api_key = current_app.config.get('IMGBB_API_KEY')
        
        if not api_key:
            print("Error: IMGBB_API_KEY not found in config")
            return None
        
        # Read file and convert to base64
        file.seek(0)  # Reset file pointer
        image_data = base64.b64encode(file.read()).decode('utf-8')
        
        # ImgBB API endpoint
        url = "https://api.imgbb.com/1/upload"
        
        # Payload
        payload = {
            "key": api_key,
            "image": image_data,
            "name": file.filename  # Optional: preserve original filename
        }
        
        # Upload
        response = requests.post(url, data=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                # Return direct image URL
                image_url = data['data']['url']
                print(f"✅ Image uploaded successfully: {image_url}")
                return image_url
            else:
                print(f"❌ ImgBB API error: {data.get('error', {}).get('message', 'Unknown error')}")
                return None
        else:
            print(f"❌ HTTP error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Upload exception: {str(e)}")
        return None


def is_valid_image(file):
    """
    Check if file is a valid image
    
    Args:
        file: FileStorage object
        
    Returns:
        bool: True if valid image
    """
    if not file or not file.filename:
        return False
    
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp'}
    extension = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
    
    return extension in allowed_extensions


def get_file_size_mb(file):
    """
    Get file size in MB
    
    Args:
        file: FileStorage object
        
    Returns:
        float: File size in MB
    """
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)  # Reset pointer
    return size / (1024 * 1024)  # Convert to MB
