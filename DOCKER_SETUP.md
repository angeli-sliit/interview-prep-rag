# 🐳 Docker Setup Guide

## Quick Start

### Option 1: Using Docker Compose (Recommended)

1. **Build and run:**
   ```bash
   docker-compose up --build
   ```

2. **Run in background:**
   ```bash
   docker-compose up -d
   ```

3. **View logs:**
   ```bash
   docker-compose logs -f
   ```

4. **Stop:**
   ```bash
   docker-compose down
   ```

### Option 2: Using Docker directly

1. **Build the image:**
   ```bash
   docker build -t interview-prep-rag .
   ```

2. **Run the container:**
   ```bash
   docker run -p 8501:8501 interview-prep-rag
   ```

3. **Run with environment variables:**
   ```bash
   docker run -p 8501:8501 \
     -e GROQ_API_KEY=your_groq_key_here \
     interview-prep-rag
   ```

4. **Run with .env file:**
   ```bash
   docker run -p 8501:8501 \
     --env-file .env \
     interview-prep-rag
   ```

## Access the Application

Once running, open your browser and navigate to:
- **Local:** http://localhost:8501
- **Network:** http://your-ip:8501

## Environment Variables

You can set API keys in two ways:

### Method 1: Environment Variables
```bash
export GROQ_API_KEY=your_key_here
export OPENAI_API_KEY=your_key_here
docker-compose up
```

### Method 2: .env File
Create a `.env` file in the project root:
```env
GROQ_API_KEY=your_groq_key_here
OPENAI_API_KEY=your_openai_key_here
```

Then run:
```bash
docker-compose up
```

## Docker Commands Cheat Sheet

```bash
# Build image
docker build -t interview-prep-rag .

# Run container
docker run -p 8501:8501 interview-prep-rag

# Run in background
docker run -d -p 8501:8501 --name rag-app interview-prep-rag

# View logs
docker logs -f rag-app

# Stop container
docker stop rag-app

# Remove container
docker rm rag-app

# Remove image
docker rmi interview-prep-rag

# List running containers
docker ps

# List all containers
docker ps -a

# Execute command in running container
docker exec -it rag-app bash
```

## Troubleshooting

### Port Already in Use
If port 8501 is already in use, change it in `docker-compose.yml`:
```yaml
ports:
  - "8502:8501"  # Use port 8502 instead
```

### Permission Issues
On Linux/Mac, you might need to use `sudo`:
```bash
sudo docker-compose up
```

### Build Fails
1. Check Docker is running: `docker --version`
2. Ensure Dockerfile is in the project root
3. Check internet connection (needed to download dependencies)

### Container Exits Immediately
Check logs:
```bash
docker logs rag-app
```

### API Keys Not Working
Ensure environment variables are set correctly:
```bash
docker exec -it rag-app env | grep API_KEY
```

## Production Deployment

For production, consider:

1. **Use specific Python version:**
   ```dockerfile
   FROM python:3.11-slim
   ```

2. **Add health checks** (already included)

3. **Use secrets management:**
   - Docker Secrets
   - Kubernetes Secrets
   - AWS Secrets Manager

4. **Add reverse proxy:**
   - Nginx
   - Traefik
   - Caddy

5. **Enable HTTPS:**
   - Let's Encrypt
   - Cloudflare

## Docker Image Size Optimization

The current Dockerfile uses `python:3.11-slim` for a smaller image size (~150MB vs ~900MB for full Python image).

To further optimize:
- Use multi-stage builds
- Remove unnecessary packages
- Use Alpine Linux (smaller but may have compatibility issues)

---

**Happy Dockerizing! 🐳**
