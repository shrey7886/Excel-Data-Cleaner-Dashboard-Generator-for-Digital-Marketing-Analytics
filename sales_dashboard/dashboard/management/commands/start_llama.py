import subprocess
import time
import os
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Start Llama model server for ML predictions'

    def add_arguments(self, parser):
        parser.add_argument(
            '--model-path',
            type=str,
            default='models/llama-2-7b-chat.gguf',
            help='Path to Llama model file'
        )
        parser.add_argument(
            '--port',
            type=int,
            default=8080,
            help='Port for Llama server (default: 8080)'
        )
        parser.add_argument(
            '--host',
            type=str,
            default='localhost',
            help='Host for Llama server (default: localhost)'
        )

    def handle(self, *args, **options):
        model_path = options['model_path']
        port = options['port']
        host = options['host']

        self.stdout.write(
            self.style.SUCCESS(
                f'Starting Llama server on {host}:{port}'
            )
        )

        try:
            # Check if model file exists
            if not os.path.exists(model_path):
                self.stdout.write(
                    self.style.ERROR(f'Model file not found: {model_path}')
                )
                return

            # Start Llama server using llama.cpp
            cmd = [
                'llama-server',
                '--model', model_path,
                '--host', host,
                '--port', str(port),
                '--ctx-size', '4096',
                '--threads', '4'
            ]

            self.stdout.write(f'Running command: {" ".join(cmd)}')

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Monitor the process
            while True:
                if process.poll() is not None:
                    self.stdout.write(
                        self.style.ERROR('Llama server stopped unexpectedly')
                    )
                    break

                # Check for output
                output = process.stdout.readline()
                if output:
                    self.stdout.write(f'Llama: {output.strip()}')

                time.sleep(1)

        except KeyboardInterrupt:
            self.stdout.write(
                self.style.WARNING('Stopping Llama server...')
            )
            if 'process' in locals():
                process.terminate()
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error starting Llama server: {str(e)}')
            ) 

