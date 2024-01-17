
import logging
import time
from src.config import Config
from src.types.student import Student

# from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains


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
        self.start_time = time.time()
        self.time_running = 0
        self.messages_sent = 0
        self.messages_failed = 0
        self.times_failed = 0
        self.time_sending = 0
        self.time_retrying = 0
        self.update_message_conditions()

        # === Send Messages ===
        while (self.has_more_students and
               self.has_more_time and
               self.has_more_messages):
            student = self.config.get_next_student()
            if student == -1:
                logging.debug("No more students to message")
                break
            self.send_message_to_student(student, self.config.message)
    def send_message_with_retry(self,
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
                logging.error(f"Error sending message to "
                              f"{student.student_id}\n{e}"
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
                res += f"Message sent to {student.student_id} " \
                    f"after {max_retries-retries+1} attempt" \
                    f"{'s' if max_retries-retries > 0 else ''}" \
                    f"\n\tTook {message_time}s to send" \
                    f"\n\t{self.messages_sent} message" \
                    f"{'s' if self.messages_sent > 1 else ''} sent so far"
                self.time_sending += message_time
                if sleep_time > 0:
                    res += f"\n\tWaiting {sleep_time}s before sending " \
                        f"the next message..."
                logging.debug(res)
            else:
                res += f"Message failed to send to {student.student_id}" \
                    f"\n\tTook {message_time}s to fail" \
                    f"\n\t{max_retries-retries+1} times tried so far"
                self.time_retrying += message_time
                if sleep_time > 0:
                    res += f"\n\tWaiting {sleep_time}s before retrying..."
                logging.warning(res)

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

    @property
    def wait(self) -> WebDriverWait:
        return self._wait

    @wait.setter
    def wait(self, timeout: int):
        self._wait = WebDriverWait(
            driver=self.config.webdriver,
            timeout=timeout)
