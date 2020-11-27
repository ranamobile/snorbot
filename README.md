# Introduction

This is a AWS Lambda-based Slack Bot to interact with Slack.

# Installation

This project manages a Lambda Layer for the Python dependencies and two Lambda Functions with the Slack Bot interactions.

## Deploy Updates

Create a local `.env` file with AWS environment variables with your own credentials.

```
AWS_ACCESS_KEY_ID=xxxxxxxxxx
AWS_SECRET_ACCESS_KEY=xxxxxxxxxx
AWS_DEFAULT_REGION=xxxxxxxxxx
```

Installation and updates for these components are wrapped in the Makefile.

* `make layers` - Run to push updates to Python dependencies
* `make push` - Run to push changes to the Slack Bot

## Manual Configuration

The Lambda Functions require a few environment variables including:

* `SLACK_OAUTH_TOKEN` - Slack Events API oauth token
* `SLACK_VERIFICATION_TOKEN` - Slack Events API verification token
* `GOOGLE_DRIVE_CONFIG` - JSON format of Google Drive API credentials

# Development

## Lambda Layer

Both Lambda Functions are using a Lambda Layer as a base layer for the dependencies.

https://docs.aws.amazon.com/lambda/latest/dg/configuration-layers.html

Dependencies are managed using Pipfile.

## Lambda Functions

There are two Lambda Functions as part of this Slack Bot due to the sometimes long processing time for the operations, e.g. uploading files to Google Drive. Slack API expects response within 3 seconds.

https://api.slack.com/events-api#the-events-api__responding-to-events

* snorbot - Respond to Slack Events API within the 3-second response window and trigger the snorslack Lambda Function.
* snorslack - Perform Slack Bot interactions, e.g. Google translate or save files to Google Drive
