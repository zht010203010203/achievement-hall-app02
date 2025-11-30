"""AI鼓励服务"""
import time
import requests
from typing import Dict, Any, Optional, Callable
from datetime import datetime
from database.db_manager import DatabaseManager
from .study_service import StudyService
from config.settings import AI_REQUEST_TIMEOUT, AI_MAX_TOKENS, AI_TEMPERATURE
from config.constants import API_PLATFORMS, AI_TRIGGER_SCENARIOS


class AIService:
    """AI鼓励服务类"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.study_service = StudyService()
        self.last_request_time = None
    
    def generate_prompt(self, identity_id: int, trigger_scene: str, 
                       context: Dict[str, Any] = None, db: DatabaseManager = None) -> str:
        """
        生成AI提示词
        
        Args:
            identity_id: AI身份ID
            trigger_scene: 触发场景
            context: 上下文信息
            db: 数据库连接（可选，用于多线程）
            
        Returns:
            完整的提示词
        """
        # 使用传入的数据库连接或默认连接
        db_conn = db if db else self.db
        
        # 获取AI身份信息
        identities = db_conn.get_all_ai_identities()
        identity = next((i for i in identities if i['id'] == identity_id), None)
        
        if not identity:
            raise Exception("AI身份不存在")
        
        # 获取场景模板
        scene_info = AI_TRIGGER_SCENARIOS.get(trigger_scene, {})
        scene_template = scene_info.get('prompt_template', '')
        
        # 获取用户数据
        if context is None:
            context = {}
        
        # 如果传入了db，说明在子线程中，需要创建临时的StudyService
        if db:
            from .study_service import StudyService
            temp_study_service = StudyService(db=db)
            today_progress = temp_study_service.get_today_progress()
            total_count = temp_study_service.get_total_count()
            streak_days = temp_study_service.get_streak_days()
            level_info = temp_study_service.get_level_info()
        else:
            # 主线程直接使用
            today_progress = self.study_service.get_today_progress()
            total_count = self.study_service.get_total_count()
            streak_days = self.study_service.get_streak_days()
            level_info = self.study_service.get_level_info()
        
        # 构建完整提示词
        prompt = f"""
{identity['system_prompt']}

你的说话风格：{identity['tone_style']}

当前用户学习情况：
- 今日完成：{today_progress['current']}题 / 目标：{today_progress['target']}题
- 连续打卡：{streak_days}天
- 总进度：{total_count}题
- 当前等级：Level {level_info['level']} {level_info['title']}

触发场景：{scene_info.get('name', trigger_scene)}
{scene_template.format(**context) if context else ''}

请根据以上信息，以{identity['name']}的身份，用{identity['tone_style']}的语气，给用户一段50-80字左右的鼓励或建议。

【重要】输出格式要求：
1. 只输出最终的鼓励内容，不要输出任何思考过程、推理步骤或分析
2. 不要加"作为XXX"、"我认为"、"回复："等前缀
3. 直接以第一人称对用户说话
4. 语言要自然亲切，符合身份特点
5. 内容要具体，结合用户的实际数据
6. 适当使用emoji增加亲和力（1-2个即可）

示例格式：
"今天完成了XX题，进步很大哦！继续保持这个节奏~ 💪"
"""
        
        return prompt.strip()
    
    def call_ai_api(self, prompt: str, identity_id: int = None) -> str:
        """
        调用AI API
        
        Args:
            prompt: 提示词
            identity_id: AI身份ID（用于记录）
            
        Returns:
            AI生成的鼓励内容
        """
        start_time = time.time()
        
        # 获取API配置
        config = self.db.get_default_api_config()
        
        if not config:
            raise Exception("未配置API，请先在设置中配置API")
        
        platform_type = config['platform_type']
        
        # 根据平台类型调用
        if platform_type in ['openrouter', 'deepseek', 'volcengine']:
            response = self._call_openai_compatible(config, prompt)
        else:
            raise Exception(f"不支持的平台类型: {platform_type}")
        
        # 计算响应时间
        response_time = time.time() - start_time
        
        # 更新最后请求时间
        self.last_request_time = datetime.now()
        
        return response
    
    def _call_openai_compatible(self, config: Dict, prompt: str) -> str:
        """
        调用OpenAI兼容格式的API
        
        Args:
            config: API配置
            prompt: 提示词
            
        Returns:
            AI响应内容
        """
        headers = {
            'Authorization': f"Bearer {config['api_key']}",
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': config['model_id'],
            'messages': [
                {'role': 'user', 'content': prompt}
            ],
            'max_tokens': AI_MAX_TOKENS,
            'temperature': AI_TEMPERATURE
        }
        
        try:
            response = requests.post(
                f"{config['base_url']}/chat/completions",
                headers=headers,
                json=data,
                timeout=AI_REQUEST_TIMEOUT
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # 调试：打印完整响应
                print(f"[DEBUG] API完整响应: {result}")
                
                # 尝试获取content
                try:
                    message = result['choices'][0]['message']
                    content = ""
                    
                    # 优先获取普通content（绝大多数模型）
                    if 'content' in message and message['content']:
                        content = message['content']
                        print(f"[DEBUG] 从content提取到完整内容")
                    
                    # 如果没有content，检查是否是推理模型
                    if not content:
                        print(f"[DEBUG] content为空，检查其他字段")
                        print(f"[DEBUG] message keys: {list(message.keys())}")
                        
                        # DeepSeek推理模型特殊处理
                        # 推理模型会有reasoning_content（思考过程）和content（最终回复）
                        # 但有时content在tool_calls或其他字段
                        
                        # 尝试从reasoning_content中智能提取
                        if 'reasoning_content' in message and message['reasoning_content']:
                            reasoning = message['reasoning_content']
                            print(f"[DEBUG] 检测到推理内容（前200字）: {reasoning[:200]}")
                            
                            import re
                            
                            # 策略1：查找引号内的完整鼓励语（最准确）
                            # 匹配形如 "你好，..." 或 「你好，...」的内容
                            quote_patterns = [
                                r'["""]([^"""]{20,})["""]',  # 双引号，至少20字
                                r'「([^」]{20,})」',  # 日式引号
                                r'"([^"]{20,})"'  # 英文引号
                            ]
                            
                            for pattern in quote_patterns:
                                quotes = re.findall(pattern, reasoning, re.DOTALL)
                                if quotes:
                                    # 找最长的引号内容
                                    content = max(quotes, key=len).strip()
                                    # 验证：必须是完整句子（有结尾标点）
                                    if any(content.endswith(p) for p in ['。', '！', '？', '~', '啊', '呢', '吧', '哦']):
                                        print(f"[DEBUG] 从引号提取完整鼓励: {content[:50]}...")
                                        break
                                    else:
                                        content = ""  # 重置，继续尝试
                            
                            # 策略2：查找"最终回复："、"鼓励："等明确标记后的内容
                            if not content:
                                keywords = ['最终回复[：:]', '鼓励[：:]', '回复[：:]', '对.*?说[：:]']
                                for kw in keywords:
                                    match = re.search(kw + r'\s*["""]?([^"""]+?)["""]?\s*(?:\n|$)', reasoning, re.DOTALL)
                                    if match:
                                        candidate = match.group(1).strip()
                                        # 验证：不包含推理词汇
                                        if not any(word in candidate[:50] for word in ['比如', '思考', '调整', '不对', '策略', '应该']):
                                            content = candidate
                                            print(f"[DEBUG] 从标记词提取: {content[:50]}...")
                                            break
                            
                            # 策略3：专门提取报告格式（📊 数据回顾 + 💬 小伙伴想对你说）
                            if not content:
                                # 查找报告的两个部分
                                data_section = re.search(r'📊\s*数据回顾\s*\n+(.*?)(?=💬|$)', reasoning, re.DOTALL)
                                chat_section = re.search(r'💬\s*小伙伴想对你说\s*\n+(.*?)$', reasoning, re.DOTALL)
                                
                                if data_section and chat_section:
                                    data_text = data_section.group(1).strip()
                                    chat_text = chat_section.group(1).strip()
                                    content = f"📊 数据回顾\n\n{data_text}\n\n💬 小伙伴想对你说\n\n{chat_text}"
                                    print(f"[DEBUG] 提取报告格式: 成功")
                                elif data_section or chat_section:
                                    # 至少有一部分
                                    content = (data_section.group(0) if data_section else "") + "\n\n" + (chat_section.group(0) if chat_section else "")
                                    content = content.strip()
                                    print(f"[DEBUG] 提取报告格式: 部分成功")
                            
                            # 策略4：提取最后一个完整段落（不含推理词汇）
                            if not content:
                                paragraphs = [p.strip() for p in reasoning.split('\n\n') if p.strip()]
                                # 从后往前找，找第一个不含推理词汇的完整段落
                                for para in reversed(paragraphs):
                                    if (len(para) > 20 and 
                                        any(para.endswith(p) for p in ['。', '！', '？', '~']) and
                                        not any(word in para[:50] for word in ['比如', '思考', '调整', '不对', '策略', '应该', '分析'])):
                                        content = para
                                        print(f"[DEBUG] 提取纯净段落: {content[:50]}...")
                                        break
                            
                            # 如果以上都失败，说明这个模型不适合
                            if not content:
                                content = "⚠️ 抱歉，当前使用的推理模型返回格式异常。建议切换到普通对话模型（如deepseek-chat）以获得更好体验。"
                                print(f"[ERROR] 无法从推理内容中提取有效回复")
                                print(f"[DEBUG] reasoning全文: {reasoning}")
                        
                        # 如果连reasoning_content都没有
                        if not content:
                            content = "AI返回了空内容，请检查API配置或更换模型。"
                            print(f"[ERROR] message中完全没有有效内容")
                        
                except (KeyError, IndexError) as e:
                    print(f"[ERROR] 提取content失败: {e}")
                    print(f"[DEBUG] result结构: {result}")
                    content = "内容解析失败，请联系开发者。"
                
                return content.strip()
            else:
                raise Exception(f"API调用失败: {response.status_code} - {response.text}")
                
        except requests.Timeout:
            raise Exception("API请求超时，请检查网络连接")
        except requests.RequestException as e:
            raise Exception(f"网络请求失败: {str(e)}")
        except Exception as e:
            raise Exception(f"AI调用失败: {str(e)}")
    
    def request_encouragement(self, trigger_scene: str, identity_id: int = None,
                            context: Dict[str, Any] = None, 
                            user_mood: str = None) -> Dict[str, Any]:
        """
        请求AI鼓励（同步）
        
        Args:
            trigger_scene: 触发场景
            identity_id: AI身份ID，默认使用第一个
            context: 上下文信息
            user_mood: 用户心情
            
        Returns:
            包含鼓励内容和元信息的字典
        """
        # 获取默认身份
        if identity_id is None:
            identities = self.db.get_all_ai_identities()
            if not identities:
                raise Exception("没有可用的AI身份")
            identity_id = identities[0]['id']
        
        # 生成提示词
        prompt = self.generate_prompt(identity_id, trigger_scene, context)
        
        # 调用API
        start_time = time.time()
        content = self.call_ai_api(prompt, identity_id)
        response_time = time.time() - start_time
        
        # 保存记录
        encouragement_id = self.db.save_ai_encouragement(
            identity_id=identity_id,
            trigger_scene=trigger_scene,
            content=content,
            response_time=response_time,
            user_mood=user_mood
        )
        
        return {
            'id': encouragement_id,
            'content': content,
            'identity_id': identity_id,
            'trigger_scene': trigger_scene,
            'response_time': response_time,
            'created_at': datetime.now().isoformat()
        }
    
    def request_encouragement_async(self, trigger_scene: str, 
                                   callback: Callable[[Optional[Dict], Optional[str]], None],
                                   identity_id: int = None,
                                   context: Dict[str, Any] = None,
                                   user_mood: str = None):
        """
        异步请求AI鼓励
        
        Args:
            trigger_scene: 触发场景
            callback: 回调函数，参数为 (result, error)
            identity_id: AI身份ID
            context: 上下文信息
            user_mood: 用户心情
        """
        from threading import Thread
        from kivy.clock import Clock
        from database.db_manager import DatabaseManager
        
        def _thread_task():
            try:
                # 在子线程中创建新的数据库连接
                thread_db = DatabaseManager()
                
                # 获取默认身份
                if identity_id is None:
                    identities = thread_db.get_all_ai_identities()
                    if not identities:
                        raise Exception("没有可用的AI身份")
                    thread_identity_id = identities[0]['id']
                else:
                    thread_identity_id = identity_id
                
                # 生成提示词（传入子线程的数据库连接）
                prompt = self.generate_prompt(thread_identity_id, trigger_scene, context, db=thread_db)
                
                # 调用API（使用子线程的数据库连接获取配置）
                config = thread_db.get_default_api_config()
                if not config:
                    raise Exception("未配置API，请先在设置中配置API")
                
                # 补充默认的base_url和model_id（如果为空）
                from config.constants import API_PLATFORMS
                platform_defaults = API_PLATFORMS.get(config['platform_type'], {})
                if not config.get('base_url'):
                    config['base_url'] = platform_defaults.get('base_url', '')
                if not config.get('model_id'):
                    default_models = platform_defaults.get('models', [])
                    config['model_id'] = default_models[0] if default_models else 'gpt-3.5-turbo'
                
                start_time = time.time()
                content = self._call_openai_compatible(config, prompt)
                response_time = time.time() - start_time
                
                # 调试：打印AI返回的内容
                print(f"[DEBUG] AI返回内容长度: {len(content)}")
                print(f"[DEBUG] AI返回内容: {content[:100]}...")
                
                # 在主线程保存记录（通过Clock调度）
                def save_to_db(dt):
                    try:
                        print(f"[DEBUG] 准备保存到数据库: content长度={len(content)}")
                        encouragement_id = self.db.save_ai_encouragement(
                            identity_id=thread_identity_id,
                            trigger_scene=trigger_scene,
                            content=content,
                            response_time=response_time,
                            user_mood=user_mood
                        )
                        print(f"[DEBUG] 保存成功: ID={encouragement_id}")
                        
                        result = {
                            'id': encouragement_id,
                            'content': content,
                            'identity_id': thread_identity_id,
                            'trigger_scene': trigger_scene,
                            'response_time': response_time,
                            'created_at': datetime.now().isoformat()
                        }
                        callback(result, None)
                    except Exception as e:
                        callback(None, str(e))
                
                Clock.schedule_once(save_to_db, 0)
                
                # 关闭子线程的数据库连接
                thread_db.close()
                
            except Exception as e:
                # 错误回调
                error_msg = str(e)
                Clock.schedule_once(lambda dt: callback(None, error_msg), 0)
        
        # 启动后台线程
        thread = Thread(target=_thread_task)
        thread.daemon = True
        thread.start()
    
    def check_trigger_conditions(self, event_type: str, event_data: Dict = None) -> Optional[str]:
        """
        检查是否应该触发AI鼓励
        
        Args:
            event_type: 事件类型
            event_data: 事件数据
            
        Returns:
            触发场景名称，如果不应触发则返回None
        """
        from config.settings import AI_MIN_INTERVAL
        
        # 检查时间间隔
        if self.last_request_time:
            elapsed = (datetime.now() - self.last_request_time).total_seconds()
            if elapsed < AI_MIN_INTERVAL:
                return None  # 间隔太短，不触发
        
        # 根据事件类型判断
        if event_type == 'daily_goal_complete':
            today_progress = self.study_service.get_today_progress()
            if today_progress['current'] >= today_progress['target']:
                return 'daily_goal_complete'
        
        elif event_type == 'achievement_unlock':
            return 'achievement_unlock'
        
        elif event_type == 'streak_milestone':
            streak_days = self.study_service.get_streak_days()
            if streak_days in [7, 30, 100]:  # 里程碑天数
                return 'streak_milestone'
        
        elif event_type == 'big_progress':
            if event_data and event_data.get('count', 0) >= 50:
                return 'big_progress'
        
        elif event_type == 'comeback':
            days_since = self.study_service.get_days_since_last_study()
            if days_since >= 3:  # 3天未学习
                return 'comeback'
        
        elif event_type == 'manual_request':
            return 'manual_request'
        
        return None
    
    def get_encouragement_history(self, limit: int = 50) -> list:
        """获取AI鼓励历史"""
        return self.db.get_ai_encouragement_history(limit)
    
    def get_active_identity(self) -> Optional[Dict]:
        """获取当前激活的AI身份"""
        # 这里简化处理，返回第一个身份
        # 实际应该有一个"当前选中"的设置
        identities = self.db.get_all_ai_identities()
        return identities[0] if identities else None
    
    def test_api_connection(self, platform_type: str, api_key: str, 
                           base_url: str, model_id: str) -> Dict[str, Any]:
        """
        测试API连接
        
        Args:
            platform_type: 平台类型
            api_key: API密钥
            base_url: API基础URL
            model_id: 模型ID
            
        Returns:
            测试结果
        """
        test_config = {
            'platform_type': platform_type,
            'api_key': api_key,
            'base_url': base_url,
            'model_id': model_id
        }
        
        test_prompt = "请回复：连接成功"
        
        try:
            start_time = time.time()
            response = self._call_openai_compatible(test_config, test_prompt)
            response_time = time.time() - start_time
            
            return {
                'success': True,
                'message': '连接成功',
                'response': response,
                'response_time': round(response_time, 2)
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': str(e),
                'response': None,
                'response_time': 0
            }
