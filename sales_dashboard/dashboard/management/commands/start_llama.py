import subprocess
import time
import requests
import os
import sys
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = 'Start Ollama with Llama 3 for the chatbot'

    def add_arguments(self, parser):
        parser.add_argument(
            '--background',
            action='store_true',
            help='Run Ollama in background mode',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting Ollama with Llama 3...'))
        
        # Check if Ollama is installed
        try:
            subprocess.run(['ollama', '--version'], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.stdout.write(
                self.style.ERROR(
                    'Ollama is not installed. Please install it from https://ollama.com/download'
                )
            )
            return

        # Check if Llama 3 model is available, if not pull it
        try:
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, check=True)
            if 'llama3' not in result.stdout:
                self.stdout.write('Llama 3 model not found. Pulling...')
                subprocess.run(['ollama', 'pull', 'llama3'], check=True)
                self.stdout.write(self.style.SUCCESS('Llama 3 model downloaded successfully!'))
        except subprocess.CalledProcessError as e:
            self.stdout.write(self.style.ERROR(f'Error checking/pulling model: {e}'))
            return

        # Start Ollama server
        try:
            if options['background']:
                # Start in background
                subprocess.Popen(['ollama', 'serve'], 
                               stdout=subprocess.DEVNULL, 
                               stderr=subprocess.DEVNULL)
                self.stdout.write('Ollama started in background mode.')
            else:
                # Start in foreground
                self.stdout.write('Starting Ollama server...')
                subprocess.run(['ollama', 'serve'])
        except subprocess.CalledProcessError as e:
            self.stdout.write(self.style.ERROR(f'Error starting Ollama: {e}'))
            return

        # Wait for Ollama to be ready
        self.stdout.write('Waiting for Ollama to be ready...')
        for i in range(30):  # Wait up to 30 seconds
            try:
                response = requests.get('http://localhost:11434/api/tags', timeout=1)
                if response.status_code == 200:
                    self.stdout.write(self.style.SUCCESS('Ollama is ready!'))
                    return
            except requests.exceptions.RequestException:
                pass
            time.sleep(1)
        
        self.stdout.write(self.style.WARNING('Ollama may not be ready yet. Please check manually.')) 