import os
import sys
import subprocess
import time
from pyngrok import ngrok, conf

# --- USER CONFIGURATION (Auth Token) ---
# Uncomment the line below and paste your token if you use a free account
# ngrok.set_auth_token("YOUR_AUTHTOKEN_HERE")

def main():
    """
    Launches Streamlit App and exposes it via ngrok.
    """
    print("🚀 Starting Moim Translator with Public Access...")

    # 1. Setup Tunnel (Port 8501)
    try:
        # Check if auth token is set in env or code
        # conf.get_default().auth_token = "..." 
        
        public_url = ngrok.connect(8501).public_url
        print("\n" + "="*60)
        print(f"🌍  EXTERNALLY ACCESSIBLE LINK:  {public_url}")
        print("="*60 + "\n")
        
        print("ℹ️  Share this link with others to allow them to access your local app.")
        print("ℹ️  (Note: Keep this terminal open!)\n")
        
    except Exception as e:
        print(f"❌ Failed to create ngrok tunnel: {e}")
        print("💡 Hint: If using free tier, you might need an auth token.")
        print("   Sign up at https://dashboard.ngrok.com/get-started/your-authtoken")
        print("   And copy credentials to share_app.py or run `ngrok config add-authtoken <token>`\n")

    # 2. Run Streamlit App
    # We use subprocess to run the command we usually type in terminal/
    try:
        # Assuming we are in the backend directory
        target_file = "streamlit_app.py"
        if not os.path.exists(target_file):
            print(f"⚠️  File {target_file} not found in current directory!")
            sys.exit(1)
            
        print(f"▶️  Running: streamlit run {target_file}")
        subprocess.run(["streamlit", "run", target_file])
        
    except KeyboardInterrupt:
        print("\n🛑 Shutting down server...")
        ngrok.kill()
        sys.exit(0)

if __name__ == "__main__":
    main()
