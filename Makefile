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

hide:  ## Encrypt credentials/secrets to save to repo
	openssl aes-256-cbc -a -salt -in snorslack/pikaservice_credentials.json -out snorslack/pikaservice_credentials.json.enc

reveal:  ## Reveal credentials/secrets
	if [ ! -f "snorslack/pikaservice_credentials.json" ]; then openssl aes-256-cbc -d -a -in snorslack/pikaservice_credentials.json.enc -out snorslack/pikaservice_credentials.json; fi

push: reveal  ## Push update to AWS Lambda function
	cd snorslack; pipenv run pip install --target . -r requirements.txt
	cd snorslack; zip -r9 ../snorslack.zip *
	pipenv run aws lambda update-function-code --function-name snorslack --zip-file fileb://snorslack.zip

	cd snorbot; pipenv run pip install --target . -r requirements.txt
	cd snorbot; zip -r9 ../snorbot.zip *
	pipenv run aws lambda update-function-code --function-name snorbot --zip-file fileb://snorbot.zip
