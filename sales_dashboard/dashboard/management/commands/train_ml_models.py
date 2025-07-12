from django.core.management.base import BaseCommand
from dashboard.services import ml_service

class Command(BaseCommand):
    help = 'Train ML models automatically on available campaign data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--client-id',
            type=int,
            help='Train models for specific client ID',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force retraining even if models exist',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🤖 Starting automatic ML model training...'))
        
        client_id = options.get('client_id')
        force_retrain = options.get('force')
        
        if client_id:
            self.stdout.write(f'Training models for client ID: {client_id}')
        else:
            self.stdout.write('Training models on all available data')
        
        # Train models
        success = ml_service.auto_train_models(client_id)
        
        if success:
            self.stdout.write(
                self.style.SUCCESS('✅ ML models trained successfully!')
            )
            
            # Display model accuracies
            if ml_service.model_accuracy:
                self.stdout.write('\n📊 Model Performance:')
                for model_name, metrics in ml_service.model_accuracy.items():
                    self.stdout.write(f'  {model_name.upper()}:')
                    self.stdout.write(f'    R² Score: {metrics["r2"]:.3f}')
                    self.stdout.write(f'    MSE: {metrics["mse"]:.6f}')
            
            self.stdout.write('\n🎯 Models are now ready for predictions!')
            self.stdout.write('💡 Use the dashboard to see AI-powered insights.')
            
        else:
            self.stdout.write(
                self.style.ERROR('❌ Model training failed. Check the logs above for details.')
            )
            self.stdout.write('💡 Make sure you have at least 10 campaigns with sufficient data.') 