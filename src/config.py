import json
import logging
import os
import random
import pandas as pd
import dotenv
from selenium import webdriver

from src.types.student import Student
from src.utils import time_str_to_seconds

DEFAULT_CONFIG = {
    "student_csv_file": "students.csv",
    "max_messages": -1,
    "max_time": "1h",
    "min_delay": 15,
    "random_delay": 5,
    "max_timeout": 30,
    "max_retries": 5,
    "handshake_url": "https://app.joinhandshake.com/edu",
    "chromedriver_path": "chromedriver-win64",
    "message_subject": None,
    "chrome_data_dir": "%HOMEPATH%\\AppData\\Local\\Google\\Chrome\\User Data"
}

DEFAULT_ENV = "VAL1=\nVAL2=\nVAL3=\n"


class Config:
    def __init__(self):
        pass

    def load(self):
        self.load_env()
        self.load_config()
        self.load_students()
        self.load_message()
        self.load_selenium()

    def load_message(self):
        logging.info("loading message file")
        try:
            with open('message.txt') as msg:
                self.message = msg.read()
        except FileNotFoundError:
            with open('message.txt', 'w') as msg:
                msg.write("")
            message = "Created message.txt file. Please edit this file " \
                "with your desired message and run again."
            logging.info(message)
            print(message)
            exit(0)

    def load_env(self):
        if dotenv.load_dotenv():
            logging.info("Loaded environment variables from .env")
        else:
            with open('.env', 'w') as env:
                env.write(DEFAULT_ENV)
            message = "Created .env file with default values. " \
                "Please edit this file with your desired configuration " \
                "and run again."
            logging.info(message)
            print(message)

    def load_config(self):
        config = None
        try:
            with open('config.json') as cfg:
                config = json.load(cfg)
                logging.info("Loaded config.json")
        except FileNotFoundError:
            with open('config.json', 'w') as cfg:
                config = DEFAULT_CONFIG
                json.dump(config, cfg, indent=4)
                message = "Created config.json file with default values. " \
                    "Please edit this file with your desired configuration " \
                    "and run again."
                logging.info(message)
                print(message)
                exit(0)

        self.set_config(config)
        logging.info("Config variables initialized")

    def load_students(self):
        self.index = 0
        self.modified = []
        try:
            with open(self.student_csv_file) as students:
                self.students = pd.read_csv(students)
                logging.info(f"Found {len(self.students)} students in "
                             f"{self.student_csv_file}")
        except FileNotFoundError:
            message = f"Could not find file " \
                f"{self.student_csv_file}. " \
                f"Please ensure this is the correct filepath and try again."

            logging.error(message)
            print(message)
            exit(1)

    def load_selenium(self):
        logging.debug("Initializing Selenium...")
        # Set PATH environmental variable to chromedriver-win64

        os.environ["PATH"] += self.chromedriver_path
        logging.debug("Added environmental Path")

        chrome_options = webdriver.ChromeOptions()
        args = [
            "--start-minimized",
            "--headless=new",
            "--disable-popup-blocking",
            "enable-automation",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-browser-side-navigation",
            "--disable-gpu",
            "--disable-extensions"
        ]
        for arg in args:
            chrome_options.add_argument(arg)
        chrome_options.add_argument(f"user-data-dir={self.chrome_data_dir}")
        # Create a new instance of the Chrome driver
        self.webdriver = webdriver.Chrome(options=chrome_options)
        self.webdriver.set_page_load_timeout(self.max_timeout)

        logging.debug(f"Initialized new Chrome webdriver instance with the"
                      f"following arguments: [{', '.join(args)}]")
        logging.info("Chrome webdriver initialized")

    def reset_webdriver(self):
        self.webdriver.quit()
        self.load_selenium()

    def set_config(self, config):
        self.student_csv_file = self.get_config_val_of(
            config=config,
            key='student_csv_file'
        )
        self.max_messages = self.get_config_val_of(
            config=config,
            key='max_messages'
        )
        self.max_time = self.get_config_val_of(
            config=config,
            key='max_time'
        )
        self.min_delay = self.get_config_val_of(
            config=config,
            key='min_delay'
        )
        self.random_delay = self.get_config_val_of(
            config=config,
            key='random_delay'
        )
        self.max_timeout = self.get_config_val_of(
            config=config,
            key='max_timeout'
        )
        self.max_retries = self.get_config_val_of(
            config=config,
            key='max_retries'
        )
        self.handshake_url = self.get_config_val_of(
            config=config,
            key='handshake_url'
        )
        self.chromedriver_path = self.get_config_val_of(
            config=config,
            key='chromedriver_path'
        )
        self.message_subject = self.get_config_val_of(
            config=config,
            key='message_subject'
        )
        self.chrome_data_dir = self.get_config_val_of(
            config=config,
            key='chrome_data_dir'
        )

    def get_config_val_of(self, config, key):
        if key not in DEFAULT_CONFIG:
            logging.error(f"Invalid config key {key}. "
                          f"This key will be skipped.")
        if key not in config:
            logging.warning(f"Could not find {key} in "
                            f"config.json. Setting to default: "
                            f"{DEFAULT_CONFIG[key]}")
            config[key] = DEFAULT_CONFIG[key]
        return config[key]

    def has_next_student(self):
        return self.index < len(self.students)

    def get_next_student(self):
        if not self.has_next_student():
            return -1
        student = self.students[self.index]
        self.index += 1
        if student.student_id == -1:
            logging.debug(f"Skipping row {self.index} of "
                          f"{self.student_csv_file}")
            return self.get_next_student()
        logging.debug(f"Next student: {student} "
                      f"(row: {self.index})")
        return student

    def verify_student_id(self, student_id: str | int, row_index):
        if student_id is None:
            logging.warning(f"Student id {student_id} at row {row_index} "
                            f"of {self.student_csv_file} is None. "
                            f"This row will be skipped.")
            self.add_modified(student_id, "none", "skip")
            return -1
        if isinstance(student_id, str) and not student_id.isdigit():
            logging.warning(f"Student id {student_id} at row {row_index} "
                            f"of {self.student_csv_file} is not an integer. "
                            f"This row will be skipped.")
            self.add_modified(student_id, "not_int", "skip")
            return -1
        student_id = int(student_id)
        if student_id < 0:
            logging.warning(f"Student id {student_id} at row {row_index} "
                            f"of {self.student_csv_file} is negative. "
                            f"This row will be converted to positive.")
            self.add_modified(student_id, "negative", "abs")
            student_id = abs(student_id)
        if student_id > 99999999:
            logging.warning(f"Student id {student_id} at row {row_index} "
                            f"of {self.student_csv_file} is too large. "
                            f"This row will be skipped.")
            self.add_modified(student_id, "too_big", "skip")
        return student_id

    def add_modified(self, student_id, type, action="skip"):
        self.modified.append({
            "handshake_id": student_id,
            "row_index": self.index,
            "type": type,
            "action": action})

    def save_modified(self):
        if len(self.modified) == 0:
            return
        with open('modified.json', 'w') as mod:
            json.dump(self.modified, mod, indent=4)
        logging.info(f"Saved {len(self.modified)} modified students to {mod}")

    def get_rand_delay_time(self):
        delay = self.min_delay + random.randint(0, self.random_delay)
        logging.debug(f"Random delay time: {delay}s")
        return delay

    @property
    def index(self) -> int:
        return self._index

    @index.setter
    def index(self, val: int):
        if not isinstance(val, int):
            raise ValueError("index must be an integer")
        self._index = val

    @property
    def message(self) -> str:
        return self._message

    @message.setter
    def message(self, val: str):
        if not isinstance(val, str):
            raise ValueError("message must be a string")
        self._message = val

    @property
    def student_csv_file(self) -> str:
        return self._student_csv_file

    @student_csv_file.setter
    def student_csv_file(self, val: str):
        if not isinstance(val, str):
            raise ValueError("student_csv_file must be a string")
        self._student_csv_file = val

    @property
    def max_messages(self) -> int:
        return self._max_messages

    @max_messages.setter
    def max_messages(self, val: int):
        if not isinstance(val, int):
            raise ValueError("max_messages must be an integer")
        self._max_messages = val

    @property
    def max_time(self) -> int:
        return self._max_time

    @max_time.setter
    def max_time(self, val: str):
        if not isinstance(val, str):
            raise ValueError("max_time must be a string")
        if "h" not in val and "m" not in val and "s" not in val:
            raise ValueError("max_time must be in the format Xh, Xm, or Xs")
        self._max_time = time_str_to_seconds(val)

    @property
    def min_delay(self) -> int:
        return self._min_delay

    @min_delay.setter
    def min_delay(self, val: int):
        if not isinstance(val, int):
            raise ValueError("min_delay must be an integer")
        self._min_delay = val

    @property
    def random_delay(self) -> int:
        return self._random_delay

    @random_delay.setter
    def random_delay(self, val: int):
        if not isinstance(val, int):
            raise ValueError("random_delay must be an integer")
        self._random_delay = val

    @property
    def max_timeout(self) -> int:
        return self._max_timeout

    @max_timeout.setter
    def max_timeout(self, val: int):
        if not isinstance(val, int):
            raise ValueError("max_timeout must be an integer")
        self._max_timeout = val

    @property
    def max_retries(self) -> int:
        return self._max_retries

    @max_retries.setter
    def max_retries(self, val: int):
        if not isinstance(val, int):
            raise ValueError("max_retries must be an integer")
        self._max_retries = val

    @property
    def handshake_url(self) -> str:
        return self._handshake_url

    @handshake_url.setter
    def handshake_url(self, val: str):
        if not isinstance(val, str):
            raise ValueError("handshake_url must be a string")
        if "joinhandshake.com" not in val:
            raise ValueError("handshake_url must be a Handshake url")
        self._handshake_url = val

    @property
    def chromedriver_path(self) -> str:
        return self._chromedriver_path

    @chromedriver_path.setter
    def chromedriver_path(self, val: str):
        if not isinstance(val, str):
            raise ValueError("chromedriver_path must be a string")
        if not os.path.exists(val):
            raise ValueError("chromedriver_path must be a valid path")
        self._chromedriver_path = val

    @property
    def message_subject(self) -> str | None:
        return self._message_subject

    @message_subject.setter
    def message_subject(self, val: str | None):
        if not isinstance(val, str) and val is not None:
            raise ValueError("message_subject must be a string or None")
        self._message_subject = val

    @property
    def students(self) -> list[Student]:
        return self._students

    @students.setter
    def students(self, val: pd.DataFrame):
        self._students = []
        if not isinstance(val, pd.DataFrame):
            raise ValueError("students must be a pandas DataFrame")
        for row in range(len(val)):
            student_row = val.iloc[row]
            id = self.verify_student_id(student_row.get("handshake_id"), row)
            self._students.append(Student(
                student_id=id,
                data=student_row.to_dict()
            ))

    @property
    def modified(self) -> list[dict]:
        return self._modified

    @modified.setter
    def modified(self, val: list[dict]):
        if not isinstance(val, list):
            raise ValueError("modified must be a list")
        self._modified = val

    @property
    def chrome_data_dir(self) -> str:
        return self._chrome_data_dir

    @chrome_data_dir.setter
    def chrome_data_dir(self, val: str):
        if not isinstance(val, str):
            raise ValueError("chrome_data_dir must be a string")
        self._chrome_data_dir = val
