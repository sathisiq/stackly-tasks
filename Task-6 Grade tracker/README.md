# Student Marks & Grade Tracker API

A Flask and MySQL REST API for managing students, their marks, and calculated grades. Every response is JSON. Grades are calculated in Python from the percentage (never in SQL).

## Setup

1. Create the database and tables: `mysql -u root -p < schema.sql`.
2. Install dependencies: `pip install -r requirements.txt`.
3. Configure MySQL if needed (defaults: `localhost`, port `3306`, user `root`, database `grade_tracker`):

   ```powershell
   $env:DB_PASSWORD="your_mysql_password"
   # Optional: DB_HOST, DB_PORT, DB_USER, DB_NAME
   ```

4. Run: `python app.py`.

The server starts at `http://localhost:5000`.

## Grade rules

| Percentage | Grade | Remark |
|---|---|---|
| 90–100 | A | Outstanding |
| 75–89.99 | B | Well done |
| 60–74.99 | C | Keep improving |
| 45–59.99 | D | Needs attention |
| Below 45 | F | Please seek help |

## Endpoints

### Students

`GET /students` — list all students.

Sample response:

```json
{"students":[{"id":1,"name":"Asha Rao","email":"asha@example.com","created_at":"2026-07-24T10:00:00"}]}
```

`GET /students/1` — get one student. Returns `404` when it does not exist.

`POST /students` — create a student.

```json
{"name":"Asha Rao","email":"asha@example.com"}
```

Response (`201`):

```json
{"message":"Student created","student":{"id":1,"name":"Asha Rao","email":"asha@example.com","created_at":"2026-07-24T10:00:00"}}
```

`PUT /students/1` — update either or both name and email.

```json
{"name":"Asha R."}
```

Response:

```json
{"message":"Student updated","student":{"id":1,"name":"Asha R.","email":"asha@example.com","created_at":"2026-07-24T10:00:00"}}
```

`DELETE /students/1` — deletes the student and their marks through the database cascade.

```json
{"message":"Student and all associated marks deleted"}
```

`GET /students/search?name=asha` — optional name search.

### Marks

`GET /students/1/marks` — gets marks, with percentage, grade, and remark. Use `?subject=math` to filter by subject.

Sample response:

```json
{"student_id":1,"marks":[{"id":1,"student_id":1,"subject":"Mathematics","score":86.0,"max_score":100.0,"percentage":86.0,"grade":"B","remarks":"Well done","added_on":"2026-07-24T10:05:00"}]}
```

`POST /students/1/marks` — add a mark. `max_score` defaults to 100.

```json
{"subject":"Mathematics","score":86,"max_score":100}
```

Response (`201`):

```json
{"message":"Mark added","mark":{"id":1,"student_id":1,"subject":"Mathematics","score":86.0,"max_score":100.0,"percentage":86.0,"grade":"B","remarks":"Well done","added_on":"2026-07-24T10:05:00"}}
```

`DELETE /marks/1` — delete one mark entry.

```json
{"message":"Mark deleted"}
```

### Reports

`GET /students/1/report` — returns all subjects plus average percentage, overall grade, pass/fail status, best subject, and weakest subject.

```json
{"student":{"id":1,"name":"Asha Rao","email":"asha@example.com","created_at":"2026-07-24T10:00:00"},"subjects":[{"id":1,"student_id":1,"subject":"Mathematics","score":86.0,"max_score":100.0,"percentage":86.0,"grade":"B","remarks":"Well done","added_on":"2026-07-24T10:05:00"}],"average_percentage":86.0,"overall_grade":"B","status":"Pass","best_subject":{"subject":"Mathematics","percentage":86.0},"weakest_subject":{"subject":"Mathematics","percentage":86.0}}
```

`GET /summary` — returns student count, class average, count by grade, highest/lowest student, pass/fail totals, and optional rankings.

```json
{"total_students":1,"class_average_percentage":86.0,"students_per_grade":{"A":0,"B":1,"C":0,"D":0,"F":0},"highest_scoring_student":{"id":1,"name":"Asha Rao","average_percentage":86.0,"grade":"B","rank":1},"lowest_scoring_student":{"id":1,"name":"Asha Rao","average_percentage":86.0,"grade":"B","rank":1},"pass_count":1,"fail_count":0,"rankings":[{"id":1,"name":"Asha Rao","average_percentage":86.0,"grade":"B","rank":1}]}
```

## Error responses

All invalid inputs return JSON and do not expose server errors. Missing fields and invalid scores return `400`; unknown student/mark returns `404`; a duplicate email returns `409`.

For example, either `{"subject":"Math","score":-10}` or `{"subject":"Math","score":150,"max_score":100}` returns:

```json
{"error":"'score' must be between 0 and max_score"}
```

with HTTP `400`.

## Required write-up

### Where grades are calculated

`calculate_grade(percentage)` in `app.py` holds the grade rules. It is called by `serialize_mark` for every mark and by the report and summary endpoints for overall grades.

```python
def calculate_grade(percentage):
    percentage = float(percentage)
    if percentage >= 90: return "A"
    if percentage >= 75: return "B"
    if percentage >= 60: return "C"
    if percentage >= 45: return "D"
    return "F"
```

### Class-average SQL

The API uses the same percentage expression per student when building rankings. A direct class-average query is:

```sql
SELECT AVG((score / max_score) * 100) AS class_average_percentage
FROM marks;
```

### Invalid score behaviour

A negative score, or a score above `max_score`, is rejected before insertion with HTTP `400` and the JSON response shown above. No mark is saved.
