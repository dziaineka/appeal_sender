from applicant.exceptions import *
from exceptions import *
import logging
import json

import pika

from applicant import Applicant
import config
from rabbit import Rabbit


class Preparer:
    def __init__(self, email: str) -> None:
        self.logger = self.setup_logging()
        self.applicant = Applicant(self.logger, address=email)
        self.queue = Rabbit()
        self.queue_name = email

    def start(self):
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=config.RABBIT_HOST,
                credentials=pika.credentials.PlainCredentials(
                    config.RABBIT_LOGIN,
                    config.RABBIT_PASSWORD),
                connection_attempts=10,
                retry_delay=2))

        channel = connection.channel()

        channel.queue_declare(queue=self.queue_name,
                              durable=True,
                              auto_delete=False)

        channel.queue_bind(queue=self.queue_name,
                           exchange=config.RABBIT_EXCHANGE_APPEAL,
                           routing_key=self.queue_name)

        channel.basic_qos(prefetch_count=1)

        channel.basic_consume(queue=self.queue_name,
                              on_message_callback=self.callback)

        self.queue.send_queue_name(self.queue_name)
        self.logger.info(' [*] Waiting for messages. To exit press CTRL+C')
        channel.start_consuming()

    def setup_logging(self):
        # create logger
        my_logger = logging.getLogger('appeal_preparer')
        my_logger.setLevel(logging.DEBUG)

        # create console handler with a higher log level
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)

        # create formatter and add it to the handlers
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)

        # add the handlers to the logger
        my_logger.addHandler(ch)

        return my_logger

    def process_captcha(self,
                        captcha_text: str,
                        user_id: int,
                        appeal_id: int) -> None:
        if self.applicant.enter_captcha_and_submit(captcha_text) != config.OK:
            raise CaptchaInputError()

        self.queue.send_status(user_id,
                               config.CAPTCHA_OK,
                               self.queue_name,
                               appeal_id)

    def process_appeal(self, method, data: dict) -> None:
        url = self.applicant.get_appeal_url(self.queue_name)
        status_code, message = self.applicant.send_appeal(data['appeal'], url)

        if status_code != config.OK:
            raise ErrorWhileSending(message)

        self.queue.send_status(data['user_id'],
                               status_code,
                               self.queue_name,
                               data['appeal_id'],
                               message)

        self.queue.send_queue_name(self.queue_name)

    def send_captcha(self, appeal_id: int, user_id: int) -> None:
        self.current_captcha_url = self.put_capcha_to_queue(appeal_id, user_id)

    def callback(self, ch, method, properties, body: str) -> None:
        data = json.loads(body)
        self.logger.info(" [x] Received %r" % data)

        try:
            if data['type'] == config.APPEAL:
                self.process_appeal(method, data)
            elif data['type'] == config.CAPTCHA_TEXT:
                self.process_captcha(data['captcha_text'],
                                     data['user_id'],
                                     data['appeal_id'])
            elif data['type'] == config.GET_CAPTCHA:
                self.send_captcha(data['appeal_id'], data['user_id'])
            elif data['type'] == config.CANCEL:
                self.logger.info("Отмена")
                self.applicant.cancel()
                self.queue.send_queue_name(self.queue_name)
        except CaptchaInputError:
            self.logger.info("Фейл капчи")
            self.send_captcha(data['appeal_id'], data['user_id'])
        except NoMessageFromPolice:
            self.logger.info("Фейл почты")
            self.send_captcha(data['appeal_id'], data['user_id'])
        except ErrorWhileSending:
            self.logger.info("Фейл почты")
            self.send_captcha(data['appeal_id'], data['user_id'])

        ch.basic_ack(delivery_tag=method.delivery_tag)
        self.logger.info(' [*] Waiting for messages. To exit press CTRL+C')

    def put_capcha_to_queue(self, appeal_id: int, user_id: int) -> str:
        url = self.applicant.get_captcha()
        self.queue.send_captcha_url(url, appeal_id, user_id)
        return url


def start(email: str):
    try:
        preparer = Preparer(email)
        preparer.start()
    except:
        print('Some fail')
        start(email)
