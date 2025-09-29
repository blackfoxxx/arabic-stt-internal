"""
LLM Service Module for Arabic STT System
Integrates Ollama local LLM for text post-processing and enhancement
"""

import requests
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import asyncio
import aiohttp

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class LLMConfig:
    """Configuration for LLM service - Optimized for RTX 5090"""
    base_url: str = "http://localhost:11434"
    model: str = "llama3.1:70b-instruct-q4_K_M"  # Upgraded to 70B for better Arabic understanding
    fallback_model: str = "llama3.1:8b"  # Keep 8B as fallback for high-volume processing
    dialect_model: str = "aya:35b-23-q4_K_M"  # Specialized for Arabic dialects
    timeout: int = 60  # Increased timeout for larger model
    max_retries: int = 3
    temperature: float = 0.1  # Lower temperature for more consistent results
    top_p: float = 0.9
    max_tokens: int = 2048

@dataclass
class LLMResponse:
    """Response from LLM service"""
    success: bool
    content: str
    error: Optional[str] = None
    processing_time: Optional[float] = None

class OllamaLLMService:
    """Service for interacting with Ollama LLM"""
    
    def __init__(self, config: LLMConfig = None):
        self.config = config or LLMConfig()
        self.session = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.config.timeout)
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    def is_available(self) -> bool:
        """Check if Ollama service is available"""
        try:
            response = requests.get(f"{self.config.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Ollama service not available: {e}")
            return False
    
    def get_available_models(self) -> List[str]:
        """Get list of available models"""
        try:
            response = requests.get(f"{self.config.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return [model['name'] for model in data.get('models', [])]
            return []
        except Exception as e:
            logger.error(f"Error getting models: {e}")
            return []
    
    async def generate_text(self, prompt: str, system_prompt: str = None, model_override: str = None, use_dialect_model: bool = False) -> LLMResponse:
        """Generate text using Ollama LLM with model selection"""
        import time
        start_time = time.time()
        
        # Select appropriate model
        selected_model = self.config.model  # Default to primary (70B)
        if model_override:
            selected_model = model_override
        elif use_dialect_model and hasattr(self.config, 'dialect_model'):
            selected_model = self.config.dialect_model
        
        try:
            payload = {
                "model": selected_model,
                "prompt": prompt,
                "stream": False
            }
            
            # Add advanced parameters for better quality
            if hasattr(self.config, 'temperature'):
                payload["options"] = {
                    "temperature": self.config.temperature,
                    "top_p": self.config.top_p,
                    "num_predict": self.config.max_tokens
                }
            
            if system_prompt:
                payload["system"] = system_prompt
            
            if not self.session:
                self.session = aiohttp.ClientSession(
                    timeout=aiohttp.ClientTimeout(total=self.config.timeout)
                )
            
            async with self.session.post(
                f"{self.config.base_url}/api/generate",
                json=payload
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    processing_time = time.time() - start_time
                    
                    return LLMResponse(
                        success=True,
                        content=data.get('response', ''),
                        processing_time=processing_time
                    )
                else:
                    error_text = await response.text()
                    # Try fallback model if primary fails
                    if selected_model == self.config.model and hasattr(self.config, 'fallback_model'):
                        logger.warning(f"Primary model failed, trying fallback: {self.config.fallback_model}")
                        return await self.generate_text(prompt, system_prompt, self.config.fallback_model)
                    
                    return LLMResponse(
                        success=False,
                        content='',
                        error=f"HTTP {response.status}: {error_text}"
                    )
                    
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Error generating text with {selected_model}: {e}")
            
            # Try fallback model if primary fails
            if selected_model == self.config.model and hasattr(self.config, 'fallback_model'):
                logger.warning(f"Primary model failed, trying fallback: {self.config.fallback_model}")
                return await self.generate_text(prompt, system_prompt, self.config.fallback_model)
            
            return LLMResponse(
                success=False,
                content='',
                error=str(e),
                processing_time=processing_time
            )
    
    def generate_text_sync(self, prompt: str, system_prompt: str = None, model_override: str = None, use_dialect_model: bool = False) -> LLMResponse:
        """Synchronous version of generate_text with model selection"""
        import time
        start_time = time.time()
        
        # Select appropriate model
        selected_model = self.config.model  # Default to primary (70B)
        if model_override:
            selected_model = model_override
        elif use_dialect_model and hasattr(self.config, 'dialect_model'):
            selected_model = self.config.dialect_model
        
        try:
            payload = {
                "model": selected_model,
                "prompt": prompt,
                "stream": False
            }
            
            # Add advanced parameters for better quality
            if hasattr(self.config, 'temperature'):
                payload["options"] = {
                    "temperature": self.config.temperature,
                    "top_p": self.config.top_p,
                    "num_predict": self.config.max_tokens
                }
            
            if system_prompt:
                payload["system"] = system_prompt
            
            response = requests.post(
                f"{self.config.base_url}/api/generate",
                json=payload,
                timeout=self.config.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                processing_time = time.time() - start_time
                
                return LLMResponse(
                    success=True,
                    content=data.get('response', ''),
                    processing_time=processing_time
                )
            else:
                # Try fallback model if primary fails
                if selected_model == self.config.model and hasattr(self.config, 'fallback_model'):
                    logger.warning(f"Primary model failed, trying fallback: {self.config.fallback_model}")
                    return self.generate_text_sync(prompt, system_prompt, self.config.fallback_model)
                
                return LLMResponse(
                    success=False,
                    content='',
                    error=f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Error generating text with {selected_model}: {e}")
            
            # Try fallback model if primary fails
            if selected_model == self.config.model and hasattr(self.config, 'fallback_model'):
                logger.warning(f"Primary model failed, trying fallback: {self.config.fallback_model}")
                return self.generate_text_sync(prompt, system_prompt, self.config.fallback_model)
            
            return LLMResponse(
                success=False,
                content='',
                error=str(e),
                processing_time=processing_time
            )

class TextEnhancementService:
    """Service for text enhancement using LLM"""
    
    def __init__(self, llm_service: OllamaLLMService = None):
        self.llm_service = llm_service or OllamaLLMService()
    
    def correct_grammar(self, text: str, language: str = "arabic") -> LLMResponse:
        """Correct grammar and improve text quality with enhanced Iraqi Arabic support"""
        
        if language.lower() == "arabic":
            # Enhanced Arabic system prompt with Iraqi dialect awareness
            system_prompt = """أنت خبير في تصحيح النصوص العربية والعامية العراقية. مهمتك:
1. تصحيح الأخطاء النحوية والإملائية
2. تحسين وضوح النص مع الحفاظ على المعنى الأصلي
3. الحفاظ على الكلمات العراقية الأصيلة مثل: شلونك، شكو ماكو، اكو، ماكو، وين، شنو، هسه، جان، يمعود
4. تطبيع الأحرف العراقية الخاصة (گ→ق، چ→ك، ژ→ز، پ→ب)
5. تحسين علامات الترقيم والتنسيق
6. إضافة التشكيل عند الضرورة للوضوح

احرص على الدقة والطبيعية في التصحيح."""
            
            prompt = f"""صحح النص التالي مع الحفاظ على اللهجة العراقية والمعنى الأصلي:

النص: {text}

النص المصحح:"""
        else:
            # English system prompt
            system_prompt = """You are an expert text editor. Your task is to:
1. Correct grammar and spelling errors
2. Improve clarity while preserving original meaning
3. Fix punctuation and formatting
4. Maintain the original tone and style

Be precise and natural in your corrections."""
            
            prompt = f"""Please correct the following text while preserving its original meaning and tone:

Text: {text}

Corrected text:"""
        
        return self.llm_service.generate_text_sync(prompt, system_prompt)
    
    def summarize_text(self, text: str, language: str = "ar", max_length: int = 200) -> LLMResponse:
        """Summarize text with enhanced Arabic dialect support"""
        
        if language.startswith("ar"):
            # Enhanced Arabic system prompt
            system_prompt = f"""أنت خبير في تلخيص النصوص العربية والعامية العراقية. مهمتك:
1. إنشاء ملخص واضح ومفيد في حدود {max_length} كلمة
2. الحفاظ على النقاط الرئيسية والمعلومات المهمة
3. استخدام لغة عربية واضحة ومفهومة
4. الحفاظ على السياق والمعنى الأصلي
5. تنظيم المعلومات بشكل منطقي ومتسلسل

اجعل الملخص شاملاً ومفيداً."""
            
            prompt = f"""لخص النص التالي بشكل واضح ومفيد:

النص: {text}

الملخص:"""
        else:
            # English system prompt
            system_prompt = f"""You are an expert text summarizer. Your task is to:
1. Create a clear and useful summary within {max_length} words
2. Preserve key points and important information
3. Use clear and understandable language
4. Maintain original context and meaning
5. Organize information logically

Make the summary comprehensive and useful."""
            
            prompt = f"""Please summarize the following text clearly and concisely:

Text: {text}

Summary:"""
        
        return self.llm_service.generate_text_sync(prompt, system_prompt)
    
    def translate_text(self, text: str, source_lang: str = "arabic", target_lang: str = "english") -> LLMResponse:
        """Translate text between languages"""
        if source_lang.lower() == "arabic" and target_lang.lower() == "english":
            system_prompt = "أنت مترجم محترف من العربية إلى الإنجليزية. قم بترجمة النص بدقة مع الحفاظ على المعنى."
            prompt = f"ترجم النص التالي من العربية إلى الإنجليزية:\n\n{text}"
        elif source_lang.lower() == "english" and target_lang.lower() == "arabic":
            system_prompt = "You are a professional translator from English to Arabic. Translate the text accurately while preserving the meaning."
            prompt = f"Translate the following text from English to Arabic:\n\n{text}"
        else:
            system_prompt = f"You are a professional translator. Translate the text from {source_lang} to {target_lang}."
            prompt = f"Translate the following text from {source_lang} to {target_lang}:\n\n{text}"
        
        return self.llm_service.generate_text_sync(prompt, system_prompt)
    
    def extract_keywords(self, text: str, language: str = "arabic", max_keywords: int = 10) -> LLMResponse:
        """Extract keywords from text"""
        if language.lower() == "arabic":
            system_prompt = f"أنت مساعد ذكي متخصص في استخراج الكلمات المفتاحية من النصوص العربية. استخرج أهم {max_keywords} كلمات مفتاحية."
            prompt = f"استخرج الكلمات المفتاحية من النص التالي:\n\n{text}"
        else:
            system_prompt = f"You are an AI assistant specialized in keyword extraction. Extract the top {max_keywords} keywords from the text."
            prompt = f"Extract keywords from the following text:\n\n{text}"
        
        return self.llm_service.generate_text_sync(prompt, system_prompt)

# Global service instances
llm_service = OllamaLLMService()
text_enhancement_service = TextEnhancementService(llm_service)

def test_llm_service():
    """Test function for LLM service"""
    print("Testing Ollama LLM Service...")
    
    # Check availability
    if not llm_service.is_available():
        print("❌ Ollama service is not available")
        return False
    
    print("✅ Ollama service is available")
    
    # Get available models
    models = llm_service.get_available_models()
    print(f"📋 Available models: {models}")
    
    # Test Arabic text generation
    test_text = "مرحبا بك في نظام التعرف على الكلام العربي"
    print(f"\n🧪 Testing with Arabic text: {test_text}")
    
    # Test grammar correction
    result = text_enhancement_service.correct_grammar(test_text)
    if result.success:
        print(f"✅ Grammar correction: {result.content}")
    else:
        print(f"❌ Grammar correction failed: {result.error}")
    
    # Test summarization
    long_text = "هذا نظام متقدم للتعرف على الكلام العربي يستخدم تقنيات الذكاء الاصطناعي الحديثة. يمكن للنظام تحويل الكلام المنطوق إلى نص مكتوب بدقة عالية. كما يدعم النظام ميزات متقدمة مثل تحديد المتحدثين وتحسين جودة الصوت."
    result = text_enhancement_service.summarize_text(long_text)
    if result.success:
        print(f"✅ Summarization: {result.content}")
    else:
        print(f"❌ Summarization failed: {result.error}")
    
    return True

if __name__ == "__main__":
    test_llm_service()