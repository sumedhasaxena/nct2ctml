"""
LLM Platform classes for different AI service providers.
Each platform class encapsulates its specific configuration, request/response handling.
"""
import json
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from loguru import logger


class LLMPlatform(ABC):
    """Base class for LLM platforms."""
    
    def __init__(self, model: str, hostname: str):
        self.model = model
        self.hostname = hostname
    
    @property
    @abstractmethod
    def port(self) -> int:
        """Return the port number for this platform."""
        pass
    
    @property
    @abstractmethod
    def chat_endpoint(self) -> str:
        """Return the chat endpoint path for this platform."""
        pass
    
    @abstractmethod
    def get_request_body(self, prompt: str, json_schema: Optional[Dict] = None) -> Dict[str, Any]:
        """Generate the request body for this platform."""
        pass
    
    @abstractmethod
    def parse_response(self, ai_response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse the response from this platform."""
        pass
    
    def get_endpoint_url(self) -> str:
        """Get the full endpoint URL."""
        import urllib.parse
        return urllib.parse.urljoin(f"{self.hostname}:{self.port}", self.chat_endpoint)


class SGLangPlatform(LLMPlatform):
    """SGLang platform implementation."""
    
    def __init__(self, model: str, hostname: str):
        super().__init__(model, hostname)
        self._port = 30000
    
    @property
    def port(self) -> int:
        return self._port
    
    @property
    def chat_endpoint(self) -> str:
        return "v1/chat/completions"
    
    def get_request_body(self, prompt: str, json_schema: Optional[Dict] = None) -> Dict[str, Any]:
        """Generate SGLang request body."""
        req_body = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a biomedical researcher."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.5,
            "max_tokens": 8192,
            "response_format": {
                "type": "json_object"
            },
            "stream": False
        }
        return req_body
    
    def parse_response(self, ai_response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse SGLang response."""
        response_dict = {}
        try:
            if type(ai_response) is dict and 'choices' in ai_response.keys() and type(ai_response['choices']) is list:
                answer = ai_response['choices'][0]
                ai_response_content = self._safe_get(answer, ['message', 'content'])
                if ai_response_content:
                    prefix_pos = ai_response_content.find('```json')  # look for ```json in response string
                    if prefix_pos > -1:
                        begin_content = ai_response_content.find('```json') + len('```json')
                        end_content = ai_response_content.find('```', begin_content)
                        response_string = ai_response_content[begin_content:end_content].strip()
                    else:
                        prefix_pos = ai_response_content.find('</think>')  # else get everything after </think>
                        if prefix_pos > -1:
                            begin_content = ai_response_content.find('</think>') + len('</think>')
                            response_string = ai_response_content[begin_content:].strip()
                        else:
                            response_string = ai_response_content
                    
                    response_dict = json.loads(response_string)
        except json.JSONDecodeError as ex:
            logger.error(f"Unexpected response format: {ex=}, {type(ex)=}")
        return response_dict
    
    def _safe_get(self, dict_data, keys):
        """Helper method to safely get nested dictionary values."""
        for key in keys:
            dict_data = dict_data.get(key, {})
        return dict_data


class VLLMPlatform(SGLangPlatform):
    """vLLM platform implementation (uses same format as SGLang)."""
    
    def __init__(self, model: str, hostname: str):
        super().__init__(model, hostname)
        self._port = 8000
    
    @property
    def chat_endpoint(self) -> str:
        return "v1/chat/completions"


class OllamaPlatform(LLMPlatform):
    """Ollama platform implementation."""
    
    def __init__(self, model: str, hostname: str):
        super().__init__(model, hostname)
        self._port = 11434
    
    @property
    def port(self) -> int:
        return self._port
    
    @property
    def chat_endpoint(self) -> str:
        #return "api/generate"
        return "api/chat"

    def _safe_get(self, dict_data, keys):
        for key in keys:
            dict_data = dict_data.get(key, {})
        return dict_data

    def get_request_body(self, prompt: str, json_schema: Optional[Dict] = None) -> Dict[str, Any]:

        if self.chat_endpoint == "api/generate":
            req_body = {
            "model": self.model,
            "prompt": prompt,
            "system": "You are a biomedical researcher specializing in cancer genomics and clinical trials.",
            "stream": False,
            "options": {
                "think": True,
                "temperature": 0,
                "seed": 42,
                "top_k": 1
            }
        }
        elif self.chat_endpoint == "api/chat":
            req_body = {
                "model": self.model,            
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a biomedical researcher specializing in cancer genomics and clinical trials."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "stream": False,
                "options": {
                    "think": True,
                    "temperature": 0,
                    "seed": 42,
                    "top_k": 1
                }
            }

        if json_schema is not None:
            req_body["format"] = json_schema
        else:
            req_body["format"] = "json"
        
        return req_body
    
    def parse_response(self, ai_response: Dict[str, Any]) -> Dict[str, Any]:
        
        response_dict = {}
        if self.chat_endpoint == "api/generate":
            try:
                if type(ai_response) is dict and 'response' in ai_response.keys():
                    ai_response_content = ai_response['response']
                    response_dict = json.loads(ai_response_content)
            except json.JSONDecodeError as ex:
                logger.error(f"Unexpected response format: {ex=}, {type(ex)=}")
        
        elif self.chat_endpoint == "api/chat":
            try:
                if type(ai_response) is dict and 'message' in ai_response.keys():
                    ai_response_content = self._safe_get(ai_response, ['message', 'content'])
                    response_dict = json.loads(ai_response_content)
            except json.JSONDecodeError as ex:
                logger.error(f"Unexpected response format: {ex=}, {type(ex)=}")
        return response_dict


class LocalAIPlatform(LLMPlatform):
    """Local AI platform implementation (not yet configured)."""
    
    def __init__(self, model: str, hostname: str):
        super().__init__(model, hostname)
        self._port = 49152
    
    @property
    def port(self) -> int:
        return self._port
    
    @property
    def chat_endpoint(self) -> str:
        return "chat/completions"
    
    def get_request_body(self, prompt: str, json_schema: Optional[Dict] = None) -> Dict[str, Any]:
        """Generate Local AI request body."""
        raise NotImplementedError("Local_ai platform is not configured yet.")
    
    def parse_response(self, ai_response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Local AI response."""
        raise NotImplementedError("Local_ai platform is not configured yet.")


def create_llm_platform(platform_name: str, model: str, hostname: str) -> LLMPlatform:
    """
    Function to create an LLM platform instance based on platform name.    
    """
    platform_name_lower = platform_name.lower()
    
    if platform_name_lower == "sglang":
        return SGLangPlatform(model, hostname)
    elif platform_name_lower == "ollama":
        return OllamaPlatform(model, hostname)
    elif platform_name_lower == "vllm":
        return VLLMPlatform(model, hostname)
    elif platform_name_lower == "local_ai":
        return LocalAIPlatform(model, hostname)
    else:
        raise ValueError(f"Unsupported LLM platform: {platform_name}")

