# iam_actions

This project is a collection of tools to scrape the AWS public website for information.
It currenly is only building a "service map" and "action map" which contain information about the AWS policy components for each service.

## Running

This will produce three JSON files in the current directory.

```sh
python3 -m iam_actions.generate -a actions.json -s services.json -e errors.json
```

If the host's Python version is not suitable, the module can be installed in a Docker container with `docker build .`.
When it outputs the last image layer's hex ID, it can be run with the following.

```sh
docker run run -tv "$PWD:/wd" -w /wd $IMAGE_ID -a actions.json -s services.json -e errors.json
```

## Deploying

Ideally, you'd want this running on a schedule to inform you of any changes.
The script `s3.py` is an example of storing output revisions in S3 and reporting on differences in the JSON.
