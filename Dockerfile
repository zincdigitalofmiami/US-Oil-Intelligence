# ---- Base Stage: Common python environment ----
FROM python:3.11.8-slim-bullseye as base
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
WORKDIR /app

# ---- Builder Stage: Install dependencies, lint, and test ----
FROM base as builder
# Copy requirements and install all dependencies (app + dev)
COPY requirements.txt .
RUN python -m pip install --upgrade pip
# The --no-warn-script-location is needed because we are running as root
RUN pip install --no-cache-dir --no-warn-script-location -r requirements.txt flake8 pytest

# Add the installed tools to the PATH
ENV PATH="/root/.local/bin:${PATH}"

# Copy source code needed for linting and testing
COPY svc ./svc

# Run linter
RUN flake8 ./svc

# Run tests
RUN pytest ./svc/tests

# ---- Runtime Stage: Final, lean production image ----
FROM base as runtime
ENV PORT=8080
ENV API_PORT=8080

# Create and switch to a non-root user
RUN useradd --create-home appuser
USER appuser
WORKDIR /home/appuser/app

# Copy installed python packages from the builder stage
# This copies only the production dependencies that were installed
COPY --from=builder --chown=appuser:appuser /root/.local /home/appuser/.local

# Add the user's local bin to the PATH
ENV PATH="/home/appuser/.local/bin:${PATH}"

# Copy application-specific code and data
COPY --chown=appuser:appuser svc ./svc
COPY --chown=appuser:appuser data ./data
COPY --chown=appuser:appuser public ./public

# Command to run the application
CMD ["python", "-m", "svc.main"]
