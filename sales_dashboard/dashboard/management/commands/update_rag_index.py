import sys
import os
from django.core.management.base import BaseCommand

# Ensure dashboard/ is on the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
dashboard_dir = os.path.abspath(os.path.join(current_dir, '../../..'))
if dashboard_dir not in sys.path:
    sys.path.insert(0, dashboard_dir)

from dashboard.rag_pipeline import update_rag_index_from_db

class Command(BaseCommand):
    help = "Build or update the FAISS RAG index from marketing data"

    def handle(self, *args, **kwargs):
        update_rag_index_from_db()
        self.stdout.write(self.style.SUCCESS("RAG index updated successfully.")) 