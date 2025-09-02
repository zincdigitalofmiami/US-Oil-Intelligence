# Use a slim, secure Python base image
FROM python:3.11-slim as base

# --- Builder Stage ---
# Used for installing dependencies, linting, and testing.
FROM base as builder

# Set the working directory
WORKDIR /app

# Create a non-root user
RUN useradd --create-home appuser
USER appuser

# Copy dependency files
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# --- Final Stage ---
# Used for the final, lean production image.
FROM base

# Set the working directory
WORKDIR /app

# Create a non-root user
RUN useradd --create-home appuser
USER appuser

# Copy installed dependencies from the builder stage
COPY --from=builder /home/appuser/.local /home/appuser/.local

# Copy the application code
COPY . .

# Set the PATH to include the installed packages
ENV PATH=/home/appuser/.local/bin:$PATH

# Expose the port the app runs on
EXPOSE 8080

# Run the application
CMD exec gunicorn --bind :8080 --workers 1 --threads 8 --timeout 0 main:app
