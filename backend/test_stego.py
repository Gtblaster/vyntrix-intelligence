import requests
import numpy as np
from PIL import Image
import io
import time

URL = "http://127.0.0.1:8000/scan-image/"

def embed_lsb(image, payload_text):
    img_array = np.array(image.convert('RGB'))
    
    # Convert payload to bits
    bits = ''.join([format(ord(c), '08b') for c in payload_text])
    
    flat_array = img_array.flatten()
    if len(bits) > len(flat_array):
        raise ValueError("Payload too large")
        
    for i, bit in enumerate(bits):
        # Clear LSB and set to bit
        flat_array[i] = (flat_array[i] & ~1) | int(bit)
        
    encoded_array = flat_array.reshape(img_array.shape)
    return Image.fromarray(encoded_array.astype('uint8'))

def test_api():
    print("Generating validation test cases...")
    
    # 1. Clean image
    clean_img = Image.new("RGB", (100, 100), color=(100, 150, 200))
    # Add some noise to simulate a real photo
    noise = np.random.randint(0, 50, (100, 100, 3), dtype=np.uint8)
    clean_img = Image.fromarray(np.clip(np.array(clean_img) + noise, 0, 255).astype('uint8'))
    
    # 2. Steganography Payload
    payload = "Vyntrix Deep Learning Payload Test 101."
    infected_img = embed_lsb(clean_img, payload)

    clean_buf = io.BytesIO()
    clean_img.save(clean_buf, format="PNG")
    clean_buf.seek(0)
    
    infected_buf = io.BytesIO()
    infected_img.save(infected_buf, format="PNG")
    infected_buf.seek(0)
    
    invalid_buf = io.BytesIO(b"This is just some text, not an image format.")
    
    print("\n--- Testing CLEAN Image ---")
    res_clean = requests.post(URL, files={"file": ("clean.png", clean_buf, "image/png")})
    print(res_clean.status_code, res_clean.json() if res_clean.status_code == 200 else res_clean.text)
    
    print("\n--- Testing INFECTED (LSB) Image ---")
    res_infected = requests.post(URL, files={"file": ("infected.png", infected_buf, "image/png")})
    # Omit overlay string to keep logs clean
    json_infected = res_infected.json()
    if "highlight_overlay" in json_infected and json_infected["highlight_overlay"]:
        json_infected["highlight_overlay"] = "<BASE64_IMAGE_DATA>"
    print(res_clean.status_code, json_infected)
    
    print("\n--- Testing INVALID FORMAT Handling ---")
    res_invalid = requests.post(URL, files={"file": ("bad_file.txt", invalid_buf, "image/jpeg")})
    print(res_invalid.status_code, res_invalid.text)
    
if __name__ == "__main__":
    # Wait a second to ensure latest uvicorn reload is up
    time.sleep(2)
    test_api()
