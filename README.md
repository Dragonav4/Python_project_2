# To-Do CLI – s31722 Project

Simple console application for managing a to-do list
---

## Purpose

* Quickly add tasks directly from the terminal  
* Mark tasks as completed and view overdue items  
* Filter by date / priority / tag  
* **Optionally** sync the `tasks.json` file with Google Drive (to keep data across computers)

---

## Getting Started

install dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
python todo_app.py
```

On first run, you will see a simple menu:

```
1 – Add task
2 – List tasks
3 – Complete task
4 – Delete task
5 – Search tasks
6 – Exit
```

> All data is stored in `data/tasks.json`.  
> If you enter an invalid date format, the app will show an error message and continue.

---

## Tests

This project uses **pytest**:

```bash
pytest -q
```

Tests use `tmp_path` fixtures, so your real `tasks.json` remains untouched.

---

## Project Structure

```
cli/                  # Command-line interface layer
services/             # Business logic (ToDoList)
models/               # Task dataclass definition
google_drive_sync/    # Optional Google Drive synchronization
tests/                # Pytest test suite
data/tasks.json       # Local storage (auto-created)
todo_app.py           # Entry point
```

---

## Google Drive Sync (Optional)

1. Go to Google Cloud Console and enable the **Drive API**.  
2. Create a Desktop OAuth client and download `credentials.json` to the project root.  
3. On first run, the app will open a browser, prompt you to sign in, and save your credentials to `token.json`.

To disable synchronization, initialize `ToDoList` with `sync=False`.

---