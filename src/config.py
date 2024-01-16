import json
import logging
import pandas as pd
import dotenv

DEFAULT_CONFIG = {
    "student_csv_file": "students.csv",
    "max_messages": -1,
    "max_time": "1h",
    "min_delay": 15,
    "max_timeout": 30,
    "max_retries": 5,
    "handshake_url": "https://app.joinhandshake.com/edu"
}

DEFAULT_ENV = "VAL1=\nVAL2=\nVAL3=\n"


class Config:
    def __init__(self):
        pass

    def load(self):

        # Load environment variables
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

        # Open the config file
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

        # Open the student csv file
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

        self.index = 0
        self.modified = []

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
        self.student_csv_file = config['student_csv_file']
        self.max_messages = config['max_messages']
        self.max_time = config['max_time']
        self.min_delay = config['min_delay']
        self.max_timeout = config['max_timeout']
        self.max_retries = config['max_retries']
        self.handshake_url = config['handshake_url']

    def verify_students(self):
        if 'id' not in self.students.columns:
            message = f"Could not find column 'id' in " \
                f"{self.config['student_csv_file']}. " \
                f"Please ensure this column exists and try again."
            logging.error(message)
            print(message)
            exit(1)
        logging.info(f"Found {len(self.students)} students in "
                     f"{self.config['student_csv_file']}")

    def get_next_student(self):
        if self.index >= len(self.students):
            return -1
        id = self.verify_student_id(self.students.iloc[self.index]['id'])
        self.index += 1
        if id == -1:
            logging.debug(f"Skipping row {self.index} of "
                          f"{self.student_csv_file}")
            return self.get_next_student()
        logging.debug(f"Next student: {id} (row: {self.index})")
        return id

    def verify_student_id(self, student_id):
        if not isinstance(student_id, int):
            logging.warn(f"Student id {student_id} at row {self.index} "
                         f"of {self.student_csv_file} is not an integer. "
                         f"This row will be skipped.")
            self.add_modified(student_id, "not_int", "skip")
            return -1
        if student_id < 0:
            logging.warn(f"Student id {student_id} at row {self.index} "
                         f"of {self.student_csv_file} is negative. "
                         f"This row will be converted to positive.")
            self.add_modified(student_id, "negative", "abs")
            student_id = abs(student_id)
        if student_id > 9999999:
            logging.warn(f"Student id {student_id} at row {self.index} "
                         f"of {self.student_csv_file} is too large. "
                         f"This row will be skipped.")
            self.add_modified(student_id, "too_big", "skip")
        return student_id

    def add_modified(self, student_id, type, action="skip"):
        self.modified.append({
            "id": student_id,
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
    def student_csv_file(self) -> str:
        return self.student_csv_file

    @student_csv_file.setter
    def student_csv_file(self, val: str):
        if not isinstance(val, str):
            raise ValueError("student_csv_file must be a string")
        self.student_csv_file = val

    @property
    def max_messages(self):
        return self.max_messages

    @max_messages.setter
    def max_messages(self, val: int):
        if not isinstance(val, int):
            raise ValueError("max_messages must be an integer")
        self.max_messages = val

    @property
    def max_time(self) -> int:
        return self.max_time

    @max_time.setter
    def max_time(self, val: str):
        if not isinstance(val, str):
            raise ValueError("max_time must be a string")
        if "h" not in val and "m" not in val:
            raise ValueError("max_time must be in the format 1h or 1m")
        if "m" in val:
            vals = val.split("m")
            self.max_time = int(vals[0]) * 60
        else:
            vals = val.split("h")
            self.max_time = int(vals[0]) * 3600

    @property
    def min_delay(self) -> int:
        return self.min_delay

    @min_delay.setter
    def min_delay(self, val: int):
        if not isinstance(val, int):
            raise ValueError("min_delay must be an integer")
        self.min_delay = val

    @property
    def max_timeout(self):
        return self.max_timeout

    @max_timeout.setter
    def max_timeout(self, val: int):
        if not isinstance(val, int):
            raise ValueError("max_timeout must be an integer")
        self.max_timeout = val

    @property
    def max_retries(self):
        return self.max_retries

    @max_retries.setter
    def max_retries(self, val: int):
        if not isinstance(val, int):
            raise ValueError("max_retries must be an integer")
        self.max_retries = val

    @property
    def handshake_url(self):
        return self.handshake_url

    @handshake_url.setter
    def handshake_url(self, val: str):
        if not isinstance(val, str):
            raise ValueError("handshake_url must be a string")
        if "joinhandshake.com" not in val:
            raise ValueError("handshake_url must be a Handshake url")
        self.handshake_url = val
