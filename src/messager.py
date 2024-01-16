
import logging
from types.student import Student
from pyparsing import nestedExpr


class Messager:
    def __init__(self):
        self.config = Config()
        self.config.load()
        self.wait = 15

    def send_message_to_student(self, student: Student, message):
        parsed_message = self.parse_message(student, message)

        self.open_student_page(student)
        self.click_message_button()

        # wait 1 second for modal to load
        time.sleep(1)

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
                        f"Replacing [{split_variable[0]}] with {student_data}")
                    variable_message += student_data
                    variable_message += split_variable[1]
                else:
                    logging.warn(f"Student {student.student_id} does not have "
                                 f"variable {split_variable[0]}")
                    variable_message += split_variable[1]
            else:
                variable_message += split_variables[i]

        return variable_message

    def open_handshake(self):
        pass

    def click_message_button(self):
        message_button = self.get_message_button()
        logging.debug("Found message button")
        actions = ActionChains(self.config.webdriver)
        actions.move_to_element(message_button).perform()
        # self.config.webdriver.execute_script(
        #     "arguments[0].scrollIntoView();", message_button)
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
        # return button.find_element(By.XPATH, "./..")

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
