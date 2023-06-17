args := $(wordlist 2, 100, $(MAKECMDGOALS))

APPLICATION_NAME = cinemabot

HELP_FUN = \
	%help; while(<>){push@{$$help{$$2//'options'}},[$$1,$$3] \
	if/^([\w-_]+)\s*:.*\#\#(?:@(\w+))?\s(.*)$$/}; \
    print"$$_:\n", map"  $$_->[0]".(" "x(20-length($$_->[0])))."$$_->[1]\n",\
    @{$$help{$$_}},"\n" for keys %help; \

CODE = cinemabot
TEST = poetry run python3 -m pytest --verbosity=2 --showlocals --log-level=DEBUG

ifndef args
MESSAGE = "No such command (or you pass two or many targets to ). List of possible commands: make help"
else
MESSAGE = "Done"
endif


help: ##@Help Show this help
	@echo -e "Usage: make [target] ...\n"
	@perl -e '$(HELP_FUN)' $(MAKEFILE_LIST)

install:  ##@Setup Install project requirements
	python3 -m pip install poetry
	poetry install

run:  ##@Application Run application
	poetry run python3 cinemabot/__main__.py

db:  ##@Database Create database with docker-compose
	docker-compose -f docker-compose.yml up -d --remove-orphans

migrate:  ##@Database Create database with docker-compose
	cd cinemabot/migrator && poetry run python3 main.py upgrade head

revision:  ##@Database Create database with docker-compose
	cd cinemabot/migrator && poetry run python3 main.py revision --autogenerate --message $(args)

test:  ##@Testing Test application with pytest
	make db && $(TEST)

test-cov:  ##@Testing Test application with pytest and create coverage report
	make db && $(TEST) --cov=$(APPLICATION_NAME) --cov-report html --cov-fail-under=70

lint:  ##@Code Check code with pylint
	poetry run python3 -m ruff $(CODE) tests

format:  ##@Code Reformat code with ruff and black
	poetry run python3 -m black $(CODE)
	poetry run python3 -m ruff $(CODE) tests --fix

clean:  ##@Code Clean directory from garbage files
	rm -fr *.egg-info dist

build:  ##@Docker Build docker container with bot
	docker build  --platform linux/amd64 -f Dockerfile -t bot:latest .

tag:  ##@Docker Create tag on local bot container
	docker tag bot cr.yandex/crp0741f2lnug1rolqa5/bot:latest

push:  ##@Docker Push container with bot to registry
	docker push cr.yandex/crp0741f2lnug1rolqa5/bot:latest

%::
	echo $(MESSAGE)

