# ──────────────────────────────────────────────
#  Base image — Python version is LOCKED to 3.11.9
#  Do NOT change to "python:3.11" (floating tag).
# ──────────────────────────────────────────────
FROM python:3.11.9-slim

# Metadata
LABEL maintainer="1906900946@qq.com"
LABEL task="csv-cleaner-cli"
LABEL version="1.0"

# Set a consistent locale and timezone
ENV LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    TZ=UTC \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Create workspace directory
WORKDIR /workspace

# Copy the dirty input data into the image so the agent has it available
COPY dirty_data.csv /workspace/dirty_data.csv

# The agent's solution file will be mounted or copied here at runtime.
# Nothing else to install — stdlib only, no pip installs needed.

# Default command: drop into a shell so test.sh can run freely
CMD ["/bin/bash"]
