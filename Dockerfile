# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install poetry for robust dependency management
RUN pip install poetry

# Copy only the files needed for dependency installation first.
# This leverages Docker's layer caching, so dependencies are not re-installed on every code change.
COPY pyproject.toml poetry.lock* ./

# Use poetry to install dependencies.
# --no-root prevents installing the project itself, which we'll do after copying the source code.
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --no-root

# Now, copy the rest of the project source code into the container
COPY . .

# Install the project itself
RUN pip install .

# Set the entrypoint to bash to allow interactive use
ENTRYPOINT ["/bin/bash"]