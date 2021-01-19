# For ubuntu, the latest tag points to the LTS version, since that is
# recommended for general use.
FROM python:3.6-slim

# grab gosu for easy step-down from root
# gosu is in repos for Debian 9 and later
RUN set -x \
	&& buildDeps=' \
		unzip \
		ca-certificates \
		dirmngr \
		wget \
		xz-utils \
		gpg \
		gpg-agent \
		ffmpeg \
		gosu \
	' \
	&& apt-get update && apt-get install -y --no-install-recommends $buildDeps \
	&& gosu nobody true

# install youtube-dl-webui
ENV YOUTUBE_DL_WEBUI_SOURCE /usr/src/youtube_dl_webui
WORKDIR $YOUTUBE_DL_WEBUI_SOURCE

COPY . $YOUTUBE_DL_WEBUI_SOURCE
RUN pip install .

ENTRYPOINT ["./docker-entrypoint.sh"]

CMD ["python", "-m", "youtube_dl_webui", "-c", "./config.json"]