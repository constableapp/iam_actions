# SPDX-License-Identifier: MIT
# Copyright 2020-2022 Big Bad Wolf Security, LLC

"""Upload generated JSON files to S3 to track revisions.

The JSON files written by iam_actions.generate.run can be given to this
script to upload them to S3 and notify about any changes since the
previous run.

The environment variable S3_BUCKET defines the bucket that will store
the uploaded files, and WEBHOOK optionally defines a Slack hook URL to
send notifications.
"""

import argparse
import boto3
import json
import os
from datetime import datetime
try:
    from slack_sdk.webhook import WebhookClient
except ImportError:
    WebhookClient = None


def create_argument_parser() -> argparse.ArgumentParser:
    """Return an `argparse.ArgumentParser` defining the CLI."""
    parser = argparse.ArgumentParser(
        description="Upload new IAM action JSON files to S3",
    )
    parser.add_argument("-a", "--actions", dest="action_map", metavar="PATH",
                        help="Path to the actions JSON file to upload",
                        type=argparse.FileType("rb"))
    parser.add_argument("-s", "--services", metavar="PATH",
                        help="Path to the services JSON file to upload",
                        type=argparse.FileType("rb"))
    parser.add_argument("-e", "--errors", metavar="PATH",
                        help="Path to the errors JSON file to upload",
                        type=argparse.FileType("rb"))
    return parser


def main(*pargs, **kwargs) -> None:
    """This is the entry point function."""
    args = create_argument_parser().parse_args()
    bucket = os.environ["S3_BUCKET"]
    webhook = os.getenv("WEBHOOK")

    client = boto3.client("s3")
    dest_dir = f"archived/{datetime.utcnow().isoformat()}"
    messages = []
    for name, source in vars(args).items():
        dest_path = f"{dest_dir}/{name}.json"
        latest_path = f"current/{name}.json"

        # Upload the file and read its hash to check for changes.
        new_hash = client.upload_fileobj(source, bucket, dest_path)["ETag"]
        old_hash = client.head_object(Bucket=bucket, Key=latest_path)["ETag"]

        # Update the file at the latest URL.
        client.copy_object(
            Bucket=bucket,
            CopySource=f"{bucket}/{dest_path}",
            Key=latest_path
        )

        # Note when the uploaded files have changed or if there were errors.
        if name == "errors":
            source.seek(0)
            errors = json.load(source)
            if errors:
                messages += ["\r\n".join(["**Errors:**"] + errors)]
        elif new_hash != old_hash:
            messages += [f"**Changes:**\r\n{name} has changed since last run"]

    if messages:
        print("\r\n\r\n".join(messages))
        if WebhookClient and webhook:
            slack = WebhookClient(webhook)
            slack.send(text="\r\n\r\n".join(messages))


if __name__ == "__main__":
    main()
