FROM	python:3

ENV	APP_DIR	/var/app

# Install system packages and clean up when done.

RUN	set -x \
	&&	apt-get update \
	&&	apt-get install -y --no-install-recommends \
			tree \
			vim \
			zsh \
	&&	rm -rf /var/lib/apt/lists/*

# Provision application directory and user.
RUN	set -x \
	&&	mkdir -p ${APP_DIR} \
	&&	useradd tempbot -s /bin/false \
	&&	chown -R tempbot:tempbot ${APP_DIR}

# Copy python requirements.txt to build directory.
COPY	requirements.txt /requirements.txt

# Install python requirements.
RUN	pip install --upgrade pip
RUN	pip install --no-cache-dir -r /requirements.txt

# Copy startup script into image
COPY	entrypoint.sh /
RUN	chmod +x /entrypoint.sh

# Run remaining instructions in application directory.
WORKDIR	${APP_DIR}

# Upload the tempbot code.
COPY	tempbot.py ${APP_DIR}/tempbot.py

# Remaining instructions run as tempbot user.
USER	tempbot

ENV	BOT_ID		'U3URB1YN9'
ENV	SLACK_BOT_TOKEN	'xoxb-130861066757-NSL9gORaseaZyN1R8Au2Y31W'

# Specify command to run at container launch.
CMD	[ "/entrypoint.sh" ]
