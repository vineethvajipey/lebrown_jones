ifneq (,$(wildcard ./.env))
	include .env
endif

export

.PHONY: run
run:
	poetry install && \
	poetry run python src/chatbot.py