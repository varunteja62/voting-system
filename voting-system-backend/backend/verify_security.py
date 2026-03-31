import requests
import base64
import json

BASE_URL = "http://127.0.0.1:5000/api"

# A dummy small white pixel image in base64
DUMMY_FACE = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgwJR8nMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAABAAEDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1FVWV1hZWmNkZWZnaGlqc3R1dnd4eXqGhcXl5iZmqjp6lr6ls9t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/9o-ADAMBAAIRAxEAPwA8D//Z"

def test_verify_non_existent():
    print("\n[Test 1] Verifying non-existent Voter ID...")
    data = {
        "voter_id": "9999999999",
        "face_image": DUMMY_FACE
    }
    try:
        response = requests.post(f"{BASE_URL}/verify", json=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        assert response.status_code == 404
        assert response.json()['error'] == "Voter not found"
        print("Result: PASS - Correctly rejected non-existent voter.")
    except Exception as e:
        print(f"Test failed: {e}")

def test_verify_wrong_face():
    # We use a real voter ID from the previous query
    voter_id = "jnph56789"
    print(f"\n[Test 2] Verifying real Voter ID ({voter_id}) with non-matching face...")
    data = {
        "voter_id": voter_id,
        "face_image": DUMMY_FACE
    }
    try:
        response = requests.post(f"{BASE_URL}/verify", json=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        # Should fail with 401 or 400 (if face detection fails on dummy)
        if response.status_code == 401:
            print("Result: PASS - Face verification failed as expected.")
        elif response.status_code == 400:
            print("Result: PASS - Face detection failed on dummy image (also acceptable security).")
        else:
            print(f"Result: FAIL - Unexpected status {response.status_code}")
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    test_verify_non_existent()
    test_verify_wrong_face()
