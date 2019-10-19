# RabbitMQ
RABBIT_HOST = 'localhost'
RABBIT_LOGIN = 'appeal_preparer'
RABBIT_PASSWORD = 'appeal_preparer'
RABBIT_ADDRESS = f'http://{RABBIT_LOGIN}:{RABBIT_PASSWORD}@localhost:15672'
RABBIT_EXCHANGE_APPEAL = 'appeal'
RABBIT_ROUTING_CAPTCHA_PIC = 'captcha_pic'
RABBIT_ROUTING_STATUS = 'appeal_status'
RABBIT_ROUTING_APPEAL_URL = 'appeal_url'

# appeal status codes
OK = 'ok'
FAIL = 'fail'
WRONG_INPUT = 'wrong_input'
CAPTCHA = 'captcha'

# message types
CAPTCHA = 'captcha'
APPEAL = 'appeal'

EMAILS = [
    'mail1@example.com',
    'mail2@example.com',
    'mail3@example.com',
    'mail4@example.com',
    'mail5@example.com',
    'mail6@example.com',
    'mail7@example.com',
    'mail8@example.com',
    'mail9@example.com',
]
