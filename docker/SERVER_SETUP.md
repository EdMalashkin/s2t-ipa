# Server Setup Guide

## Prerequisites

1. **Install Podman and Podman Compose**:

   ```bash
   # On RHEL/CentOS/Fedora
   sudo dnf install podman podman-compose

   # On Ubuntu/Debian
   sudo apt update && sudo apt install podman podman-compose
   ```

2. **Create deployment directory**:

   ```bash
   sudo mkdir -p /opt/s2t-ipa
   sudo chown $USER:$USER /opt/s2t-ipa
   cd /opt/s2t-ipa
   ```

3. **Download docker-compose.yml**:

   ```bash
   curl -o docker-compose.yml https://raw.githubusercontent.com/EdMalashkin/s2t-ipa/master/docker/docker-compose.yml
   ```

4. **Create cache directory**:

   ```bash
   sudo mkdir -p /var/cache/s2t/ipa
   ```

5. **Set up environment file**:
   ```bash
   echo "DOCKERHUB_USERNAME=your_dockerhub_username" > .env
   ```

## GitHub Actions Secrets

Configure these secrets in your GitHub repository:

- `SERVER_SSH_KEY`: Private SSH key for server access
- `SERVER_HOST`: Server IP address or hostname
- `SERVER_USER`: SSH username for server access
- `DOCKERHUB_USERNAME`: Your Docker Hub username
- `DOCKERHUB_TOKEN`: Your Docker Hub access token

## Manual Deployment

To deploy manually on the server:

```bash
cd /opt/s2t-ipa
sudo podman pull docker.io/your_username/s2t-ipa:latest
sudo podman-compose up -d
```

## Health Check

Verify the service is running:

```bash
curl http://localhost:8080/health
```
