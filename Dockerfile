FROM swe-arena-base

RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-virtualenv \
    python3-venv \
    libpq-dev \
    gcc \
    --no-install-recommends && rm -rf /var/lib/apt/lists/*

ENV COMMIT_HASH=da3c1ed27eda275985322f78b2f42bb16dd924a9
ENV REPO_URL=https://github.com/qwakeley-teachx/zed-base.git
ENV REPO_NAME=zed-base

WORKDIR /testbed/${REPO_NAME}

RUN git init && \
  git remote add origin ${REPO_URL} && \
  git fetch --depth 1 origin ${COMMIT_HASH} && \
  git checkout FETCH_HEAD && \
  git remote remove origin

RUN chmod -R 777 /testbed/${REPO_NAME}

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir \
    psycopg2-binary \
    sqlalchemy \
    python-dotenv \
    marshmallow \
    customtkinter
