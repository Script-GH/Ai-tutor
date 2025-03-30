from celery import Celery
from dotenv import load_dotenv
import os
import logging
from pymongo import MongoClient
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    filename=os.getenv('LOG_FILE', 'celery.log'),
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Celery
celery = Celery(
    'tasks',
    broker=os.getenv('REDIS_URL'),
    backend=os.getenv('REDIS_URL')
)

# MongoDB connection
mongo_client = MongoClient(os.getenv('MONGODB_URI'))
db = mongo_client[os.getenv('DB_NAME')]

@celery.task(bind=True)
def generate_test(self, data):
    """
    Background task to generate test from syllabus
    """
    try:
        logger.info(f"Starting test generation for task {self.request.id}")
        
        # Update task status
        self.update_state(state='PROCESSING')
        
        # TODO: Implement actual test generation logic here
        # This would typically involve:
        # 1. Retrieving syllabus content
        # 2. Processing with AI/ML models
        # 3. Generating questions
        # 4. Formatting results
        
        # For now, we'll just log and store a placeholder result
        result = {
            'task_id': self.request.id,
            'status': 'completed',
            'timestamp': datetime.utcnow(),
            'data': {
                'message': 'Test generation completed',
                'syllabus_id': data.get('syllabus_id')
            }
        }
        
        # Store result in MongoDB
        db.test_results.insert_one(result)
        
        logger.info(f"Test generation completed for task {self.request.id}")
        return result
        
    except Exception as e:
        logger.error(f"Test generation failed for task {self.request.id}: {e}")
        self.update_state(state='FAILURE', meta={'error': str(e)})
        raise

@celery.task
def cleanup_old_files():
    """
    Periodic task to cleanup old temporary files
    """
    try:
        # Implement cleanup logic here
        logger.info("Starting cleanup task")
        
        # Example: Delete files older than 30 days
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        result = db.syllabi.delete_many({
            'uploaded_at': {'$lt': cutoff_date},
            'status': 'temporary'
        })
        
        logger.info(f"Cleanup completed. Deleted {result.deleted_count} files")
        
    except Exception as e:
        logger.error(f"Cleanup task failed: {e}")
        raise

# Configure periodic tasks
celery.conf.beat_schedule = {
    'cleanup-old-files': {
        'task': 'tasks.cleanup_old_files',
        'schedule': 86400.0,  # Run daily
    },
} 