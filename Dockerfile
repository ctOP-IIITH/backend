FROM python:3.10-slim
WORKDIR /app
COPY . /app/
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt
ENV PORT=3000
EXPOSE $PORT
CMD ["bash", "run.sh"]
