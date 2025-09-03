# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the project files into the container
COPY . .

# Install poetry for robust dependency management
# (This is a best practice for containerized Python apps)
RUN pip install poetry

# Use poetry to install dependencies from pyproject.toml
# --no-root prevents installing the project itself yet, which is a caching optimization
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --no-root

# Now, install the project itself
RUN pip install .

# Set the entrypoint to bash to allow interactive use
ENTRYPOINT ["/bin/bash"]