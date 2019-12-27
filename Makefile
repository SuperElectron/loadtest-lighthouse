include make_env

NS ?= superelectron
COMPANY_REPOSITORY=superelectron
VERSION ?= latest

IMAGE_NAME ?= loadtest-lighthouse
CONTAINER_NAME ?= loadtest-lighthouse
CONTAINER_INSTANCE ?= default

.PHONY: show-version pull pull-company run run-company push push-company export-variables test

show-version:
	echo $(VERSION)

pull:
	docker pull $(NS)/$(IMAGE_NAME):$(VERSION)
pull-company:
	docker pull $(COMPANY_REPOSITORY)/$(IMAGE_NAME):$(VERSION)

run:
	docker run --name $(IMAGE_NAME) -d $(NS)/$(IMAGE_NAME):$(VERSION)
run-company:
	docker run --name $(IMAGE_NAME) -d $(COMPANY_REPOSITORY)/$(IMAGE_NAME):$(VERSION)

push:
	docker push $(COMPANY_REPOSITORY)/$(IMAGE_NAME):$(VERSION)
push-company:
	docker push $(IMAGE_NAME) -d $(NS)/$(IMAGE_NAME):$(VERSION)

export-variables:
	docker exec $(IMAGE_NAME) sh -c "$(EXPORTS)"

test:
	docker exec $(IMAGE_NAME) sh -c "python -m code/test_script"

default: build