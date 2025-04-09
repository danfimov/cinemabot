args := $(wordlist 2, 100, $(MAKECMDGOALS))

HELP_FUN = \
	%help; while(<>){push@{$$help{$$2//'options'}},[$$1,$$3] \
	if/^([\w-_]+)\s*:.*\#\#(?:@(\w+))?\s(.*)$$/}; \
    print"$$_:\n", map"  $$_->[0]".(" "x(20-length($$_->[0])))."$$_->[1]\n",\
    @{$$help{$$_}},"\n" for keys %help; \

CODE = cinemabot
TEST = pytest --verbosity=2 --showlocals --log-level=DEBUG

ifndef args
MESSAGE = "No such command (or you pass two or many targets to ). List of possible commands: make help"
else
MESSAGE = "Done"
endif

help: ##@Help Show this help
	@echo -e "Usage: make [target] ...\n"
	@perl -e '$(HELP_FUN)' $(MAKEFILE_LIST)

install:  ##@Setup Install project requirements
	uv venv --allow-existing
	uv sync --all-extras

run:  ##@Application Run application
	python3 -m cinemabot

up:  ##@AApplication Create databases and app containers with docker-compose
	docker-compose -f docker-compose.yaml up -d --remove-orphans --build

migrate:  ##@Database Create database with docker-compose
	python3 -m cinemabot.infrastructure.database.migrations upgrade head

revision:  ##@Database Create database with docker-compose
	python3 -m cinemabot.infrastructure.database.migrations revision --autogenerate --message $(args)

test:  ##@Testing Test application with pytest
	$(TEST)

test-cov:  ##@Testing Test application with pytest and create coverage report
	$(TEST) --cov=$(CODE) --cov-report html --cov-fail-under=70

lint:  ##@Code Check code with pylint
	ruff check .

format:  ##@Code Reformat code with ruff and black
	ruff check . --fix --unsafe-fixes

build:  ##@Docker Build docker container with bot
	docker build  --platform linux/amd64 -f Dockerfile -t cinemabot:local .

%::
	echo $(MESSAGE)
