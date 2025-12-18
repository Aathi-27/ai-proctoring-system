import base64
import numpy as np
import cv2
from typing import Tuple


def decode_base64_image(base64_string: str) -> np.ndarray:
    if "," in base64_string:
        base64_string = base64_string.split(",")[1]
    
    image_data = base64.b64decode(base64_string)
    nparr = np.frombuffer(image_data, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if image is None:
        raise ValueError("Failed to decode image")
    
    return image


def encode_image_to_base64(image: np.ndarray) -> str:
    _, buffer = cv2.imencode('.jpg', image)
    image_base64 = base64.b64encode(buffer).decode('utf-8')
    return f"data:image/jpeg;base64,{image_base64}"


def resize_image(image: np.ndarray, max_width: int = 640, max_height: int = 480) -> np.ndarray:
    h, w = image.shape[:2]
    
    if w <= max_width and h <= max_height:
        return image
    
    scale = min(max_width / w, max_height / h)
    new_w = int(w * scale)
    new_h = int(h * scale)
    
    resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
    return resized


def validate_image_format(image: np.ndarray) -> Tuple[bool, str]:
    if image is None:
        return False, "Image is None"
    
    if len(image.shape) != 3:
        return False, "Image must be 3-channel (BGR)"
    
    if image.shape[2] != 3:
        return False, "Image must have 3 channels"
    
    if image.shape[0] < 50 or image.shape[1] < 50:
        return False, "Image is too small (minimum 50x50)"
    
    return True, "Valid"
