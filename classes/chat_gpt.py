import os
import openai
import httpx


class ChatGPT:
    _instance = None

    def __new__(cls, *args, **kwargs):
        '''Гарантирует, что будет создан только один экземпляр класса.'''
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            return cls._instance

    def __init__(self):
        self._gpt_token = os.getenv('GPT_TOKEN')
        self._proxy = os.getenv('PROXY_GPT')
        self._client = self._create_client()

    def _create_client(self):
        gpt_client = openai.AsyncOpenAI(
            api_key=self._gpt_token,
            http_client=httpx.AsyncClient(
                proxy=self._proxy
            )
        )
        return gpt_client

    @staticmethod
    def _load_prompt(prompt_name: str) -> str:
        '''Загружает промпт из файла.
        Если файла нет — возвращается имя промпта как строка (резервный вариант).'''
        prompt_path = os.path.join('resources', 'prompts', f'{prompt_name}.txt')
        if os.path.isfile(prompt_path):
            with open(prompt_path, 'r', encoding='UTF-8') as file:
                prompt = file.read()
        else:
            prompt = prompt_name
        return prompt

    def _init_message(self, prompt_name: str) -> dict[str, str | list[dict[str, str]]]:
        ''' Формирует начальное сообщение для GPT.
        Включает системное сообщение из промпта и модель GPT.'''

        return {'messages': [
            {'role': 'system',
             'content': self._load_prompt(prompt_name),
             }
        ],
            'model': 'gpt-3.5-turbo',
        }

    async def random_request(self) -> str:
        '''Запрашивает случайный факт.
        Использует промпт из файла random.txt.'''

        response = await self._client.chat.completions.create(
            **self._init_message('random'),
        )
        return response.choices[0].message.content

    async def gpt_request(self, request_text: str) -> str:
        '''Отвечает на произвольный пользовательский запрос.
        Использует промпт gpt.txt.'''

        key_args = self._init_message('gpt')
        key_args['messages'].append({'role': 'user', 'content': request_text})
        response = await self._client.chat.completions.create(
            **key_args,
        )
        return response.choices[0].message.content

    async def celebrity_request(self, prompt: str, history) -> str:
        '''Диалог с "знаменитостью".
        Передаётся контекст (имя знаменитости) и история диалога.'''

        key_args = self._init_message(prompt)
        for hist in history:
            key_args['messages'].append(hist)
        response = await self._client.chat.completions.create(
            **key_args,
        )
        return response.choices[0].message.content

