import json
import logging
import os
import pandas as pd
import dotenv
from selenium import webdriver

from src.types.student import Student

DEFAULT_CONFIG = {
    "student_csv_file": "students.csv",
    "max_messages": -1,
    "max_time": "1h",
    "min_delay": 15,
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
        except FileNotFoundError:
            message = f"Could not find file " \
                f"{self.student_csv_file}. " \
                f"Please ensure this is the correct filepath and try again."

            logging.error(message)
            print(message)
            exit(1)

        self.verify_students()

    def load_selenium(self):
        logging.debug("Initializing Selenium...")
        # Set PATH environmental variable to chromedriver-win64

        os.environ["PATH"] += self.chromedriver_path
        logging.debug("Added environmental Path")

        chrome_options = webdriver.ChromeOptions()
        # args = ["--start-minimized", "--headless=new", "--disable-popup-blocking"]
        args = ["--disable-popup-blocking"]
        for arg in args:
            chrome_options.add_argument(arg)
        # Create a new instance of the Chrome driver
        self.webdriver = webdriver.Chrome(options=chrome_options)

        logging.debug(f"Initialized new Chrome webdriver instance with the"
                      f"following arguments: [{', '.join(args)}]")
        logging.info("Chrome webdriver initialized")

    def set_config(self, config):

        if 'student_csv_file' not in config:
            logging.warning(f"Could not find student_csv_file in "
                            f"config.json. Setting to default: "
                            f"{DEFAULT_CONFIG['student_csv_file']}")
            config['student_csv_file'] = DEFAULT_CONFIG['student_csv_file']
        if 'max_messages' not in config:
            logging.warning(f"Could not find max_messages in "
                            f"config.json. Setting to default: "
                            f"{DEFAULT_CONFIG['max_messages']}")
            config['max_messages'] = DEFAULT_CONFIG['max_messages']
        if 'max_time' not in config:
            logging.warning(f"Could not find max_time in "
                            f"config.json. Setting to default: "
                            f"{DEFAULT_CONFIG['max_time']}")
            config['max_time'] = DEFAULT_CONFIG['max_time']
        if 'min_delay' not in config:
            logging.warning(f"Could not find min_delay in "
                            f"config.json. Setting to default: "
                            f"{DEFAULT_CONFIG['min_delay']}")
            config['min_delay'] = DEFAULT_CONFIG['min_delay']
        if 'max_timeout' not in config:
            logging.warning(f"Could not find max_timeout in "
                            f"config.json. Setting to default: "
                            f"{DEFAULT_CONFIG['max_timeout']}")
            config['max_timeout'] = DEFAULT_CONFIG['max_timeout']
        if 'max_retries' not in config:
            logging.warning(f"Could not find max_retries in "
                            f"config.json. Setting to default: "
                            f"{DEFAULT_CONFIG['max_retries']}")
            config['max_retries'] = DEFAULT_CONFIG['max_retries']
        if 'handshake_url' not in config:
            logging.warning(f"Could not find handshake_url in "
                            f"config.json. Setting to default: "
                            f"{DEFAULT_CONFIG['handshake_url']}")
            config['handshake_url'] = DEFAULT_CONFIG['handshake_url']
        if 'chromedriver_path' not in config:
            logging.warning(f"Could not find chromedriver_path in "
                            f"config.json. Setting to default: "
                            f"{DEFAULT_CONFIG['chromedriver_path']}")
            config['chromedriver_path'] = DEFAULT_CONFIG['chromedriver_path']
        if 'message_subject' not in config or config['message_subject'] == "":
            logging.warning(f"Could not find message_subject in "
                            f"config.json. Setting to default: "
                            f"{DEFAULT_CONFIG['message_subject']}")
            config['message_subject'] = DEFAULT_CONFIG['message_subject']
        if 'chrome_data_dir' not in config or config['chrome_data_dir'] == "":
            logging.warning(f"Could not find chrome_data_dir in "
                            f"config.json. Setting to default: "
                            f"{DEFAULT_CONFIG['chrome_data_dir']}")
            config['chrome_data_dir'] = DEFAULT_CONFIG['chrome_data_dir']

        self.student_csv_file = config['student_csv_file']
        self.max_messages = config['max_messages']
        self.max_time = config['max_time']
        self.min_delay = config['min_delay']
        self.max_timeout = config['max_timeout']
        self.max_retries = config['max_retries']
        self.handshake_url = config['handshake_url']
        self.chromedriver_path = config['chromedriver_path']
        self.message_subject = config['message_subject']
        self.chrome_data_dir = config['chrome_data_dir']

    def verify_students(self):
        if 'handshake_id' not in self.students.columns:
            message = f"Could not find column 'handshake_id' in " \
                f"{self.student_csv_file}. " \
                f"Please ensure this column exists and try again."
            logging.error(message)
            print(message)
            exit(1)
        logging.info(f"Found {len(self.students)} students in "
                     f"{self.student_csv_file}")

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
            logging.warn(f"Student id {student_id} at row {row_index} "
                         f"of {self.student_csv_file} is None. "
                         f"This row will be skipped.")
            self.add_modified(student_id, "none", "skip")
            return -1
        if isinstance(student_id, str) and not student_id.isdigit():
            logging.warn(f"Student id {student_id} at row {row_index} "
                         f"of {self.student_csv_file} is not an integer. "
                         f"This row will be skipped.")
            self.add_modified(student_id, "not_int", "skip")
            return -1
        student_id = int(student_id)
        if student_id < 0:
            logging.warn(f"Student id {student_id} at row {row_index} "
                         f"of {self.student_csv_file} is negative. "
                         f"This row will be converted to positive.")
            self.add_modified(student_id, "negative", "abs")
            student_id = abs(student_id)
        if student_id > 99999999:
            logging.warn(f"Student id {student_id} at row {row_index} "
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
        if "h" not in val and "m" not in val:
            raise ValueError("max_time must be in the format 1h or 1m")
        if "m" in val:
            vals = val.split("m")
            self._max_time = int(vals[0]) * 60
        else:
            vals = val.split("h")
            self._max_time = int(vals[0]) * 3600

    @property
    def min_delay(self) -> int:
        return self._min_delay

    @min_delay.setter
    def min_delay(self, val: int):
        if not isinstance(val, int):
            raise ValueError("min_delay must be an integer")
        self._min_delay = val

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
