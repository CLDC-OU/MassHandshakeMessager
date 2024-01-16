
import logging
from types.student import Student
from pyparsing import nestedExpr


class Messager:
    def __init__(self):
        pass

    def send_message_to_student(self, student: Student, message):
        self.open_student_page(student)
        self.click_message_button()
        parsed_message = self.parse_message(student, message)
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
        pass

    def paste_message(self, message):
        pass

    def paste_subject(self, subject):
        pass

    def click_send(self):
        pass
    @property
    def wait(self) -> WebDriverWait:
        return self._wait

    @wait.setter
    def wait(self, timeout: int):
        self._wait = WebDriverWait(
            driver=self.config.webdriver,
            timeout=timeout)
