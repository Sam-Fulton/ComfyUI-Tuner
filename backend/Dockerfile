FROM python:3.10.11

# Set the working directory inside the container to /backend
WORKDIR /backend

# Set PYTHONPATH to include /backend so that app is found properly
ENV PYTHONPATH="/backend"

# Copy the requirements file and install dependencies
COPY backend/requirements.txt /backend/requirements.txt
RUN pip install --no-cache-dir -r /backend/requirements.txt

# Copy the entire backend source code to the container's /backend directory
COPY backend /backend

# Expose the port Flask runs on
EXPOSE 5000

# Command to run the Flask app
CMD ["python", "-m", "app.app"]

