FROM python:3.7
COPY requirements.txt .

RUN apt-get update && apt-get install libpq-dev && apt-get clean

RUN pip install -U pip && pip install wheel && pip install -r requirements.txt

COPY . /app

# Expose the application on port 8000
EXPOSE 8000
# Run test server
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

CMD ["exec", "gunicorn", "xanana.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]