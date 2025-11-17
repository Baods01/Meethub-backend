TORTOISE_ORM = {
            'connections': {
                'default': {
                    'engine': 'tortoise.backends.mysql',
                    'credentials': {
                        'host': '127.0.0.1',
                        'port': '3306',
                        'user':'root',
                        'password':'123456',
                        'database':'meethub_db',
                        'minsize': 1,
                        'maxsize': 5,
                        'charset':'utf8mb4',
                        'echo': True,
                    }
                },
            },
            'apps': {
                'models': {
                    'models': [
                        'models.users',
                        'models.roles',
                        'aerich.models',
                        'models.activities',
                        'models.registrations',
                        'models.user_logs'
                        ],
                    'default_connection': 'default',
                }
            },
            'use_tz': False,
            'timezone': 'Asia/Shanghai'
}

# ============ Coze AI 配置 ============
COZE_CONFIG = {
    'bot_id': '7569792114469879835',
    'workflow_id': '7569792648278589466',
    'api_token': 'pat_54iXVjcHOk65KPjZSNUgoC2GXlvlsqcSbvA3hFZiZldxEGZMcoTB5MtYBYeUgToW',
    'api_base_url': 'https://api.coze.cn/v3',
    'timeout': 30,  # 请求超时时间（秒）
}