
import json
import logging
import os
import time
from src.config import Config
from src.types.student import Student

# from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

from colorama import Fore, Style

from src.utils import get_stats, get_stats_message, time_seconds_to_str


class Messager:
    def __init__(self):
        self.config = Config()
        self.config.load()
        self.wait = self.config.max_timeout

    def update_message_conditions(self):
        self.has_more_students = self.config.has_next_student()
        self.has_more_time = (
            self.config.max_time == -1
        ) or (
            self.time_running < self.config.max_time
        )
        self.has_more_messages = (
            self.config.max_messages == -1
        ) or (
            self.messages_sent < self.config.max_messages
        )

    def run(self):
        logging.debug("Starting messager...")
        self.load_stats()
        self.start_time = time.time() - self.time_running
        self.update_message_conditions()
        counter = 0

        # === Send Messages ===
        while (self.has_more_students and
               self.has_more_time and
               self.has_more_messages):
            counter += 1
            if counter % 10 == 0:
                message = f"Script has been running for {counter} " \
                    f"iterations, saving stats to file and resetting " \
                    f"webdriver..."
                logging.info(message)
                print(Fore.YELLOW + message + Style.RESET_ALL)
                self.update_stats()
                self.config.reset_webdriver()
                self.wait = self.config.max_timeout

            student = self.config.get_next_student()
            if student == -1:
                logging.debug("No more students to message")
                break

            # Send Message
            send_success = self.send_message_with_retry(
                student=student,
                message=self.config.message,
                retries=self.config.max_retries
            )

            self.update_time_running()
            logging.debug("Finished attempt to send message to "
                          f"{student.student_id} ({self.config.index})"
                          f"\n\tTime running: {self.time_running}s"
                          f"\n\tResult: "
                          f"{'Success' if send_success else 'Fail'}")
            self.update_message_conditions()

        self.update_stats()

        # === Report Results ===

        stop_message = (
            f"\n{Fore.LIGHTBLUE_EX}Finished after "
            f"{Fore.LIGHTMAGENTA_EX}{time_seconds_to_str(self.time_running)} "
            f"{Fore.LIGHTBLUE_EX}with reason: "
            f"{Fore.LIGHTMAGENTA_EX}{self.get_stop_cause()}\n{Style.RESET_ALL}"
        )
        logging.debug(stop_message)
        print(stop_message)

        stats_message = get_stats_message()
        logging.info(stats_message)
        print(stats_message)

    # Determines the reason for stopping the send message loop
    def get_stop_cause(self):
        if not self.has_more_messages:
            return "No more students to message"
        elif (
            self.config.max_time != -1
        ) and (
            self.time_running > self.config.max_time
        ):
            return f"Max time reached " \
                f"({time_seconds_to_str(self.config.max_time)})"
        elif (
            self.config.max_messages != -1
        ) and (
            self.messages_sent > self.config.max_messages
        ):
            return f"Max messages sent ({self.config.max_messages})"
        else:
            return "Unknown"

    def send_message_with_retry(
        self,
        student: Student,
        message: str,
        retries: int
    ):
        max_retries = retries
        success = False
        while success is not True and retries > 0:
            message_time = time.time()
            logging.debug(f"Starting attempt {max_retries-retries+1} to send "
                          f"message to {student.student_id}...")
            try:
                self.send_message_to_student(student, message)
                success = True
                self.messages_sent += 1
            except Exception as e:
                retries -= 1
                self.times_failed += 1
                logging.error(f"Error sending message to {student.student_id} "
                              f"({self.config.index})\n{e}"
                              f"\n\tRemaining retries: "
                              f"{retries}")

            message_time = time.time() - message_time
            sleep_time = self.config.get_rand_delay_time() - (message_time)

            self.update_time_running()
            self.update_message_conditions()

            if sleep_time < 0:
                sleep_time = 0
            if success and not self.has_more_students:
                sleep_time = 0
            if not self.has_more_time:
                sleep_time = 0
            if success and not self.has_more_messages:
                sleep_time = 0

            res = ""
            if success:
                res += f"Message successfully sent to {student.student_id} " \
                    f"({self.config.index}) after {max_retries-retries+1} " \
                    f"attempt{'s' if max_retries-retries > 0 else ''}" \
                    f"\n\tTook {message_time}s to send" \
                    f"\n\t{self.messages_sent} message" \
                    f"{'s' if self.messages_sent > 1 else ''} sent so far"
                self.time_sending += message_time
                if sleep_time > 0:
                    res += f"\n\tWaiting {sleep_time}s before sending " \
                        f"the next message..."
                logging.debug(res)
                print(Fore.GREEN + f"Message successfully sent to "
                      f"{student.student_id} ({self.config.index})"
                      + Style.RESET_ALL)
            else:
                res += f"Message failed to send to {student.student_id} " \
                    f"({self.config.index})\n\tTook {message_time}s to fail" \
                    f"\n\t{max_retries-retries} times tried so far"
                self.time_retrying += message_time
                if sleep_time > 0:
                    res += f"\n\tWaiting {sleep_time}s before retrying..."
                logging.warning(res)
                print(Fore.RED + f"Message failed to send to "
                      f"{student.student_id} ({self.config.index})"
                      + Style.RESET_ALL)
            if not self.has_more_time:
                break
            time.sleep(sleep_time)

        if not success:
            self.messages_failed += 1
        return success

    def update_time_running(self):
        self.time_running = time.time() - self.start_time

    def send_message_to_student(self, student: Student, message):
        parsed_message = self.parse_message(student, message)

        self.open_student_page(student)
        self.click_message_button()

        # wait for modal to load
        self.wait.until(
            EC.visibility_of_element_located(
                (By.ID, "modal-title")
            )
        )

        # time.sleep(1)

        self.paste_subject(self.config.message_subject)
        self.paste_message(parsed_message)
        time.sleep(0.5)
        self.click_send()

    def open_student_page(self, student: Student):
        url = f"{self.config.handshake_url}/users/{student.student_id}"
        logging.debug(f"Opening {url}")
        self.config.webdriver.get(url)

    def parse_message(self, student: Student, message: str):
        escaped_message = message.replace("\\{", "")
        escaped_message = escaped_message.replace("\\}", "")
        split_variables = escaped_message.split('{')

        if len(split_variables) == 1:  # There are no variables
            return message

        variable_message = ""

        for i in range(0, len(split_variables)):
            if "}" in split_variables[i]:
                split_variable = split_variables[i].split("}")
                student_data = student.get_student_data(split_variable[0])
                if student_data is not None:
                    logging.debug(
                        f"Replacing [{split_variable[0]}] with "
                        f"\"{student_data}\"")
                    variable_message += student_data
                    variable_message += split_variable[1]
                else:
                    logging.warning(f"Student {student.student_id} does not "
                                    f"have variable [{split_variable[0]}]")
                    variable_message += split_variable[1]
            else:
                variable_message += split_variables[i]

        return variable_message

    def click_message_button(self):
        message_button = self.get_message_button()
        logging.debug("Found message button")
        actions = ActionChains(self.config.webdriver)
        actions.move_to_element(message_button).perform()
        logging.debug("Scrolled to message button")
        message_button.click()
        logging.debug("Clicked message button")

    def get_message_button(self):
        button = self.wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, '//a[contains(@href,"send-message")]')
            )
        )
        return button

    def paste_message(self, message):
        actions = ActionChains(self.config.webdriver)
        actions.click(self.get_subject_field()).perform()
        actions.send_keys(Keys.TAB).perform()
        actions.send_keys(message).perform()

    def paste_subject(self, subject):
        if subject is None or subject == "":
            logging.debug("No subject to paste. Leaving subject field"
                          "as default")
            return
        self.get_send_button()  # Wait for subject field to load
        self.get_subject_field().send_keys(subject)
        logging.debug(f"Pasted subject {subject}")

    def get_subject_field(self):
        return self.config.webdriver.find_element(
            By.ID,
            "message-modal-subject"
        )

    def click_send(self):
        self.get_send_button().click()

    def get_send_button(self):
        return self.config.webdriver.find_element(
            By.XPATH,
            "//a[contains(@data-bind, 'click: createConversation')]"
        )

    def update_stats(self):
        stats = {
            "time_running": self.time_running,
            "messages_sent": self.messages_sent,
            "messages_failed": self.messages_failed,
            "times_failed": self.times_failed,
            "time_sending": self.time_sending,
            "time_retrying": self.time_retrying,
            "current_position": self.config.index,
        }
        with open("stats.json", "w") as f:
            f.write(json.dumps(stats, indent=4))
            f.close()

    def load_stats(self):
        (self.time_running, self.messages_sent, self.messages_failed,
         self.times_failed, self.time_sending, self.time_retrying,
         self.config.index) = get_stats()

    @property
    def wait(self) -> WebDriverWait:
        return self._wait

    @wait.setter
    def wait(self, timeout: int):
        self._wait = WebDriverWait(
            driver=self.config.webdriver,
            timeout=timeout)

    @property
    def time_running(self) -> float:
        return self._time_running

    @time_running.setter
    def time_running(self, time: float):
        if not isinstance(time, float):
            raise ValueError(f"Invalid time_running value {time}")
        self._time_running = time

    @property
    def messages_sent(self) -> int:
        return self._messages_sent

    @messages_sent.setter
    def messages_sent(self, messages: int):
        if not isinstance(messages, int):
            raise ValueError(f"Invalid messages_sent value {messages}")
        self._messages_sent = messages

    @property
    def messages_failed(self) -> int:
        return self._messages_failed

    @messages_failed.setter
    def messages_failed(self, messages: int):
        if not isinstance(messages, int):
            raise ValueError(f"Invalid messages_failed value {messages}")
        self._messages_failed = messages

    @property
    def times_failed(self) -> int:
        return self._times_failed

    @times_failed.setter
    def times_failed(self, times: int):
        if not isinstance(times, int):
            raise ValueError(f"Invalid times_failed value {times}")
        self._times_failed = times

    @property
    def time_sending(self) -> float:
        return self._time_sending

    @time_sending.setter
    def time_sending(self, time: float):
        if not isinstance(time, float):
            raise ValueError(f"Invalid time_sending value {time}")
        self._time_sending = time

    @property
    def time_retrying(self) -> float:
        return self._time_retrying

    @time_retrying.setter
    def time_retrying(self, time: float):
        if not isinstance(time, float):
            raise ValueError(f"Invalid time_retrying value {time}")
        self._time_retrying = time
