import os
import csv

class Constants:
    """
    Contains static constant variables to use in helper methods.
    Makes things easier...
    """
    GRADE_LETTER_A = "A"
    GRADE_LETTER_B = "B"
    GRADE_LETTER_C = "C"
    GRADE_LETTER_D = "D"
    GRADE_LETTER_F = "F"

    GPA_POINTS_A = 4.0
    GPA_POINTS_B = 3.0
    GPA_POINTS_C = 2.0
    GPA_POINTS_D = 1.0
    GPA_POINTS_F = 0.0

    GRADE_A_MINIMUM = 90.0
    GRADE_B_MINIMUM = 80.0
    GRADE_C_MINIMUM = 70.0
    GRADE_D_MINIMUM = 60.0

def get_letter_grade(score: float) -> str:
    """
    Matches a given score to its corresponding letter grade.
    :param score: A student score.
    """
    if score >= Constants.GRADE_A_MINIMUM:
        return Constants.GRADE_LETTER_A

    elif score >= Constants.GRADE_B_MINIMUM:
        return Constants.GRADE_LETTER_B

    elif score >= Constants.GRADE_C_MINIMUM:
        return Constants.GRADE_LETTER_C

    elif score >= Constants.GRADE_D_MINIMUM:
        return Constants.GRADE_LETTER_D

    return Constants.GRADE_LETTER_F

def get_gpa_point(point: str) -> float:
    """
    Converts a letter grade to its value on the GPA scale. Ex: A = 4.0
    :param point: A class's letter grade on the GPA scale.
    """
    point = point.upper()

    match point:
        case Constants.GRADE_LETTER_A:
            return Constants.GPA_POINTS_A
        case Constants.GRADE_LETTER_B:
            return Constants.GPA_POINTS_B
        case Constants.GRADE_LETTER_C:
            return Constants.GPA_POINTS_C
        case Constants.GRADE_LETTER_D:
            return Constants.GPA_POINTS_D
        case _:
            return Constants.GPA_POINTS_F

def write_gpa_data(grade_point_average : float) -> None:
    """
    Writes GPA data to a CSV file.
    :param grade_point_average: A grade point average, to be written to a file.
    """
    file = None

    if not os.path.exists("grades.csv"):
        file = open("grades.csv", "a", newline="")
        writer = csv.writer(file)
        writer.writerow(["GPA"])

    file = open("grades.csv", "a", newline="")
    writer = csv.writer(file)
    writer.writerow([grade_point_average])
    file.close()