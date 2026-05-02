from PyQt6.QtWidgets import *
from gui import *
import helper
import csv
import os

class Logic(QMainWindow, Ui_MainWindow):
    MINIMUM_SCORE = 0.0
    MAXIMUM_SCORE = 100.0

    MINIMUM_ATTEMPTS = 1
    MAXIMUM_ATTEMPTS = 4
    MAXIMUM_CREDIT_COUNT = 7
    
    INPUT_NAME = "Score_Input"
    LABEL_NAME = "Score_Label"

    ERROR_COLOR = "color:red"
    GOOD_COLOR = "color:green"

    ASSIGNER_WINDOW_INDEX = 1
    GPA_WINDOW_INDEX = 0
    VALID_LETTER_GRADES = ["A", "B", "C", "D", "F"]

    def __init__(self) -> None:
        """
        Initializes private variables and the application window, as well as connect events.
        """
        super().__init__()
        self.setupUi(self)

        # ----- INSTANCE VARIABLES -----
        self.__student_name : str = ""
        self.__attempt_count : int = 0
        self.__scores : list[float] = []

        self.__gpa_points : list[str] = []
        self.__credits : list[str] = []
        # --------------------
        self.stackedWidget.setCurrentIndex(self.ASSIGNER_WINDOW_INDEX)

        self.AssignerSubmit.clicked.connect(lambda: self.setup_scores())
        self.ScoreSubmit.clicked.connect(lambda : self.submit_scores())
        self.ScoreClear.clicked.connect(lambda : self.clear_scores())

        self.GPASubmit.clicked.connect(lambda: self.submit_gpa())
        self.GPAClear.clicked.connect(lambda: self.clear_gpa_input())

        self.SwapToGPA.clicked.connect(lambda: self.swap_window())
        self.SwapToAssigner.clicked.connect(lambda: self.swap_window())

        self.StudentNameInput.textChanged.connect(lambda : self.AssignerDisplay.clear())
        self.AttemptsInput.textChanged.connect(lambda : self.AssignerDisplay.clear())

        self.CreditsInput.textChanged.connect(lambda: self.GPADisplay.clear())
        self.LetterGradesInput.textChanged.connect(lambda: self.GPADisplay.clear())

    def setup_scores(self) -> None:
        """
        Dynamically creates score boxes and labels.
        """
        self.AssignerDisplay.clear()
        self.clear_scores()

        try:
            self.validate_assigner_input()

        except Exception as error:
            self.AssignerDisplay.setText(str(error))
            self.AssignerDisplay.setStyleSheet(self.ERROR_COLOR)

        else: # if no errors occur. pretty useful statement!
            self.ScoreSubmit.show()
            self.ScoreClear.show()

            # variables for clarity and to avoid hardcoding.
            label_x = 90
            label_width = 80
            input_x = 165
            input_width = 140
            y_coordinate = 210
            y_increment = 40
            height = 30

            for x in range(self.__attempt_count): # creates attempt_count new score boxes along with labels.
                score_label = QLabel(f"Score {x + 1}:", parent=self.AssignerWindow)
                score_label.setGeometry(label_x, y_coordinate, label_width, height)
                score_label.setObjectName(self.LABEL_NAME)
                score_label.show()

                score = QLineEdit(parent=self.AssignerWindow)
                score.setGeometry(input_x, y_coordinate, input_width, height)
                score.setObjectName(self.INPUT_NAME)
                score.textChanged.connect(lambda : self.AssignerDisplay.clear())
                score.show()

                y_coordinate += y_increment

    def submit_scores(self) -> None:
        """
        Writes scores and student name to a CSV file.
        """
        self.AssignerDisplay.clear()

        try:
            self.validate_scores()

        except Exception as error:
            self.AssignerDisplay.setText(str(error))
            self.AssignerDisplay.setStyleSheet(self.ERROR_COLOR)

        else: # write data to csv file.
            file = None

            if not os.path.exists("data.csv"): #file does not exist - create it, and append header row.
                file = open("data.csv", "a", newline="")
                writer = csv.writer(file)
                writer.writerow(["Name", "Score One", "Score Two", "Score Three", "Score Four", "Final"])

            file = open("data.csv", "a", newline="")
            writer = csv.writer(file)

            total = 0
            length = len(self.__scores)
            row = [self.__student_name]

            for x in range(self.MAXIMUM_ATTEMPTS):
                if x < length:
                    score = self.__scores[x]
                    total += score
                    row.append(str(score))

                else:
                    row.append("0")

            average = total / len(self.__scores)
            row.append(f"{average} - {helper.get_letter_grade(average)}")
            writer.writerow(row)
            file.close()

            self.AssignerDisplay.setText("Data saved to CSV file (named data.csv)!")
            self.AssignerDisplay.setStyleSheet(self.GOOD_COLOR)

    def validate_assigner_input(self) -> None:
        """
        Validates student name and number of scores.
        """
        self.__student_name = self.StudentNameInput.text().strip()

        if self.__student_name == "":
            raise ValueError("Please provide a student name.")

        scores = self.AttemptsInput.text().replace(" ", "")

        if scores == "":
            raise ValueError("Please provide a number of attempts.")

        elif not scores.isdecimal():
            raise ValueError("Attempts must be numeric and between 1 and 4, inclusive.")

        self.__attempt_count = int(scores)

        if self.__attempt_count < self.MINIMUM_ATTEMPTS or self.__attempt_count > self.MAXIMUM_ATTEMPTS:
            raise ValueError("Attempts must be between 1 and 4, inclusive.")

    def validate_scores(self) -> None:
        """
        Check that all scores are valid (numeric, not empty, in the range of [0, 100]).
        """
        self.__scores = []

        for widget in self.AssignerWindow.children():
            name = widget.objectName()
            
            if name == self.INPUT_NAME:
                score = widget.text().replace(" ", "")
                
                if score == "":
                    raise ValueError("Scores cannot be left blank.")
                
                try:
                    float(score)

                except:
                    raise ValueError("Scores must be numeric and between 0 and 100.")
                
                if float(score) < self.MINIMUM_SCORE or float(score) > self.MAXIMUM_SCORE:
                    raise ValueError("Scores must be between 0 and 100.")

                self.__scores.append(float(score))

    def clear_scores(self) -> None:
        """
        Removes score widgets and hides score buttons.
        """
        self.ScoreSubmit.hide()
        self.ScoreClear.hide()
        self.__scores = []

        for widget in self.AssignerWindow.children(): # all widgets in the assigner window are its children.
            name = widget.objectName()

            # score label and inputs are named "Score_Label" and "Score_Input", respectively. remove these.
            if name == self.INPUT_NAME or name == self.LABEL_NAME:
                widget.deleteLater()

    def submit_gpa(self) -> None:
        """
        Calculates grade point average of all classes.
        GPA = sum of (class credit * class grade on GPA scale) / total credits
        """
        self.GPADisplay.clear()  # clear error or previous GPA display.

        try:
            self.validate_gpa_input()

        except Exception as error:
            self.GPADisplay.setText(str(error))
            self.GPADisplay.setStyleSheet(self.ERROR_COLOR)

        else:
            input_length = len(self.__gpa_points)
            credit_sum = 0.0
            quality_points = 0.0

            for x in range(input_length): # calculates gpa
                curr_gpa_point = helper.get_gpa_point(self.__gpa_points[x])
                curr_credit = int(self.__credits[x])

                credit_sum += curr_credit
                quality_points += (curr_credit * curr_gpa_point)

            helper.write_gpa_data(round(quality_points / credit_sum, 2))

            self.GPADisplay.setText("Data saved to CSV file (named grades.csv)! Click \"Clear\" to reset "
                                    "input fields and enter extra data!")
            self.GPADisplay.setStyleSheet(self.GOOD_COLOR)

    def validate_gpa_input(self) -> None:
        """
        Checks for valid input in the GPA Calculator window. Throws errors otherwise,
        to be displayed to the user.
        """
        self.__credits = self.CreditsInput.text().replace(" ", "").split(",")
        self.__gpa_points = self.LetterGradesInput.text().replace(" ", "").split(",")

        if self.__gpa_points == [""]:  # empty letter grade list
            raise ValueError("Please provide a list of comma separated letter grades.")

        if self.__credits == [""]:  # empty credit list
            raise ValueError("Please provide a list of comma separated credit hours.")

        if len(self.__gpa_points) != len(self.__credits):
            raise RuntimeError(f"Please the same amount of credits and grades.")

        if len(self.__gpa_points) > self.MAXIMUM_CREDIT_COUNT or len(self.__credits) > self.MAXIMUM_CREDIT_COUNT:
            raise ValueError("Please provide between 1 and 7 credits and grades.")

        for letter in self.__gpa_points:  # validate each letter grade
            if letter.upper() not in self.VALID_LETTER_GRADES:
                raise ValueError("Please provide a list of valid grades (A, B, C, D, or F).")

        for credit in self.__credits:  # validate each credit - cannot be negative, float, or non-numeric.
            if not credit.isdigit or int(credit) < self.MINIMUM_SCORE:
                raise ValueError("Credits must be positive whole numbers or zero.")

    def clear_gpa_input(self) -> None:
        """
        Clears input fields and error/grade display boxes in the GPA Calculator window when pressing clear.
        """
        self.CreditsInput.clear()
        self.LetterGradesInput.clear()
        self.GPADisplay.clear()

    def swap_window(self) -> None:
        """
        Swaps between GPA Calculator and Grade Assigner windows. Clears pages before moving on.
        """
        if self.stackedWidget.currentIndex() == self.ASSIGNER_WINDOW_INDEX:
            self.clear_scores()
            self.stackedWidget.setCurrentIndex(self.GPA_WINDOW_INDEX)

        else:
            self.clear_gpa_input()
            self.stackedWidget.setCurrentIndex(self.ASSIGNER_WINDOW_INDEX)