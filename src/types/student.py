class Student:
    def __init__(self, student_id, data):
        self.student_id = student_id
        self.data = data

    def get_student_data(self, var_name):
        if var_name not in self.data:
            return None
        return self.data[var_name]
