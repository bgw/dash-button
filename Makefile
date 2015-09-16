# in progress

.PHONY: all

all: .env

.env: setup.py
	rm -rf .env
	virtualenv -p python3 .env
	.env/bin/pip install .

clean:
	rm -rf .env
