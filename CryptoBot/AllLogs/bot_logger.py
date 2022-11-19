import logging
import pathlib
from datetime import datetime

from aiogram import loggers


class BotLogger:
    infolog = None

    def __init__(self):
        today_for_log = datetime.now().strftime('%Y-%m-%d')
        pathlib.Path('AllLogs/bot_logs/').mkdir(parents=True, exist_ok=True)
        self.infolog = loggers.event
        self.infolog.setLevel(logging.INFO)
        self.infolog.addHandler(logging.FileHandler(filename=f"AllLogs/bot_logs/{today_for_log}.log", mode='a'))
        self.infolog.addHandler(logging.StreamHandler())

        self.infolog.info('Logger is ready!')
