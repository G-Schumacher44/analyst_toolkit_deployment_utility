# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the entire project context
COPY . .

# Install the project and its dependencies defined in pyproject.toml
RUN pip install .

# Set the entrypoint to bash to allow interactive use
ENTRYPOINT ["/bin/bash"]