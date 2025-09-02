# Use a specific, common base image for reproducibility
FROM python:3.11.8-slim-bullseye

# Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PORT=8080
ENV API_PORT=8080

# Set the working directory
WORKDIR /app

# Create a non-root user to run the app and add their local bin to the PATH
RUN useradd --create-home appuser
ENV PATH="/home/appuser/.local/bin:${PATH}"

# Copy requirements file and change ownership
COPY --chown=appuser:appuser requirements.txt .

# Switch to the non-root user
USER appuser

# Upgrade pip and install dependencies as the non-root user
RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir --user -r requirements.txt

# Copy the rest of the application code
COPY --chown=appuser:appuser svc ./svc
COPY --chown=appuser:appuser data ./data
COPY --chown=appuser:appuser public ./public

# Command to run the application
CMD ["python", "-m", "svc.main"]
