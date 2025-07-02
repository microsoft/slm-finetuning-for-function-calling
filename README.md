# SLM fine-tuning & evaluation labs

This repository contains labs for [finetuning](finetuning/README.md) and [evaluating](evaluation/README.md) Small Language Models (SLMs) developed for the AI Learning day at Microsoft (March for EMEA and April for Americas). The labs are designed to be interactive with various levels of depths so that audience with various backgrounds and experience levels, from beginners to advanced users can learn and understand the concepts with little to no guidance.

## Key Points Covered

- Small Language Models (SLMs)
- Function Calling
- Data Preparation
- Tokenization
- Model Configuration
- Fine-Tuning
- Evaluation Metrics for SLMs
- Error Analysis

## Pre-requisites

Some familiarity with the following will help:

- Python
- Jupyter notebooks, though we will be using them in VS Code which is much simpler :)
- A conceptual understanding of large language models (LLM) and Machine Learning Basics (training, validation, and evaluation)

## Environment setup

You have 3 options for environment setup using Notebooks. Please choose the one which suits you best.

1. [**Github CodeSpaces**](docs/env-setup-codespaces.md) - a purely cloud-based environment.  This should be your go-to option if you do NOT have a linux environment (OSX or WSL2/Windows).

2. [**Run code on a remote VM**](docs/env-setup-remote-vm.md) - run the code from VS Code. Ideal if you need some beefy processing, and have access to a high-performance Azure VM.

3. **Run on your laptop** - if you have plenty of RAM and maybe wish to test the performance of inference & fine-tuning on your local machine.  You have two options:

    a. [With a Dev Container](docs/env-setup-devcontainer.md) OR

    b. [Create your own virtualenv](docs/env-setup-local.md) - if you are comfortable with creating a Python environment on your local machine.

## Accessing the labs

This repo contains two labs:

1. [SLM finetuning](finetuning/README.md) - everything from running an SLM for the first time, to inference, finetuning & performance-tuning.

2. [Evaluation lab](evaluation/README.md) - building on the 'SLM finetuning' lab, we focus on the important aspect of Evaluation.
