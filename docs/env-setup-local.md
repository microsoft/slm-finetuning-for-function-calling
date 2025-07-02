# Environment setup on your local machine

Warning: This could be potentially the most challenging setup. Only recommended if:

- Your laptop has at least 32GB memory
- You have macOS, Linux or WSL2 (on Windows)
- You are able to create Python virtual environments

Bonus points if your laptop has an Nvidia GPU but it's not a necessity to get through the lab - you'll still learn lots about performance without one, even if it's learning the hard way 😅

<br>

## Create a Python virtual environment

Python version 3.11 or newer should work fine. (Codespaces is running Python 3.11.11)

Use one of the following options to create your virtualenv and install dependencies:

### Option 1 - using uv

'uv' is a lightning-fast package and dependency manager for Python, written in rust.

- Install `uv` if you haven't already. [Instructions here](https://docs.astral.sh/uv/getting-started/installation/)
- Verify that uv is installed by running `uv --version` in your terminal or command prompt.
- Open a new terminal within VS Code.
- Run `uv sync` to create a new virtual environment to install the dependencies in `.venv`
- You can then activate the virtualenv.
  - On Windows - `.venv\Scripts\activate`
  - On macOS/Linux: `source .venv/bin/activate`

After activation, you should see the virtual environment name in your terminal prompt.

<br>

### Option 2 - using Poetry

- Install Poetry if you haven't already got it. <https://python-poetry.org/docs/>
- Update poetry if you had it already installed - `poetry self update`
- Create the virtual env & install the dependencies - `poetry install`

This also creates a virtualenv within the '.venv' folder, and installs the dependencies in 'pyproject.toml'.

You can either:

- activate this virtualenv with `poetry shell` OR
- execute commands using `poetry run ...` instead

<br>

### Option 3 - using the basic venv module

To manually create a virtual environment using Python’s venv module, and then activate it, and install dependencies:

```bash
python -m venv .venv

source .venv/bin/activate

pip install -r requirements.txt
```

<br>

## Use the notebooks

You're now ready to [run the notebooks in VS Code](using-notebooks-in-vs-code.md).
