# Use the official Python image from the Docker Hub
FROM python:3.13-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project files
COPY . .

# Run the application
#CMD ["gunicorn", "--bind", "0.0.0.0:8001", "ecomm.wsgi:application"]

CMD ["python", "manage.py", "runserver", "0.0.0.0:9000"]
