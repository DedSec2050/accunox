# Accuknox Django Assignment

This project contains both assignment topics in one Django application and can be run from a single server process.

## Topics Covered

1. Django Signals
2. Custom Classes in Python (`Rectangle`)

## Tech Stack

- Python 3
- Django
- SQLite (default local database)

## Project Layout

- `accunox/` - Django project settings and root URLs
- `signals_app/` - Assignment app
- `signals_app/signals.py` - Signal handlers and runtime probe data
- `signals_app/views.py` - Views for both demos
- `signals_app/rectangle.py` - `Rectangle` class implementation
- `signals_app/templates/signals_app/` - HTML pages for both demos

## How to Run

1. Install dependencies (if needed):

```bash
python3 -m venv .venv
.venv/bin/pip install django
```

2. Run migrations:

```bash
.venv/bin/python manage.py makemigrations
.venv/bin/python manage.py migrate
```

3. Start server:

```bash
.venv/bin/python manage.py runserver
```

4. Open pages:

- Rectangle demo: http://127.0.0.1:8000/rectangle/
- Signals assignment demo: http://127.0.0.1:8000/signals-assignment/
- Django admin: http://127.0.0.1:8000/admin/

## Assignment 1: Django Signals

### Question 1

By default, Django signals are **synchronous**.

#### Proof logic used in this project

- Signal handler intentionally sleeps for 1 second on specific test usernames.
- Caller measures elapsed time around `User.objects.create_user(...)`.
- Observed elapsed time is >= 1 second, proving caller waits for handler completion.

Core snippet:

```python
# view
start = time.perf_counter()
User.objects.create_user(username=username_sync, password="pass12345")
elapsed = time.perf_counter() - start

# signal
if instance.username.startswith("signal_demo_sync_"):
    time.sleep(1)
```

### Question 2

By default, Django signals run in the **same thread** as the caller.

#### Proof logic used in this project

- Caller thread id is captured with `threading.get_ident()` before create call.
- Signal handler captures its own thread id.
- IDs are compared and match.

Core snippet:

```python
# caller
caller_thread_id = threading.get_ident()
set_caller_context(caller_thread_id)
User.objects.create_user(...)

# signal
signal_thread_id = threading.get_ident()
```

### Question 3

By default, Django signals run in the **same database transaction** as the caller.

#### Proof logic used in this project

- `User.objects.create_user(...)` is called inside `transaction.atomic()`.
- Signal creates a `MyModel` row during `post_save`.
- A forced exception triggers rollback.
- Both `User` row and signal-created `MyModel` row do not exist afterward.
- Signal also observes `connection.in_atomic_block == True`.

Core snippet:

```python
try:
    with transaction.atomic():
        User.objects.create_user(username=username_tx, password="pass12345")
        raise RuntimeError("Force rollback")
except RuntimeError:
    pass

tx_user_exists = User.objects.filter(username=username_tx).exists()
tx_model_exists = MyModel.objects.filter(name=f"from-signal:{username_tx}").exists()
```

## Assignment 2: Custom Rectangle Class

Requirement:

- `Rectangle(length: int, width: int)`
- Iterable behavior returns:
  1. `{"length": <value>}`
  2. `{"width": <value>}`

Implementation in this project:

```python
class Rectangle:
    def __init__(self, length: int, width: int):
        self.length = length
        self.width = width

    def __iter__(self):
        yield {"length": self.length}
        yield {"width": self.width}
```

### UI behavior

- `/rectangle/` page takes length and width from query params/form.
- View instantiates `Rectangle` and renders `list(rectangle)` in template output.

## Notes

- This repository is configured to avoid committing local-only artifacts via `.gitignore` (virtual env, sqlite db, caches, logs, env files, editor metadata).
- Both assignment topics are runnable in one Django project without separate standalone scripts.
