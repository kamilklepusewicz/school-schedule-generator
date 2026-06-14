# school-schedule-generator


## Most basic docker workflow:

1. docker compose config
2. docker compose up --build

## Basic git workflow

1. git switch _branchName_
2. git pull origin _branchName_
3. git add .
4. git commit -m "_message_"
5. git push

## Access to different app sections

- Frontend: http://localhost:5173/
- Guided setup: http://localhost:5173/admin-data-wizard
- Backend: http://localhost:8000/docs

## Manual schedule validation

After generating a timetable and starting the backend, validate the data exposed
to the frontend with:

```powershell
python backend/schedule_validator.py --api-url http://localhost:8000
```

The command exits with code `0` for a valid schedule, `1` when schedule problems
are found, and `2` when the backend data cannot be loaded. Validator unit tests
can be run with:

```powershell
python -m unittest discover -s backend/tests -v
```
