SHELL := /bin/bash

.PHONY: $(SERVICES) logs clean tests build

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

install: ## Install virtual environment
	pipenv install --dev

clean: ## Remove untracked files except for .env file
	git clean -fxd --exclude .env

push: ## Push update to AWS Lambda function
	rm *.zip

	cd snorslack; zip -r9 ../snorslack.zip *
	pipenv run aws lambda update-function-code --function-name snorslack \
		--zip-file fileb://snorslack.zip
	pipenv run aws lambda update-function-configuration --function-name snorslack \
		--layers $$(pipenv run aws lambda list-layers | grep -e "LayerVersionArn" | grep snorbot | awk -F\" '{ print $$4 }')

	cd snorbot; zip -r9 ../snorbot.zip *
	pipenv run aws lambda update-function-code --function-name snorbot \
		--zip-file fileb://snorbot.zip
	pipenv run aws lambda update-function-configuration --function-name snorbot \
		--layers $$(pipenv run aws lambda list-layers | grep -e "LayerVersionArn" | grep snorbot | awk -F\" '{ print $$4 }')

layers: ## Push update to AWS Layers
	pipenv run pip install -r <(pipenv lock -r) --target python/lib/python3.8/site-packages
	zip -r9 snorbot-dependencies.zip python
	pipenv run aws lambda publish-layer-version --layer-name snorbot-dependencies \
		--zip-file fileb://snorbot-dependencies.zip \
		--compatible-runtimes python3.8
