# Use an official Python runtime as a parent image
FROM python:3.13-slim

# Set the working directory in the container
WORKDIR /app

# Copy the entire project context
COPY . .

# Install the project and its dependencies defined in pyproject.toml
RUN pip install .

# Set the entrypoint to your CLI tool
ENTRYPOINT ["analyst-deploy"]

# Default command shows help output so container doesn’t appear "empty"
CMD ["--help"]