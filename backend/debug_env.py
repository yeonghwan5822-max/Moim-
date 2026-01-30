import os
from dotenv import load_dotenv

# Path calculation same as crawler.py
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
print(f"Loading env from: {env_path}")

try:
    if os.path.exists(env_path):
        print("✅ File exists.")
        with open(env_path, 'r') as f:
            lines = f.readlines()
            print(f"Line count: {len(lines)}")
            for line in lines:
                if line.startswith("EBC_ID"):
                    print(f"Found EBC_ID line: {line.strip()[:10]}...") 
    else:
        print("❌ File NOT found.")

    load_dotenv(env_path)
    val = os.getenv("EBC_ID")
    if val:
        print(f"✅ Loaded EBC_ID: {val[:2]}***")
    else:
        print("❌ os.getenv('EBC_ID') is None/Empty.")

except Exception as e:
    print(f"Error: {e}")
