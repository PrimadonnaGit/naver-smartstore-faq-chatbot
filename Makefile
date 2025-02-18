.PHONY: install setup run preprocess redis-up redis-down help

help:
	@echo "사용 가능한 명령어:"
	@echo "make install      - Poetry 및 필요한 패키지 설치"
	@echo "make setup        - 초기 환경 설정 (디렉토리 생성 등)"
	@echo "make preprocess   - FAQ 데이터 전처리 실행"
	@echo "make redis-up     - Redis 서버 도커 컨테이너 실행"
	@echo "make redis-down   - Redis 서버 도커 컨테이너 중지"
	@echo "make run         - FastAPI 서버 실행"

install:
	poetry install

setup:
	mkdir -p data
	test -f .env.local || cp .env.example .env.local
	@echo "환경 설정이 완료되었습니다. .env 파일에 OPENAI_API_KEY를 설정해주세요."

preprocess:
	poetry run python scripts/preprocessing.py

redis-up:
	docker run --name redis-chat -p 6379:6379 -d redis:alpine

redis-down:
	docker stop redis-chat
	docker rm redis-chat

run:
	poetry run uvicorn src.main:app --reload
