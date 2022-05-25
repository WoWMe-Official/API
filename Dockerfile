FROM python:3.10-slim
WORKDIR /code
COPY . /code/
RUN pip install --no-cache-dir -r requirements.txt
CMD ["uvicorn", "api.app:app", "--proxy-headers", "--host", "0.0.0.0"] 