FROM python:3.10.11

WORKDIR /backend

ENV PYTHONPATH="/backend"

COPY backend/requirements.txt /backend/requirements.txt
RUN pip install -r /backend/requirements.txt

COPY backend /backend

EXPOSE 5000

CMD ["python", "-m", "app.app"]

