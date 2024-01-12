import logging
from types.student import Student
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
        pass

    def parse_message(self, student: Student, message: str):
        pass

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
