import os
from openai import OpenAI
from typing import List, Dict, Optional, Any

# 尝试加载.env文件
try:
    from dotenv import load_dotenv
    # 查找.env文件（可能在当前目录或上级目录）
    env_paths = [
        os.path.join(os.path.dirname(__file__), '.env'),  # llm目录下的.env
        os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'),  # backend目录下的.env
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env'),  # 项目根目录下的.env
    ]
    
    for env_path in env_paths:
        if os.path.exists(env_path):
            load_dotenv(env_path)
            break
except ImportError:
    # 如果没有安装python-dotenv，就跳过
    pass


class QwenLLM:
    """通义千问大模型调用封装类"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "qwen-plus"):
        """
        初始化QwenLLM
        
        Args:
            api_key: API密钥，如果不提供则从环境变量DASHSCOPE_API_KEY获取
            model: 模型名称，默认为qwen-plus
        """
        self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY")
        if not self.api_key:
            raise ValueError("API密钥未提供，请设置DASHSCOPE_API_KEY环境变量或传入api_key参数")
        
        self.model = model
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
    
    def chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        enable_thinking: Optional[bool] = None
    ) -> Any:
        """
        调用通义千问进行对话补全
        
        Args:
            messages: 消息列表，格式为[{"role": "user", "content": "你好"}]
            temperature: 温度参数，控制输出的随机性，默认0.7
            max_tokens: 最大输出token数
            stream: 是否使用流式输出
            enable_thinking: 是否启用思考过程（Qwen3模型特有）
            
        Returns:
            模型响应结果
        """
        try:
            # 构建请求参数
            params = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "stream": stream
            }
            
            if max_tokens:
                params["max_tokens"] = max_tokens
            
            # 添加Qwen3特有的参数
            if enable_thinking is not None:
                params["extra_body"] = {"enable_thinking": enable_thinking}
            
            # 调用API
            completion = self.client.chat.completions.create(**params)
            
            return completion
            
        except Exception as e:
            raise Exception(f"调用通义千问API失败: {str(e)}")
    
    def simple_chat(self, user_message: str, system_message: str = "You are a helpful assistant.") -> str:
        """
        简单的对话方法
        
        Args:
            user_message: 用户消息
            system_message: 系统消息，默认为"You are a helpful assistant."
            
        Returns:
            模型回复的文本内容
        """
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
        
        response = self.chat_completion(messages)
        return response.choices[0].message.content
    
    def batch_chat(self, conversations: List[Dict[str, str]], system_message: str = "You are a helpful assistant.") -> List[str]:
        """
        批量对话方法
        
        Args:
            conversations: 对话列表，每个元素包含user_message
            system_message: 系统消息
            
        Returns:
            回复列表
        """
        results = []
        for conv in conversations:
            user_message = conv.get("user_message", "")
            if user_message:
                response = self.simple_chat(user_message, system_message)
                results.append(response)
        
        return results


# 使用示例
if __name__ == "__main__":
    # 创建LLM实例
    llm = QwenLLM()
    
    # 简单对话
    response = llm.simple_chat("你是谁？")
    print(f"回复: {response}")
    
    # 使用chat_completion方法
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "请介绍一下Python编程语言"}
    ]
    
    completion = llm.chat_completion(messages, temperature=0.5)
    print(f"完整响应: {completion.model_dump_json()}")