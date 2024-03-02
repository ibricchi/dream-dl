import os
import sys
import datetime

class Logger:
    @staticmethod
    def log(message):
        print(f'[{datetime.datetime.now()}] {message}')

    @staticmethod
    def error(message):
        Logger.log('ERROR: ' + message)