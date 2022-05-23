FROM python:3.10-slim

WORKDIR /code
COPY . /code
RUN pip install -r requirements.txt
CMD ["python","-u","/code/main.py"]