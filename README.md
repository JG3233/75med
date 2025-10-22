# 75 Hard Challenge Tracker

A multi-user web application for tracking the [75 Hard Challenge](https://andyfrisella.com/pages/75hard-info) - a 75-day personal development program. Built with Flask and optimized for deployment on Raspberry Pi.

## Features

- 🏋️ Multi-user progress tracking with shared 75-day timeline
- ✅ Daily goal check-offs with HTMX for smooth interactions
- 📊 Transparent scoreboard showing everyone's progress and streaks
- 🎯 Customizable goals per user (default: 5 goals)
- 🔒 Secure authentication with password hashing
- 🐳 Docker-ready for easy deployment
- 🥧 Raspberry Pi optimized (ARM architecture, resource limits)
- ⚡ Production-ready with Gunicorn WSGI server

## Tech Stack

- **Backend**: Flask 2.0+, SQLAlchemy, Flask-Login
- **Frontend**: Jinja2 templates, HTMX, CSS
- **Database**: SQLite (lightweight, perfect for Pi)
- **Production Server**: Gunicorn (WSGI server)
- **Deployment**: Docker + Docker Compose

## Quick Start (Docker)

### Prerequisites

- Docker and Docker Compose installed
- For Raspberry Pi: Use the automated deployment script (see below)

### Local Development

```bash
# Clone the repository
git clone <your-repo-url>
cd 75med

# Create .env file
cat > .env << EOF
FLASK_ENV=development
SECRET_KEY=$(openssl rand -hex 32)
DATABASE_URL=sqlite:///instance/75hard.db
EOF

# Start with Docker Compose (use docker-compose or docker compose depending on your version)
docker compose up -d
# OR: docker-compose up -d

# Access the app (note: port 5001 to avoid macOS AirPlay conflict)
open http://localhost:5001
```

**Notes**:
- This project supports both `docker compose` (v2) and `docker-compose` (v1). The scripts will auto-detect which version you have.
- **Port 5001**: We use port 5001 to avoid conflict with macOS AirPlay (which uses port 5000). Access at `http://localhost:5001`.

## Deployment to Raspberry Pi

### Automated Deployment (Recommended)

The included script handles everything automatically:

```bash
# Make the script executable (first time only)
chmod +x deploy_to_pi.sh

# Deploy to your Raspberry Pi
./deploy_to_pi.sh <raspberry-pi-ip-or-hostname>

# Example:
./deploy_to_pi.sh raspberrypi.local
# or
./deploy_to_pi.sh 192.168.1.100

# To build the Docker image on the Pi (slower but saves local resources):
./deploy_to_pi.sh raspberrypi.local --build-on-pi
```

The script will:
1. ✅ Test SSH connection to your Pi
2. ✅ Sync application files via rsync
3. ✅ Create `.env` file with secure random SECRET_KEY
4. ✅ Install Docker if not present
5. ✅ Build and start the Docker container
6. ✅ Verify the application is running

### Manual Deployment

If you prefer manual control:

```bash
# 1. Copy files to your Raspberry Pi
rsync -avz --exclude '__pycache__' --exclude '.git' \
  ./ pi@raspberrypi.local:/home/pi/75hard/

# 2. SSH into your Pi
ssh pi@raspberrypi.local

# 3. Navigate to the app directory
cd /home/pi/75hard

# 4. Create .env file
cat > .env << EOF
FLASK_ENV=production
SECRET_KEY=$(openssl rand -hex 32)
DATABASE_URL=sqlite:///instance/75hard.db
EOF

# 5. Install Docker (if not installed)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker pi
# Logout and login again for group changes

# 6. Start the application
docker-compose up -d

# 7. Check if running
docker-compose ps
```

### First Time Setup

1. Navigate to `http://<your-raspberry-pi-ip>:5000`
2. Create an account (first user)
3. Go to Settings > Challenge Settings to set the start date
4. Invite others to register - they'll join the same timeline
5. Customize your goals in "My Goals"

## Managing Your Deployment

**Note**: Use `docker compose` or `docker-compose` depending on your version. Examples below use `docker compose`.

### View Logs

```bash
# SSH into Pi
ssh pi@raspberrypi.local

# View logs
cd /home/pi/75hard
docker compose logs -f
```

### Stop/Start/Restart

```bash
# Stop
docker compose down

# Start
docker compose up -d

# Restart
docker compose restart

# Check status
docker compose ps
```

### Update Application

```bash
# From your local machine
./deploy_to_pi.sh raspberrypi.local
```

### Backup Database

```bash
# SSH into Pi
ssh pi@raspberrypi.local

# Create backup
docker cp 75hard-app:/app/instance/75hard.db ~/75hard_backup_$(date +%Y%m%d).db

# Copy backup to local machine (from your computer)
scp pi@raspberrypi.local:~/75hard_backup_*.db ./
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_ENV` | Environment (development/production) | `production` |
| `SECRET_KEY` | Flask session encryption key | Auto-generated |
| `DATABASE_URL` | SQLite database path | `sqlite:///instance/75hard.db` |

### Docker Resource Limits (Raspberry Pi)

Configured in [docker-compose.yml](docker-compose.yml):
- **CPU**: 1.0 core max, 0.25 reserved
- **Memory**: 512MB limit, 128MB reserved
- **Health Check**: Every 30s with 3 retries
- **Workers**: 2 Gunicorn workers with 2 threads each

## Default Goals

New users automatically get these 5 goals:
1. Complete two 45-minute workouts (one must be outdoors)
2. Follow a diet (no alcohol or cheat meals)
3. Drink 1 gallon of water
4. Read 10 pages of a non-fiction book
5. Take a progress photo

Goals can be customized in the app settings.

## Troubleshooting

### Can't Connect to Raspberry Pi

```bash
# Check SSH is enabled on Pi
# Enable via: sudo raspi-config → Interface Options → SSH

# Test connection
ssh pi@raspberrypi.local
```

### Container Won't Start

```bash
# Check logs
docker compose logs

# Rebuild container
docker compose down
docker compose build --no-cache
docker compose up -d
```

### Permission Errors

```bash
# Ensure pi user is in docker group
sudo usermod -aG docker pi

# Logout and login again
```

### Database Issues

```bash
# Reset database (WARNING: deletes all data)
docker compose down
docker volume rm 75med_sqlite_data
docker compose up -d
```

## Development

### Running Locally Without Docker

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
FLASK_ENV=development
SECRET_KEY=dev-secret-key
DATABASE_URL=sqlite:///instance/75hard.db
EOF

# Run app
python app.py

# Access at http://localhost:5000
```

### Project Structure

```
75med/
├── app.py                 # Main Flask application
├── models.py              # Database models
├── config.py              # Flask configuration
├── requirements.txt       # Python dependencies
├── Dockerfile             # Docker image definition
├── docker-compose.yml     # Docker orchestration
├── deploy_to_pi.sh        # Automated deployment script
├── .dockerignore          # Files to exclude from Docker build
├── templates/             # Jinja2 HTML templates
│   ├── base.html
│   ├── dashboard.html
│   ├── login.html
│   ├── register.html
│   ├── goals.html
│   ├── scoreboard.html
│   └── challenge_settings.html
└── static/
    └── css/
        └── style.css      # Custom styles
```

## License

This project is open source and available under the MIT License.

---

**Made with ❤️ for the 75 Hard Challenge community**
