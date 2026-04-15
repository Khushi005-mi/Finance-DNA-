APP_NAME=finance-dna

install:
	pip install -r requirements.txt

test:
	pytest tests/ -v --disable-warnings

run:
	uvicorn api.routes:app --host 0.0.0.0 --port 8000

docker-build:
	docker build -t $(APP_NAME) .

docker-run:
	docker run -p 8000:8000 $(APP_NAME)

format:
	black .

lint:
	python -m py_compile $(shell find . -name "*.py")

clean:
	find . -type d -name "__pycache__" -exec rm -r {} +