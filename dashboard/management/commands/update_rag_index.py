from django.core.management.base import BaseCommand
from dashboard.rag_pipeline import update_rag_index_from_db

class Command(BaseCommand):
    help = "Build or update the FAISS RAG index from marketing data"

    def handle(self, *args, **kwargs):
        update_rag_index_from_db()
        self.stdout.write(self.style.SUCCESS("RAG index updated successfully.")) 