# from django.core.management.base import BaseCommand
# from dashboard.tasks import update_rag_index_task
#
# class Command(BaseCommand):
#     help = "Build or update the FAISS RAG index from marketing data (async via Celery)"
#
#     def handle(self, *args, **kwargs):
#         result = update_rag_index_task.delay()
#         self.stdout.write(self.style.SUCCESS(f"RAG index update task dispatched (task_id={result.id}).")) 