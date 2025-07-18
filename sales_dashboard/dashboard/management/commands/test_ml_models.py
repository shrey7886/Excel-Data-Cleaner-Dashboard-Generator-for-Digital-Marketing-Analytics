from django.core.management.base import BaseCommand
from dashboard.services import ml_service
from dashboard.models import Client

class Command(BaseCommand):
    help = 'Test ML model training and print accuracy for a given client.'

    def add_arguments(self, parser):
        parser.add_argument('--client-id', type=int, required=True, help='Client ID to train models for')

    def handle(self, *args, **options):
        client_id = options['client_id']
        try:
            client = Client.objects.get(id=client_id)
        except Client.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Client with ID {client_id} does not exist.'))
            return

        self.stdout.write(self.style.SUCCESS(f'Training ML models for client: {client} (ID: {client_id})'))
        success = ml_service.auto_train_models(client_id)
        if success:
            self.stdout.write(self.style.SUCCESS('ML models trained successfully!'))
            for metric, acc in ml_service.model_accuracy.items():
                self.stdout.write(f'\nModel: {metric.upper()}')
                self.stdout.write(f"  MSE: {acc.get('mse')}")
                self.stdout.write(f"  R2: {acc.get('r2')}")
                if 'feature_importance' in acc:
                    self.stdout.write(f"  Feature Importance: {acc['feature_importance']}")
        else:
            self.stdout.write(self.style.ERROR('Model training failed. Not enough data or an error occurred.')) 