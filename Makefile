SHELL := /bin/bash

.PHONY: $(SERVICES) logs clean tests build

FORCE: ;  ## always run targets with this keyword


## NOTE: Add this to your .bashrc to enable make target tab completion
##    complete -W "\`grep -oE '^[a-zA-Z0-9_.-]+:([^=]|$)' ?akefile | sed 's/[^a-zA-Z0-9_.-]*$//'\`" make
## Reference: https://stackoverflow.com/a/38415982

help: ## This info
	@echo '_________________'
	@echo '| Make targets: |'
	@echo '-----------------'
	@echo
	@cat Makefile | grep -E '^[a-zA-Z\/_-]+:.*?## .*$$' | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
	@echo

clean:  ## Remove untracked files except for .env file
	git clean -fxd --exclude .env

push:  ## Push update to AWS Lambda function
	rm -f snorbot.zip
	pipenv run pip install -r <(pipenv lock -r) --target package
	cd package; zip -r9 ../snorbot.zip .
	zip -g snorbot.zip lambda_function.py slackapi.py
	aws lambda update-function-code --function-name snorbot --zip-file fileb://snorbot.zip
