FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

# because of crewai[tools] requirements are heavy
# it makes sense to try installing binary files when it possible
RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x start.sh

CMD ["./start.sh"]