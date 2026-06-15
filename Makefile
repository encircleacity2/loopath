.PHONY: verify-lab1

REPO ?= .

verify-lab1:
	python3 labs/lab01/verify.py --repo $(REPO)
