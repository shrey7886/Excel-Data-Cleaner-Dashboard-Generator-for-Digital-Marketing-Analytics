# 🚀 Quick Start Guide

## Automatic Startup (Recommended)

### Windows Users
1. **Double-click** `start_server.bat` or run `start_server.ps1` in PowerShell
2. The script will automatically:
   - Install Ollama if needed
   - Download Llama 3 model
   - Start Ollama server
   - Start Django server
   - Open your dashboard at http://127.0.0.1:8000

### Mac/Linux Users
1. **Run the Python script:**
   ```bash
   python start_server.py
   ```

## Manual Startup

If you prefer to start services manually:

### 1. Install Ollama
Download from: https://ollama.com/download

### 2. Pull Llama 3 Model
```bash
ollama pull llama3
```

### 3. Start Ollama Server
```bash
ollama serve
```

### 4. Start Django Server
```bash
python manage.py runserver 127.0.0.1:8000
```

## 🎯 What You Get

- **🌐 Django Dashboard** at http://127.0.0.1:8000
- **💬 AI Chatbot** on every page (powered by Llama 3)
- **🔒 Privacy** - All AI runs locally on your machine
- **🛠️ Full Analytics Platform** with multi-platform data integration

## 🦙 Chatbot Features

The chatbot can help with:
- **Dashboard Navigation** - "How do I connect Google Ads?"
- **Feature Questions** - "How do I download a report?"
- **Troubleshooting** - "Why can't I see my data?"
- **General Support** - "What platforms can I connect?"

## 🛑 Stopping the Server

Press `Ctrl+C` in the terminal to stop both Django and Ollama servers.

## 🔧 Troubleshooting

### Ollama Not Found
- Install Ollama from https://ollama.com/download
- Restart your terminal/command prompt

### Llama 3 Model Not Downloading
- Check your internet connection
- Try running `ollama pull llama3` manually

### Chatbot Not Responding
- Make sure Ollama is running (`ollama serve`)
- Check that Llama 3 model is installed (`ollama list`)

## 📱 Access Your Dashboard

Once started, visit: **http://127.0.0.1:8000**

The chatbot will appear as a floating button on every page! 