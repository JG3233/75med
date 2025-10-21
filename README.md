# 75 Hard Challenge Tracker

A Dockerized multi-user web application for tracking progress through the 75 Hard Challenge. Built with Flask, HTMX, and SQLite - optimized for Raspberry Pi deployment.

## 🎯 Features

- **Multi-User Support**: Shared challenge timeline with individual tracking
- **Flexible Goals**: Each user can customize their 5 daily goals anytime
- **Real-Time Progress**: Check off goals with instant feedback using HTMX
- **Transparent Scoreboard**: View everyone's progress and goals
- **Motivational Feedback**: Contextual encouragement based on progress
- **Secure Authentication**: Password-based login system
- **Docker Ready**: Easy deployment on Raspberry Pi or any platform
- **Pi Optimized**: Lightweight containers with ARM64 support

## 🚀 Quick Start

### Prerequisites

- Raspberry Pi (any model with 2GB+ RAM recommended)
- Python 3.7+ (pre-installed on most Pi OS versions)

## Deployment Options

### Option 1: Docker (Recommended)

```bash
# Install Docker first
chmod +x install_docker_pi.sh
sudo ./install_docker_pi.sh

# Deploy the app
docker-compose up -d
```

### Option 2: Direct Python (Simpler)

```bash
# Transfer files to Pi
scp -r 75med/ pi@raspberry-pi-ip:~/

# Run deployment script
python3 deploy_pi.py

# Or manually:
python3 -m pip install -r requirements.txt
mkdir -p instance
python3 app.py
```

### Access the Application

Navigate to `http://your-raspberry-pi-ip:5000`

4. **Create accounts** and set your goals!

### First Time Setup

- One user should go to Settings > Challenge Settings to set the start date
- Other users can register and will automatically be added to the same timeline
- Each user gets default 75 Hard goals but can customize them anytime

## 🏗️ Architecture

### Tech Stack
- **Backend**: Flask + SQLAlchemy
- **Frontend**: Jinja2 templates + HTMX
- **Database**: SQLite (Raspberry Pi optimized)
- **Authentication**: Flask-Login with session persistence
- **Container**: Docker with docker-compose

### Database Schema

- **Users**: Account information and authentication
- **Challenge**: Global timeline (single active challenge)
- **Goals**: Customizable daily objectives per user
- **Daily Progress**: Check-off tracking per goal per day

### API Endpoints

- **Authentication**: `/login`, `/register`, `/logout`
- **Dashboard**: `/` (redirects to dashboard when logged in)
- **Goals**: `/goals` (GET/POST for viewing/editing)
- **Progress**: `/progress/toggle/<goal_id>` (HTMX endpoint)
- **Scoreboard**: `/scoreboard`
- **Settings**: `/challenge/settings`

## 🔧 Configuration

### Environment Variables

Set these in `docker-compose.yml`:

```yaml
environment:
  - SECRET_KEY=your-unique-secret-key-here
  - DATABASE_URL=sqlite:///75hard.db  # Persistent SQLite file
  - FLASK_ENV=production
```

### Challenge Timeline

By default, the challenge starts today. To change:
1. Log in as any user
2. Navigate to Settings > Challenge Settings
3. Update the challenge start date
4. **Important**: This affects all users

### Resource Limits (Raspberry Pi)

The docker-compose includes Pi-optimized resource limits:
- CPU: 1 core maximum, 0.25 reserved
- RAM: 512MB limit, 128MB reserved

Adjust based on your Pi model (4GB RAM recommended).

## 📊 Usage

### For Users

1. **Register/Login**: Create your account with username/password
2. **Dashboard**: View your daily goals and check them off
3. **Progress Tracking**: Visual progress bar shows completion %
4. **Scoreboard**: See how everyone is doing (including goals)
5. **Goal Editing**: Customize your 5 daily goals anytime via "My Goals"

### For Households

- **Shared Timeline**: Everyone on the same 75-day schedule
- **Full Transparency**: See each other's goals and progress
- **Motivation**: Compete kindly while supporting each other
- **Easy Scaling**: Add family members anytime

## 🔍 Troubleshooting

### Common Issues

**Container Won't Start:**
```bash
# Check logs
docker-compose logs 75hard-app

# Restart service
docker-compose restart 75hard-app
```

**Database Issues:**
```bash
# Reset database (WARNING: destroys all data)
docker-compose down
sudo rm -rf data/
docker-compose up -d
```

**Port Conflicts:**
- Change port in `docker-compose.yml`: `ports: - "5001:5000"`

**High CPU/Memory Usage:**
- Monitor with `docker stats`
- Adjust resource limits in `docker-compose.yml`

### Raspberry Pi Specific

**Slow Performance:**
- Ensure adequate cooling
- Increase memory limits if possible
- Consider SQLite WAL mode for better concurrency

**Storage Issues:**
- SQLite database grows over time
- Monitor disk space: `df -h`

## 🚀 Advanced Configuration

### Custom Domain

Use nginx-proxy or traefik:

```yaml
# Add to docker-compose.yml
services:
  nginx-proxy:
    image: nginxproxy/nginx-proxy:alpine
    ports:
      - "80:80"
    volumes:
      - /var/run/docker.sock:/tmp/docker.sock:ro

  75hard-app:
    environment:
      - VIRTUAL_HOST=75hard.yourdomain.com
      - LETSENCRYPT_HOST=75hard.yourdomain.com
      - LETSENCRYPT_EMAIL=your-email@domain.com
```

### Backup Strategy

```bash
# Backup script
#!/bin/bash
docker-compose exec 75hard-app sqlite3 /app/instance/75hard.db .dump > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore
docker-compose exec -T 75hard-app sqlite3 /app/instance/75hard.db < backup.sql
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test on your Pi/other devices
5. Submit a pull request

### Development Setup

```bash
# Local development (non-Docker)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export FLASK_ENV=development
python app.py
```

## 📄 License

MIT License - feel free to use this for your own family or community!

## 🙏 Acknowledgments

- 75 Hard program created by Andy Frisella
- Flask and HTMX communities
- Raspberry Pi enthusiasts everywhere

---

**Remember**: This is a 75-day commitment that will change your life! Stay strong, and remember... you CAN do this! 💪
