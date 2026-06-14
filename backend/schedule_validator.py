from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import urlopen


ENDPOINTS = {
    "lessons": "/classes",
    "teachers": "/teachers",
    "classrooms": "/class_rooms",
    "groups": "/class_groups",
    "subjects": "/subjects",
    "lesson_counts": "/lesson_counts",
}

LESSON_FIELDS = (
    "subject_id",
    "classroom_id",
    "teacher_id",
    "group_id",
    "day",
    "slot",
)


def _is_integer(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _record_label(record: dict[str, Any], position: int) -> str:
    return f"lesson {record.get('id', f'at position {position}')}"


def _build_index(
    records: list[dict[str, Any]], entity_name: str, errors: list[str]
) -> dict[int, dict[str, Any]]:
    index: dict[int, dict[str, Any]] = {}
    for position, record in enumerate(records, start=1):
        if not isinstance(record, dict):
            errors.append(f"{entity_name} at position {position} is not an object.")
            continue

        record_id = record.get("id")
        if not _is_integer(record_id):
            errors.append(
                f"{entity_name} at position {position} has an invalid or missing id."
            )
            continue

        if record_id in index:
            errors.append(f"Duplicate {entity_name} id: {record_id}.")
            continue

        index[record_id] = record
    return index


def _add_collision_errors(
    lessons: list[tuple[str, dict[str, Any]]],
    resource_field: str,
    resource_name: str,
    errors: list[str],
) -> None:
    occupied: dict[tuple[int, int, int], str] = {}
    for label, lesson in lessons:
        key = (lesson["day"], lesson["slot"], lesson[resource_field])
        previous = occupied.get(key)
        if previous is not None:
            errors.append(
                f"{resource_name} {lesson[resource_field]} collision on day "
                f"{lesson['day']}, slot {lesson['slot']}: {previous} and {label}."
            )
        else:
            occupied[key] = label


def validate_schedule(
    lessons: list[dict[str, Any]],
    teachers: list[dict[str, Any]],
    classrooms: list[dict[str, Any]],
    groups: list[dict[str, Any]],
    subjects: list[dict[str, Any]],
    lesson_counts: list[dict[str, Any]],
) -> list[str]:
    """Return every detected schedule error. An empty list means valid data."""
    errors: list[str] = []

    teacher_by_id = _build_index(teachers, "teacher", errors)
    classroom_by_id = _build_index(classrooms, "classroom", errors)
    group_by_id = _build_index(groups, "group", errors)
    subject_by_id = _build_index(subjects, "subject", errors)

    valid_lessons: list[tuple[str, dict[str, Any]]] = []
    exact_lessons: dict[tuple[int, ...], str] = {}

    for position, lesson in enumerate(lessons, start=1):
        if not isinstance(lesson, dict):
            errors.append(f"Lesson at position {position} is not an object.")
            continue

        label = _record_label(lesson, position)
        missing_fields = [field for field in LESSON_FIELDS if field not in lesson]
        if missing_fields:
            errors.append(f"{label} is missing fields: {', '.join(missing_fields)}.")
            continue

        invalid_fields = [
            field for field in LESSON_FIELDS if not _is_integer(lesson[field])
        ]
        if invalid_fields:
            errors.append(
                f"{label} has non-integer fields: {', '.join(invalid_fields)}."
            )
            continue

        valid_lessons.append((label, lesson))

        if lesson["day"] not in range(1, 6):
            errors.append(f"{label} has day {lesson['day']}; expected 1-5.")
        if lesson["slot"] not in range(1, 9):
            errors.append(f"{label} has slot {lesson['slot']}; expected 1-8.")

        references = (
            ("teacher", lesson["teacher_id"], teacher_by_id),
            ("classroom", lesson["classroom_id"], classroom_by_id),
            ("group", lesson["group_id"], group_by_id),
            ("subject", lesson["subject_id"], subject_by_id),
        )
        for entity_name, entity_id, index in references:
            if entity_id not in index:
                errors.append(f"{label} references missing {entity_name} {entity_id}.")

        teacher = teacher_by_id.get(lesson["teacher_id"])
        if teacher is not None and teacher.get("subject_id") != lesson["subject_id"]:
            errors.append(
                f"{label} assigns subject {lesson['subject_id']} to teacher "
                f"{lesson['teacher_id']}, who is assigned to subject "
                f"{teacher.get('subject_id')}."
            )

        classroom = classroom_by_id.get(lesson["classroom_id"])
        subject = subject_by_id.get(lesson["subject_id"])
        if classroom is not None and subject is not None:
            room_type = classroom.get("classroom_type_id")
            required_type = subject.get("classroom_type_id")
            if room_type != required_type:
                errors.append(
                    f"{label} uses classroom {lesson['classroom_id']} of type "
                    f"{room_type}, but subject {lesson['subject_id']} requires type "
                    f"{required_type}."
                )

        exact_key = tuple(lesson[field] for field in LESSON_FIELDS)
        previous = exact_lessons.get(exact_key)
        if previous is not None:
            errors.append(f"Duplicate lesson data: {previous} and {label}.")
        else:
            exact_lessons[exact_key] = label

    _add_collision_errors(valid_lessons, "teacher_id", "Teacher", errors)
    _add_collision_errors(valid_lessons, "classroom_id", "Classroom", errors)
    _add_collision_errors(valid_lessons, "group_id", "Group", errors)

    expected_counts: Counter[tuple[int, int]] = Counter()
    for position, demand in enumerate(lesson_counts, start=1):
        if not isinstance(demand, dict):
            errors.append(f"Lesson count at position {position} is not an object.")
            continue

        group_id = demand.get("student_group_id")
        subject_id = demand.get("subject_id")
        hours = demand.get("hours")
        if not all(_is_integer(value) for value in (group_id, subject_id, hours)):
            errors.append(
                f"Lesson count at position {position} has invalid group, subject, or hours."
            )
            continue
        if hours < 0:
            errors.append(f"Lesson count at position {position} has negative hours.")
            continue
        if group_id not in group_by_id:
            errors.append(
                f"Lesson count at position {position} references missing group "
                f"{group_id}."
            )
        if subject_id not in subject_by_id:
            errors.append(
                f"Lesson count at position {position} references missing subject "
                f"{subject_id}."
            )
        expected_counts[(group_id, subject_id)] += hours

    actual_counts = Counter(
        (lesson["group_id"], lesson["subject_id"])
        for _, lesson in valid_lessons
    )
    for group_subject in sorted(expected_counts.keys() | actual_counts.keys()):
        expected = expected_counts[group_subject]
        actual = actual_counts[group_subject]
        if actual != expected:
            group_id, subject_id = group_subject
            errors.append(
                f"Group {group_id}, subject {subject_id}: expected {expected} lessons, "
                f"found {actual}."
            )

    return errors


def _fetch_json_list(api_url: str, path: str) -> list[dict[str, Any]]:
    url = f"{api_url.rstrip('/')}{path}"
    with urlopen(url, timeout=10) as response:
        payload = json.load(response)
    if not isinstance(payload, list):
        raise ValueError(f"{path} returned {type(payload).__name__}, expected a list.")
    return payload


def load_schedule_data(api_url: str) -> dict[str, list[dict[str, Any]]]:
    return {
        name: _fetch_json_list(api_url, path)
        for name, path in ENDPOINTS.items()
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the timetable currently exposed by the backend API."
    )
    parser.add_argument(
        "--api-url",
        default="http://localhost:8000",
        help="Backend base URL (default: http://localhost:8000).",
    )
    args = parser.parse_args()

    try:
        data = load_schedule_data(args.api_url)
    except (HTTPError, URLError, TimeoutError, ValueError, json.JSONDecodeError) as error:
        print(f"Could not load schedule data: {error}", file=sys.stderr)
        return 2

    errors = validate_schedule(**data)
    if errors:
        print(f"Schedule is invalid. Found {len(errors)} problem(s):")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Schedule is valid ({len(data['lessons'])} lessons checked).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
