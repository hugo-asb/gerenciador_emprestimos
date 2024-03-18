FROM python:3.11

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY . .
RUN pip install -r requirements.txt

EXPOSE 8000

RUN chmod +x entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]
