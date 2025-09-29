"""
LLM Training Service for Arabic STT Post-Processing
Provides comprehensive training capabilities for fine-tuning Llama models on Arabic text data
"""

import asyncio
import json
import logging
import os
import sqlite3
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum

import torch
from transformers import (
    AutoTokenizer, AutoModelForCausalLM, 
    TrainingArguments, Trainer, DataCollatorForLanguageModeling
)
from peft import LoraConfig, get_peft_model, TaskType
from datasets import Dataset
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TrainingDataType(Enum):
    """Types of training data for different purposes"""
    TRANSCRIPTION_CORRECTION = "transcription_correction"
    GRAMMAR_ENHANCEMENT = "grammar_enhancement"
    DIALECT_ADAPTATION = "dialect_adaptation"
    CONTEXT_UNDERSTANDING = "context_understanding"

class ModelVersion(Enum):
    """Available model versions for training"""
    LLAMA_8B = "llama3.1:8b"
    LLAMA_70B = "llama3.1:70b-instruct-q4_K_M"
    AYA_35B = "aya:35b-23-q4_K_M"

@dataclass
class TrainingDataPoint:
    """Single training data point with input/output pair"""
    id: str
    input_text: str
    target_text: str
    data_type: TrainingDataType
    dialect: Optional[str] = None
    quality_score: Optional[float] = None
    user_feedback: Optional[str] = None
    timestamp: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class TrainingConfig:
    """Configuration for fine-tuning process"""
    model_name: str = "llama3.1:8b"
    output_dir: str = "./trained_models"
    num_train_epochs: int = 3
    per_device_train_batch_size: int = 4
    per_device_eval_batch_size: int = 4
    warmup_steps: int = 500
    weight_decay: float = 0.01
    logging_dir: str = "./logs"
    save_steps: int = 1000
    eval_steps: int = 500
    learning_rate: float = 5e-4
    
    # LoRA specific parameters
    lora_r: int = 16
    lora_alpha: int = 32
    lora_dropout: float = 0.1
    target_modules: List[str] = None
    
    # Arabic-specific parameters
    max_length: int = 512
    temperature: float = 0.7
    top_p: float = 0.9

class TrainingDataManager:
    """Manages training data collection, storage, and retrieval"""
    
    def __init__(self, db_path: str = "training_data.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database for training data storage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS training_data (
                id TEXT PRIMARY KEY,
                input_text TEXT NOT NULL,
                target_text TEXT NOT NULL,
                data_type TEXT NOT NULL,
                dialect TEXT,
                quality_score REAL,
                user_feedback TEXT,
                timestamp TEXT,
                metadata TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS training_sessions (
                session_id TEXT PRIMARY KEY,
                model_name TEXT NOT NULL,
                config TEXT NOT NULL,
                start_time TEXT,
                end_time TEXT,
                status TEXT,
                metrics TEXT,
                model_path TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def add_training_data(self, data_point: TrainingDataPoint) -> bool:
        """Add a new training data point"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO training_data 
                (id, input_text, target_text, data_type, dialect, quality_score, 
                 user_feedback, timestamp, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data_point.id,
                data_point.input_text,
                data_point.target_text,
                data_point.data_type.value,
                data_point.dialect,
                data_point.quality_score,
                data_point.user_feedback,
                data_point.timestamp or datetime.now().isoformat(),
                json.dumps(data_point.metadata) if data_point.metadata else None
            ))
            
            conn.commit()
            conn.close()
            logger.info(f"Added training data point: {data_point.id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding training data: {e}")
            return False
    
    def get_training_data(self, 
                         data_type: Optional[TrainingDataType] = None,
                         dialect: Optional[str] = None,
                         min_quality: Optional[float] = None,
                         limit: Optional[int] = None) -> List[TrainingDataPoint]:
        """Retrieve training data with optional filters"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = "SELECT * FROM training_data WHERE 1=1"
            params = []
            
            if data_type:
                query += " AND data_type = ?"
                params.append(data_type.value)
            
            if dialect:
                query += " AND dialect = ?"
                params.append(dialect)
            
            if min_quality:
                query += " AND quality_score >= ?"
                params.append(min_quality)
            
            if limit:
                query += " LIMIT ?"
                params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()
            
            data_points = []
            for row in rows:
                metadata = json.loads(row[8]) if row[8] else None
                data_point = TrainingDataPoint(
                    id=row[0],
                    input_text=row[1],
                    target_text=row[2],
                    data_type=TrainingDataType(row[3]),
                    dialect=row[4],
                    quality_score=row[5],
                    user_feedback=row[6],
                    timestamp=row[7],
                    metadata=metadata
                )
                data_points.append(data_point)
            
            return data_points
            
        except Exception as e:
            logger.error(f"Error retrieving training data: {e}")
            return []

class LoRATrainer:
    """Handles LoRA fine-tuning for Llama models"""
    
    def __init__(self, config: TrainingConfig):
        self.config = config
        self.tokenizer = None
        self.model = None
        self.peft_model = None
    
    def load_model(self):
        """Load the base model and tokenizer"""
        try:
            # For local Ollama models, we'll use a compatible HuggingFace model
            model_mapping = {
                "llama3.1:8b": "meta-llama/Llama-3.1-8B-Instruct",
                "llama3.1:70b-instruct-q4_K_M": "meta-llama/Llama-3.1-70B-Instruct",
                "aya:35b-23-q4_K_M": "CohereForAI/aya-23-35B"
            }
            
            hf_model_name = model_mapping.get(self.config.model_name, "meta-llama/Llama-3.1-8B-Instruct")
            
            logger.info(f"Loading model: {hf_model_name}")
            
            self.tokenizer = AutoTokenizer.from_pretrained(hf_model_name)
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            self.model = AutoModelForCausalLM.from_pretrained(
                hf_model_name,
                torch_dtype=torch.float16,
                device_map="auto",
                trust_remote_code=True
            )
            
            logger.info("Model loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False
    
    def setup_lora(self):
        """Setup LoRA configuration and wrap the model"""
        try:
            target_modules = self.config.target_modules or [
                "q_proj", "k_proj", "v_proj", "o_proj",
                "gate_proj", "up_proj", "down_proj"
            ]
            
            lora_config = LoraConfig(
                task_type=TaskType.CAUSAL_LM,
                r=self.config.lora_r,
                lora_alpha=self.config.lora_alpha,
                lora_dropout=self.config.lora_dropout,
                target_modules=target_modules,
                bias="none"
            )
            
            self.peft_model = get_peft_model(self.model, lora_config)
            self.peft_model.print_trainable_parameters()
            
            logger.info("LoRA configuration applied successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error setting up LoRA: {e}")
            return False
    
    def prepare_dataset(self, training_data: List[TrainingDataPoint]) -> Dataset:
        """Prepare dataset for training"""
        def format_prompt(data_point: TrainingDataPoint) -> str:
            """Format training data into prompt-response format"""
            if data_point.data_type == TrainingDataType.TRANSCRIPTION_CORRECTION:
                return f"تصحيح النص التالي: {data_point.input_text}\nالنص المصحح: {data_point.target_text}"
            elif data_point.data_type == TrainingDataType.GRAMMAR_ENHANCEMENT:
                return f"تحسين قواعد النحو للنص: {data_point.input_text}\nالنص المحسن: {data_point.target_text}"
            elif data_point.data_type == TrainingDataType.DIALECT_ADAPTATION:
                dialect_name = data_point.dialect or "عربي"
                return f"تحويل النص إلى {dialect_name}: {data_point.input_text}\nالنص المحول: {data_point.target_text}"
            else:
                return f"المدخل: {data_point.input_text}\nالمخرج: {data_point.target_text}"
        
        # Format all training examples
        formatted_texts = [format_prompt(dp) for dp in training_data]
        
        # Tokenize the data
        def tokenize_function(examples):
            return self.tokenizer(
                examples["text"],
                truncation=True,
                padding=True,
                max_length=self.config.max_length,
                return_tensors="pt"
            )
        
        # Create dataset
        dataset = Dataset.from_dict({"text": formatted_texts})
        tokenized_dataset = dataset.map(tokenize_function, batched=True)
        
        return tokenized_dataset
    
    def train(self, training_data: List[TrainingDataPoint]) -> Dict[str, Any]:
        """Execute the training process"""
        try:
            if not self.load_model():
                return {"success": False, "error": "Failed to load model"}
            
            if not self.setup_lora():
                return {"success": False, "error": "Failed to setup LoRA"}
            
            # Prepare dataset
            dataset = self.prepare_dataset(training_data)
            
            # Split dataset for training and validation
            train_size = int(0.9 * len(dataset))
            train_dataset = dataset.select(range(train_size))
            eval_dataset = dataset.select(range(train_size, len(dataset)))
            
            # Setup training arguments
            training_args = TrainingArguments(
                output_dir=self.config.output_dir,
                num_train_epochs=self.config.num_train_epochs,
                per_device_train_batch_size=self.config.per_device_train_batch_size,
                per_device_eval_batch_size=self.config.per_device_eval_batch_size,
                warmup_steps=self.config.warmup_steps,
                weight_decay=self.config.weight_decay,
                logging_dir=self.config.logging_dir,
                logging_steps=100,
                save_steps=self.config.save_steps,
                eval_steps=self.config.eval_steps,
                evaluation_strategy="steps",
                save_strategy="steps",
                load_best_model_at_end=True,
                metric_for_best_model="eval_loss",
                greater_is_better=False,
                learning_rate=self.config.learning_rate,
                fp16=True,  # Enable mixed precision for RTX 5090
                dataloader_pin_memory=True,
                gradient_checkpointing=True,
                remove_unused_columns=False
            )
            
            # Data collator
            data_collator = DataCollatorForLanguageModeling(
                tokenizer=self.tokenizer,
                mlm=False
            )
            
            # Initialize trainer
            trainer = Trainer(
                model=self.peft_model,
                args=training_args,
                train_dataset=train_dataset,
                eval_dataset=eval_dataset,
                data_collator=data_collator,
                tokenizer=self.tokenizer
            )
            
            # Start training
            logger.info("Starting training...")
            start_time = time.time()
            
            training_result = trainer.train()
            
            end_time = time.time()
            training_duration = end_time - start_time
            
            # Save the model
            model_save_path = os.path.join(self.config.output_dir, "final_model")
            trainer.save_model(model_save_path)
            
            # Prepare results
            results = {
                "success": True,
                "training_duration": training_duration,
                "final_loss": training_result.training_loss,
                "model_path": model_save_path,
                "training_samples": len(train_dataset),
                "eval_samples": len(eval_dataset),
                "epochs_completed": self.config.num_train_epochs
            }
            
            logger.info(f"Training completed successfully in {training_duration:.2f} seconds")
            return results
            
        except Exception as e:
            logger.error(f"Training failed: {e}")
            return {"success": False, "error": str(e)}

class LLMTrainingService:
    """Main service for managing LLM training operations"""
    
    def __init__(self):
        self.data_manager = TrainingDataManager()
        self.current_session = None
    
    async def collect_transcription_feedback(self, 
                                           original_text: str,
                                           corrected_text: str,
                                           user_id: str = "system",
                                           quality_score: float = None) -> bool:
        """Collect user feedback on transcription corrections"""
        data_point = TrainingDataPoint(
            id=f"correction_{int(time.time())}_{hash(original_text) % 10000}",
            input_text=original_text,
            target_text=corrected_text,
            data_type=TrainingDataType.TRANSCRIPTION_CORRECTION,
            quality_score=quality_score,
            timestamp=datetime.now().isoformat(),
            metadata={"user_id": user_id, "source": "transcription_feedback"}
        )
        
        return self.data_manager.add_training_data(data_point)
    
    async def collect_dialect_sample(self,
                                   standard_text: str,
                                   dialect_text: str,
                                   dialect_name: str,
                                   quality_score: float = None) -> bool:
        """Collect dialect adaptation samples"""
        data_point = TrainingDataPoint(
            id=f"dialect_{int(time.time())}_{hash(standard_text) % 10000}",
            input_text=standard_text,
            target_text=dialect_text,
            data_type=TrainingDataType.DIALECT_ADAPTATION,
            dialect=dialect_name,
            quality_score=quality_score,
            timestamp=datetime.now().isoformat(),
            metadata={"dialect": dialect_name, "source": "dialect_collection"}
        )
        
        return self.data_manager.add_training_data(data_point)
    
    async def start_training_session(self, 
                                   config: TrainingConfig,
                                   data_filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Start a new training session"""
        try:
            # Get training data based on filters
            filters = data_filters or {}
            training_data = self.data_manager.get_training_data(
                data_type=filters.get("data_type"),
                dialect=filters.get("dialect"),
                min_quality=filters.get("min_quality", 0.7),
                limit=filters.get("limit")
            )
            
            if len(training_data) < 10:
                return {
                    "success": False,
                    "error": f"Insufficient training data. Found {len(training_data)} samples, need at least 10"
                }
            
            # Initialize trainer
            trainer = LoRATrainer(config)
            
            # Start training
            session_id = f"session_{int(time.time())}"
            self.current_session = session_id
            
            logger.info(f"Starting training session {session_id} with {len(training_data)} samples")
            
            # Execute training
            results = trainer.train(training_data)
            
            # Store session results
            if results["success"]:
                logger.info(f"Training session {session_id} completed successfully")
            else:
                logger.error(f"Training session {session_id} failed: {results.get('error')}")
            
            results["session_id"] = session_id
            results["training_data_count"] = len(training_data)
            
            return results
            
        except Exception as e:
            logger.error(f"Error in training session: {e}")
            return {"success": False, "error": str(e)}
    
    def get_training_statistics(self) -> Dict[str, Any]:
        """Get statistics about collected training data"""
        try:
            all_data = self.data_manager.get_training_data()
            
            stats = {
                "total_samples": len(all_data),
                "by_type": {},
                "by_dialect": {},
                "quality_distribution": {"high": 0, "medium": 0, "low": 0, "unrated": 0}
            }
            
            for data_point in all_data:
                # Count by type
                type_name = data_point.data_type.value
                stats["by_type"][type_name] = stats["by_type"].get(type_name, 0) + 1
                
                # Count by dialect
                dialect = data_point.dialect or "standard"
                stats["by_dialect"][dialect] = stats["by_dialect"].get(dialect, 0) + 1
                
                # Quality distribution
                if data_point.quality_score is None:
                    stats["quality_distribution"]["unrated"] += 1
                elif data_point.quality_score >= 0.8:
                    stats["quality_distribution"]["high"] += 1
                elif data_point.quality_score >= 0.6:
                    stats["quality_distribution"]["medium"] += 1
                else:
                    stats["quality_distribution"]["low"] += 1
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting training statistics: {e}")
            return {"error": str(e)}

# Global service instance
training_service = LLMTrainingService()