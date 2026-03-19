import base64
import os

DIR = r"C:\Users\varun\.gemini\antigravity\brain\c60cf70d-e0a1-4095-be7e-269591cc449e"
files = [f for f in os.listdir(DIR) if f.startswith("dummy_face_voter") and f.endswith(".png")]

for f in files:
    path = os.path.join(DIR, f)
    with open(path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        data_uri = f"data:image/png;base64,{encoded_string}"
        
        output_path = os.path.join(DIR, f.replace(".png", "_base64.txt"))
        with open(output_path, "w") as out:
            out.write(data_uri)
    print(f"Converted {f} to base64")
