#!/usr/bin/env python
"""
Startup script for the Django server with automatic Ollama/Llama 3 setup
"""
import subprocess
import time
import sys
import os
import requests
from pathlib import Path

def check_ollama_installed():
    """Check if Ollama is installed"""
    try:
        subprocess.run(['ollama', '--version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def start_ollama():
    """Start Ollama with Llama 3"""
    print("🦙 Starting Ollama with Llama 3...")
    
    # Check if Ollama is installed
    if not check_ollama_installed():
        print("❌ Ollama is not installed.")
        print("📥 Please install Ollama from: https://ollama.com/download")
        print("   After installation, run this script again.")
        print("   For now, starting Django without chatbot support...")
        return False
    
    # Check if Llama 3 model is available, if not pull it
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, check=True)
        if 'llama3' not in result.stdout:
            print("📥 Llama 3 model not found. Pulling...")
            print("   This may take a few minutes on first run...")
            subprocess.run(['ollama', 'pull', 'llama3'], check=True)
            print("✅ Llama 3 model downloaded successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error checking/pulling model: {e}")
        print("   Starting Django without chatbot support...")
        return False

    # Start Ollama server in background
    try:
        print("🚀 Starting Ollama server...")
        subprocess.Popen(['ollama', 'serve'], 
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.DEVNULL)
        
        # Wait for Ollama to be ready
        print("⏳ Waiting for Ollama to be ready...")
        for i in range(30):  # Wait up to 30 seconds
            try:
                response = requests.get('http://localhost:11434/api/tags', timeout=1)
                if response.status_code == 200:
                    print("✅ Ollama is ready!")
                    return True
            except requests.exceptions.RequestException:
                pass
            time.sleep(1)
        
        print("⚠️  Ollama may not be ready yet. The chatbot might not work.")
        return False
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting Ollama: {e}")
        print("   Starting Django without chatbot support...")
        return False

def start_django():
    """Start Django development server"""
    print("🌐 Starting Django development server...")
    try:
        subprocess.run(['python', 'manage.py', 'runserver', '127.0.0.1:8000'])
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user.")
    except Exception as e:
        print(f"❌ Error starting Django server: {e}")

def main():
    """Main function to start both Ollama and Django"""
    print("🚀 Starting Digital Marketing Analytics Dashboard...")
    print("=" * 50)
    
    # Change to the sales_dashboard directory
    os.chdir(Path(__file__).parent)
    
    # Start Ollama
    ollama_ready = start_ollama()
    
    if ollama_ready:
        print("✅ Chatbot will be available!")
    else:
        print("⚠️  Chatbot will not be available. Install Ollama for full functionality.")
    
    print("\n" + "=" * 50)
    print("🌐 Starting Django server...")
    print("📱 Access your dashboard at: http://127.0.0.1:8000")
    if ollama_ready:
        print("💬 Chatbot will be available on every page!")
    else:
        print("💬 Chatbot is disabled. Install Ollama for AI support.")
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 50)
    
    # Start Django
    start_django()

if __name__ == "__main__":
    main() 