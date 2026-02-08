# AWS Daily Platform Report

# Overview
This repository contains an automated workflow that runs on a daily schedule to collect platform signals from AWS and publish the results back to the repository.
It demonstrates how to build a simple, repeatable automation using GitHub Actions and AWS that focuses on visibility, correctness, and secure access rather than application delivery.

# What the workflow does
On a scheduled run or manual trigger, the workflow:

1. Authenticates to AWS using GitHub Actions OpenID Connect (OIDC)
2. Executes a Python script to query AWS platform data
3. Runs a Terraform plan to validate infrastructure configuration
4. Performs a lightweight static scan for additional visibility
5. enerates report files and commits them back to the repository

# Each run leaves a clear, versioned record of what was executed and what was observed.

