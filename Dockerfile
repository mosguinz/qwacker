FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Install uv
RUN pip install --upgrade uv

# Copy dependency files
COPY pyproject.toml uv.lock* ./

# Install dependencies
RUN uv sync

COPY . .
CMD ["uv", "run", "task", "start"]
