# 🦙 Installing Ollama for the Chatbot

## Quick Installation

### Windows
1. **Download Ollama** from: https://ollama.com/download
2. **Run the installer** and follow the setup wizard
3. **Restart your terminal/command prompt**
4. **Run the startup script:**
   ```bash
   python start_server.py
   ```

### Mac
1. **Download Ollama** from: https://ollama.com/download
2. **Install the .dmg file**
3. **Open Terminal and run:**
   ```bash
   python start_server.py
   ```

### Linux
1. **Install Ollama:**
   ```bash
   curl -fsSL https://ollama.com/install.sh | sh
   ```
2. **Run the startup script:**
   ```bash
   python start_server.py
   ```

## What Happens Next

1. **First run** - The script will download the Llama 3 model (this may take 5-10 minutes)
2. **Subsequent runs** - Ollama will start quickly with the already-downloaded model
3. **Chatbot will be available** on every page of your dashboard

## Testing the Installation

After installation, you can test Ollama manually:

```bash
# Check if Ollama is installed
ollama --version

# List available models
ollama list

# Pull Llama 3 (if not already done)
ollama pull llama3

# Start Ollama server
ollama serve
```

## Troubleshooting

### "Ollama not found" error
- Make sure you installed Ollama from https://ollama.com/download
- Restart your terminal/command prompt after installation
- On Windows, you may need to restart your computer

### "Model not found" error
- Run `ollama pull llama3` manually
- Check your internet connection
- The model is about 4GB, so it may take time to download

### Chatbot not responding
- Make sure Ollama is running (`ollama serve`)
- Check that Llama 3 is installed (`ollama list`)
- Try restarting the Django server

## System Requirements

- **RAM:** At least 8GB (16GB recommended)
- **Storage:** At least 10GB free space
- **OS:** Windows 10+, macOS 10.15+, or Linux

## Benefits of Local AI

- **🔒 Privacy** - No data leaves your machine
- **⚡ Speed** - No internet dependency for AI responses
- **💰 Cost** - No API fees or usage limits
- **🛠️ Control** - Full control over the AI model and responses 