
try:
    import requests
    print("✅ requests imported")
except ImportError as e:
    print(f"❌ requests failed: {e}")

try:
    from bs4 import BeautifulSoup
    print("✅ bs4 imported")
except ImportError as e:
    print(f"❌ bs4 failed: {e}")

try:
    import pandas
    print("✅ pandas imported")
except ImportError as e:
    print(f"❌ pandas failed: {e}")
