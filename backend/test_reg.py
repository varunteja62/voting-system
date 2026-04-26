import requests
import json
import base64

# Dummy base64 image (very small white pixel)
dummy_img = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAABAAEDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZnaGlqc3R1dnd4eXqGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/9oAMBAAIRAxEAPwA= "

def test_register():
    url = "http://localhost:5000/api/register"
    # Using random ID to avoid collision
    import random
    import string
    test_id = "TEST_" + ''.join(random.choices(string.ascii_uppercase, k=5))
    
    payload = {
        "voter_id": test_id,
        "name": "Test User",
        "password": "password123",
        "face_images": [dummy_img, dummy_img, dummy_img]
    }
    
    # We need to bypass CSRF for this local test if it's enabled and strictly enforced 
    # but since it's a POST request from a script to a local dev server, 
    # usually decorators might check Origin or Referer.
    
    try:
        # Note: the actual server is likely running on 5000. 
        # I'll try to call the internal flask app if possible or just use requests.
        r = requests.post(url, json=payload)
        print(f"Status: {r.status_code}")
        print(f"Response: {r.text}")
        return test_id
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    # Note: Spoofing and face detection might fail on a dummy pixel. 
    # I should check if I can mock those or use a real-ish face embedding if I had one.
    # Actually, the server might return 400 because of face detection.
    test_register()
