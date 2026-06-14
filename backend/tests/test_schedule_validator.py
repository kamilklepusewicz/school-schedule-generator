import unittest

from backend.schedule_validator import validate_schedule


def valid_data():
    return {
        "lessons": [
            {
                "id": 1,
                "subject_id": 1,
                "classroom_id": 1,
                "teacher_id": 1,
                "group_id": 1,
                "day": 1,
                "slot": 1,
            },
            {
                "id": 2,
                "subject_id": 1,
                "classroom_id": 2,
                "teacher_id": 2,
                "group_id": 2,
                "day": 1,
                "slot": 1,
            },
            {
                "id": 3,
                "subject_id": 2,
                "classroom_id": 3,
                "teacher_id": 3,
                "group_id": 1,
                "day": 1,
                "slot": 2,
            },
        ],
        "teachers": [
            {"id": 1, "subject_id": 1},
            {"id": 2, "subject_id": 1},
            {"id": 3, "subject_id": 2},
        ],
        "classrooms": [
            {"id": 1, "classroom_type_id": 1},
            {"id": 2, "classroom_type_id": 1},
            {"id": 3, "classroom_type_id": 2},
        ],
        "groups": [{"id": 1}, {"id": 2}],
        "subjects": [
            {"id": 1, "classroom_type_id": 1},
            {"id": 2, "classroom_type_id": 2},
        ],
        "lesson_counts": [
            {"student_group_id": 1, "subject_id": 1, "hours": 1},
            {"student_group_id": 1, "subject_id": 2, "hours": 1},
            {"student_group_id": 2, "subject_id": 1, "hours": 1},
        ],
    }


class ScheduleValidatorTests(unittest.TestCase):
    def test_accepts_valid_schedule(self):
        self.assertEqual(validate_schedule(**valid_data()), [])

    def test_detects_teacher_classroom_and_group_collisions(self):
        data = valid_data()
        data["lessons"].append(
            {
                "id": 4,
                "subject_id": 1,
                "classroom_id": 1,
                "teacher_id": 1,
                "group_id": 1,
                "day": 1,
                "slot": 1,
            }
        )
        data["lesson_counts"][0]["hours"] = 2

        errors = validate_schedule(**data)

        self.assertTrue(any("Teacher 1 collision" in error for error in errors))
        self.assertTrue(any("Classroom 1 collision" in error for error in errors))
        self.assertTrue(any("Group 1 collision" in error for error in errors))

    def test_detects_invalid_time_references_and_assignments(self):
        data = valid_data()
        data["lessons"][0].update(
            {
                "teacher_id": 999,
                "classroom_id": 3,
                "day": 0,
                "slot": 9,
            }
        )

        errors = validate_schedule(**data)

        self.assertTrue(any("expected 1-5" in error for error in errors))
        self.assertTrue(any("expected 1-8" in error for error in errors))
        self.assertTrue(any("missing teacher 999" in error for error in errors))
        self.assertTrue(any("requires type 1" in error for error in errors))

    def test_detects_teacher_assigned_to_wrong_subject(self):
        data = valid_data()
        data["lessons"][0]["teacher_id"] = 3

        errors = validate_schedule(**data)

        self.assertTrue(any("who is assigned to subject 2" in error for error in errors))

    def test_detects_lesson_count_mismatch(self):
        data = valid_data()
        data["lessons"].pop()

        errors = validate_schedule(**data)

        self.assertIn("Group 1, subject 2: expected 1 lessons, found 0.", errors)

    def test_detects_lesson_count_with_missing_reference(self):
        data = valid_data()
        data["lesson_counts"].append(
            {"student_group_id": 999, "subject_id": 999, "hours": 1}
        )

        errors = validate_schedule(**data)

        self.assertTrue(any("references missing group 999" in error for error in errors))
        self.assertTrue(any("references missing subject 999" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
