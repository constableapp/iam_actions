# SPDX-License-Identifier: MIT
# Copyright 2020-2022 Big Bad Wolf Security, LLC
FROM python:3.10-bullseye
COPY . /src
RUN pip install --no-cache-dir /src
ENTRYPOINT ["/usr/local/bin/iam_actions_generate"]
CMD ["/usr/local/bin/iam_actions_generate", "--help"]
