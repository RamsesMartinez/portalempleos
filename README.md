# Portal de Empleos

Job portal for everyone. Platform that connects job seekers with companies offering employment opportunities.

## 🚀 Features

- **Intelligent Search**: Advanced algorithms to connect talent with opportunities
- **Professional Profiles**: Creation of outstanding profiles
- **Quick Application**: Simplified application system
- **Multi-platform**: Responsive design for all devices
- **Smart Notifications**: Personalized alerts for new opportunities
- **Advanced Analytics**: Labor market statistics

## 🛠️ Technologies

- **Backend**: Django 5.1
- **Database**: PostgreSQL
- **Cache**: Redis
- **Task Queue**: Celery
- **Frontend**: Bootstrap 5, Custom CSS
- **Deployment**: Docker, Docker Compose
- **Storage**: AWS S3
- **Reverse Proxy**: Traefik

## 📋 Requirements

- Python 3.11+
- Docker and Docker Compose
- PostgreSQL
- Redis

## 🚀 Production Deployment

### Available Scripts

#### 1. **Complete Deployment** (`./scripts/deploy.sh`)
```bash
./scripts/deploy.sh
```
- ✅ Pre-deployment checks
- 🔄 Automatic backup of configuration and database
- 🐳 Docker container build and deployment
- 🗄️ Database migrations
- 📁 Automatic static files collection
- 🔍 Post-deployment verification
- 🚨 Automatic rollback on failure

#### 2. **Status Verification** (`./scripts/status.sh`)
```bash
./scripts/status.sh
```
- 🔍 Status of all services
- 📊 Resource usage
- 📝 Recent error logs
- 💾 Disk usage
- 🐳 Docker usage

#### 3. **Emergency Rollback** (`./scripts/rollback.sh`)
```bash
./scripts/rollback.sh
```
- ⚠️ User confirmation required
- 🔄 Restoration to previous version
- 🚨 For critical failure cases

### Deployment Flow

1. **Preparation**
   ```bash
   # Check current status
   ./scripts/status.sh
   
   # Ensure no pending changes
   git status
   ```

2. **Deployment**
   ```bash
   # Execute complete deployment
   ./scripts/deploy.sh
   ```

3. **Verification**
   ```bash
   # Check post-deployment status
   ./scripts/status.sh
   
   # Review logs if necessary
   docker compose -f docker-compose.production.yml logs -f
   ```

4. **In case of problems**
   ```bash
   # Immediate rollback
   ./scripts/rollback.sh
   ```

### System Services

- **🌐 Django**: Main application (port 5000)
- **🗄️ PostgreSQL**: Main database
- **⚡ Redis**: Cache and message queue
- **🚦 Traefik**: Reverse proxy and load balancer (ports 80, 443)
- **⚙️ Celery Worker**: Background task processing
- **⏰ Celery Beat**: Task scheduler
- **🌸 Flower**: Celery monitoring (port 5555)
- **☁️ AWS CLI**: Backup and S3 management

## 🔧 Local Development

### Environment Setup

1. **Clone repository**
   ```bash
   git clone <repository-url>
   cd portalempleos
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements/local.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .envs/.local/.django .envs/.local/.django.example
   # Edit .envs/.local/.django with your configurations
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run development server**
   ```bash
   python manage.py runserver
   ```

### Local Docker Compose

```bash
# Local services
docker compose -f docker-compose.local.yml up -d

# Documentation services
docker compose -f docker-compose.docs.yml up -d
```

## 📁 Project Structure

```
portalempleos/
├── config/                 # Main Django configuration
│   ├── settings/          # Environment-specific configurations
│   ├── storage.py         # S3 storage configuration
│   └── urls.py            # Main URLs
├── portalempleos/         # Main application
│   ├── templates/         # HTML templates
│   ├── static/            # Static files
│   └── users/             # Users application
├── compose/               # Docker configurations
│   ├── local/             # Local services
│   └── production/        # Production services
├── scripts/               # Automation scripts
│   ├── deploy.sh          # Complete deployment
│   ├── status.sh          # Status verification
│   └── rollback.sh        # Emergency rollback
└── requirements/           # Python dependencies
    ├── base.txt           # Base dependencies
    ├── local.txt          # Development dependencies
    └── production.txt     # Production dependencies
```

## 🔒 Security

- **HTTPS**: Automatic redirection in production
- **HSTS**: Security headers configured
- **CSRF**: CSRF protection enabled
- **File validation**: Uploaded file validation system
- **Authentication**: Robust system with django-allauth

## 📊 Monitoring

- **Sentry**: Error and performance monitoring
- **Flower**: Celery task monitoring
- **Logs**: Configured logging system
- **Health Checks**: Service health verifications

## 🚨 Troubleshooting

### Static Files Not Loading

If CSS/JS files don't load in production:

1. **Verify S3 configuration**
   ```bash
   python manage.py check --settings=config.settings.production
   ```

2. **Run collectstatic**
   ```bash
   python manage.py collectstatic --noinput --settings=config.settings.production
   ```

3. **Verify staticfiles.json in S3**

### Services Not Starting

1. **Check status**
   ```bash
   ./scripts/status.sh
   ```

2. **Review logs**
   ```bash
   docker compose -f docker-compose.production.yml logs -f [service]
   ```

3. **Check resources**
   ```bash
   docker stats
   df -h
   ```

## 🤝 Contributing

1. Fork the project
2. Create a branch for your feature (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is under the MIT License. See the `LICENSE` file for more details.

## 📞 Contact

- **Developer**: Ramses Martinez
- **Email**: contacto@portalempleos.com.mx
- **Website**: https://portalempleos.com.mx

## 🙏 Acknowledgments

- Django Cookiecutter for the base structure
- Django community for best practices
- Project contributors 
