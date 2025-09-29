"""
Continuous Learning Scheduler
Automatically processes new transcription results and triggers training sessions
"""

import asyncio
import schedule
import time
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from audio_training_service import AudioEnhancedTrainingService
from llm_training_service import LLMTrainingService, TrainingConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MultimodalResultsHandler(FileSystemEventHandler):
    """File system event handler for new multimodal results"""
    
    def __init__(self, scheduler):
        self.scheduler = scheduler
        self.processed_files = set()
    
    def on_created(self, event):
        """Handle new file creation"""
        if not event.is_directory and event.src_path.endswith('.json'):
            if 'multimodal_analysis_results_' in os.path.basename(event.src_path):
                logger.info(f"New multimodal result detected: {event.src_path}")
                self.scheduler.process_new_result(event.src_path)
    
    def on_modified(self, event):
        """Handle file modification"""
        if not event.is_directory and event.src_path.endswith('.json'):
            if 'multimodal_analysis_results_' in os.path.basename(event.src_path):
                if event.src_path not in self.processed_files:
                    logger.info(f"Modified multimodal result detected: {event.src_path}")
                    self.scheduler.process_new_result(event.src_path)
                    self.processed_files.add(event.src_path)

class ContinuousLearningScheduler:
    """Scheduler for continuous learning operations"""
    
    def __init__(self, 
                 watch_directory: str = ".",
                 training_threshold: int = 20,
                 quality_threshold: float = 0.7,
                 training_interval_hours: int = 6):
        
        self.watch_directory = watch_directory
        self.training_threshold = training_threshold
        self.quality_threshold = quality_threshold
        self.training_interval_hours = training_interval_hours
        
        # Initialize services
        self.audio_service = AudioEnhancedTrainingService()
        self.llm_service = LLMTrainingService()
        
        # Tracking variables
        self.new_samples_count = 0
        self.last_training_time = None
        self.is_training = False
        
        # File system watcher
        self.observer = Observer()
        self.event_handler = MultimodalResultsHandler(self)
        
        # Statistics
        self.stats = {
            'total_processed': 0,
            'successful_processing': 0,
            'training_sessions': 0,
            'last_update': datetime.now().isoformat()
        }
    
    def process_new_result(self, file_path: str) -> bool:
        """Process a new multimodal analysis result"""
        try:
            logger.info(f"Processing new result: {file_path}")
            
            # Process the result file
            success = self.audio_service.process_transcription_result(file_path)
            
            if success:
                self.new_samples_count += 1
                self.stats['successful_processing'] += 1
                logger.info(f"Successfully processed {file_path}. New samples count: {self.new_samples_count}")
                
                # Check if we should trigger training
                if self.should_trigger_training():
                    asyncio.create_task(self.trigger_training_session())
            
            self.stats['total_processed'] += 1
            self.stats['last_update'] = datetime.now().isoformat()
            
            return success
            
        except Exception as e:
            logger.error(f"Error processing result {file_path}: {e}")
            return False
    
    def should_trigger_training(self) -> bool:
        """Determine if training should be triggered"""
        # Check sample count threshold
        if self.new_samples_count < self.training_threshold:
            return False
        
        # Check if already training
        if self.is_training:
            return False
        
        # Check time interval since last training
        if self.last_training_time:
            time_since_last = datetime.now() - self.last_training_time
            if time_since_last < timedelta(hours=self.training_interval_hours):
                return False
        
        return True
    
    async def trigger_training_session(self):
        """Trigger a new training session"""
        try:
            logger.info("Triggering new training session...")
            self.is_training = True
            
            # Get training statistics to determine best approach
            audio_stats = self.audio_service.get_audio_training_statistics()
            
            # Configure training based on available data
            training_config = TrainingConfig(
                model_name="llama3.1:8b",
                num_train_epochs=2,  # Shorter epochs for continuous learning
                per_device_train_batch_size=4,
                learning_rate=0.0003,  # Lower learning rate for stability
                lora_r=16,
                lora_alpha=32,
                lora_dropout=0.1,
                max_length=512
            )
            
            # Start training with quality filters
            filters = {
                'min_quality': self.quality_threshold,
                'limit': min(self.new_samples_count * 2, 1000)  # Don't overwhelm
            }
            
            session_id = await self.llm_service.start_training_session(
                config=training_config,
                filters=filters
            )
            
            if session_id:
                logger.info(f"Started training session: {session_id}")
                self.stats['training_sessions'] += 1
                self.last_training_time = datetime.now()
                self.new_samples_count = 0  # Reset counter
            
        except Exception as e:
            logger.error(f"Error triggering training session: {e}")
        finally:
            self.is_training = False
    
    def start_watching(self):
        """Start watching for new multimodal results"""
        try:
            self.observer.schedule(
                self.event_handler, 
                self.watch_directory, 
                recursive=False
            )
            self.observer.start()
            logger.info(f"Started watching directory: {self.watch_directory}")
            
        except Exception as e:
            logger.error(f"Error starting file watcher: {e}")
    
    def stop_watching(self):
        """Stop watching for new files"""
        try:
            self.observer.stop()
            self.observer.join()
            logger.info("Stopped file watching")
            
        except Exception as e:
            logger.error(f"Error stopping file watcher: {e}")
    
    def process_existing_results(self):
        """Process any existing multimodal results that haven't been processed"""
        try:
            pattern = "multimodal_analysis_results_*.json"
            existing_files = list(Path(self.watch_directory).glob(pattern))
            
            logger.info(f"Found {len(existing_files)} existing result files")
            
            for file_path in existing_files:
                self.process_new_result(str(file_path))
            
        except Exception as e:
            logger.error(f"Error processing existing results: {e}")
    
    def scheduled_maintenance(self):
        """Perform scheduled maintenance tasks"""
        try:
            logger.info("Running scheduled maintenance...")
            
            # Clean up old processed files (optional)
            # Update statistics
            self.stats['last_update'] = datetime.now().isoformat()
            
            # Log current status
            audio_stats = self.audio_service.get_audio_training_statistics()
            logger.info(f"Current audio training samples: {audio_stats.get('total_audio_samples', 0)}")
            logger.info(f"New samples since last training: {self.new_samples_count}")
            
        except Exception as e:
            logger.error(f"Error in scheduled maintenance: {e}")
    
    def get_status(self) -> Dict:
        """Get current scheduler status"""
        return {
            'is_watching': self.observer.is_alive() if hasattr(self, 'observer') else False,
            'is_training': self.is_training,
            'new_samples_count': self.new_samples_count,
            'training_threshold': self.training_threshold,
            'last_training_time': self.last_training_time.isoformat() if self.last_training_time else None,
            'statistics': self.stats,
            'watch_directory': self.watch_directory
        }
    
    def run_scheduler(self):
        """Run the continuous learning scheduler"""
        try:
            # Schedule maintenance tasks
            schedule.every(1).hours.do(self.scheduled_maintenance)
            schedule.every(30).minutes.do(self.process_existing_results)
            
            # Start file watching
            self.start_watching()
            
            # Process existing results on startup
            self.process_existing_results()
            
            logger.info("Continuous learning scheduler started")
            
            # Main loop
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
                
        except KeyboardInterrupt:
            logger.info("Scheduler interrupted by user")
        except Exception as e:
            logger.error(f"Error in scheduler main loop: {e}")
        finally:
            self.stop_watching()

# Global scheduler instance
scheduler_instance = None

def get_scheduler() -> ContinuousLearningScheduler:
    """Get or create scheduler instance"""
    global scheduler_instance
    if scheduler_instance is None:
        scheduler_instance = ContinuousLearningScheduler()
    return scheduler_instance

def start_continuous_learning_service():
    """Start the continuous learning service"""
    scheduler = get_scheduler()
    scheduler.run_scheduler()

if __name__ == "__main__":
    start_continuous_learning_service()