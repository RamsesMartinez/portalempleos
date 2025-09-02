# 🤝 Contributing Guide

Thank you for your interest in contributing to **Job Portal**! This document will guide you through the contribution process.

## 🌟 **Why Contribute?**

- **🌍 Global Impact**: Help democratize access to employment
- **🚀 Learning**: Work with modern technologies and best practices
- **👥 Community**: Join a community of passionate developers
- **📚 Portfolio**: Add a meaningful project to your CV

## 🚀 **Getting Started**

### **1. Fork the Repository**
```bash
# Go to https://github.com/ramthedev/portalempleos
# Click "Fork" in the top right corner
```

### **2. Clone your Fork**
```bash
git clone https://github.com/YOUR_USERNAME/portalempleos.git
cd portalempleos
```

### **3. Set up Remote Repository**
```bash
git remote add upstream https://github.com/ramthedev/portalempleos.git
git fetch upstream
```

## 🔧 **Development Environment Setup**

### **Option 1: Docker (Recommended)**
```bash
# Clone and configure
git clone https://github.com/YOUR_USERNAME/portalempleos.git
cd portalempleos

# Configure environment variables
cp .envs/.local/.django.example .envs/.local/.django
cp .envs/.local/.postgres.example .envs/.local/.postgres

# Run services
docker compose -f docker-compose.local.yml up -d
```

### **Option 2: Local Environment**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements/local.txt

# Configure database
python manage.py migrate
python manage.py createsuperuser

# Run server
python manage.py runserver
```

## 📋 **Types of Contributions**

### **🐛 Report Bugs**
- **Verify** that the bug hasn't been reported already
- **Use** the bug report template
- **Include** steps to reproduce the problem
- **Attach** screenshots if relevant

### **💡 Suggest Features**
- **Describe** the functionality you'd like to see
- **Explain** why it would be useful
- **Consider** the impact on existing architecture

### **🔧 Improve Code**
- **Follow** the project's code conventions
- **Add** tests for new functionality
- **Update** documentation when necessary

### **📚 Improve Documentation**
- **Fix** typos and errors
- **Clarify** confusing instructions
- **Add** examples and use cases

## 📝 **Workflow**

### **1. Create a Branch**
```bash
git checkout -b feature/feature-name
# or
git checkout -b fix/fix-name
```

### **2. Make Changes**
- **Write** clean and well-documented code
- **Follow** PEP 8 conventions for Python
- **Add** tests for new functionality
- **Update** relevant documentation

### **3. Commit and Push**
```bash
git add .
git commit -m "feat: add new advanced search functionality"
git push origin feature/feature-name
```

### **4. Create Pull Request**
- **Go** to your fork on GitHub
- **Click** "New Pull Request"
- **Select** the branch with your changes
- **Describe** your changes in detail

## 🎯 **Code Conventions**

### **Python (PEP 8)**
```python
# ✅ Correct
def search_jobs(filters=None):
    """Search jobs based on provided filters."""
    if filters is None:
        filters = {}
    return Job.objects.filter(**filters)

# ❌ Incorrect
def searchJobs(filters=None):
    if filters==None:
        filters={}
    return Job.objects.filter(**filters)
```

### **Django**
```python
# ✅ Correct
class Job(models.Model):
    title = models.CharField(max_length=200, verbose_name="Job title")
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    publication_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-publication_date']
        verbose_name = "Job"
        verbose_name_plural = "Jobs"

# ❌ Incorrect
class job(models.Model):
    title=models.CharField(max_length=200)
    company=models.ForeignKey(company,on_delete=models.CASCADE)
```

### **HTML/Templates**
```html
<!-- ✅ Correct -->
<div class="job-card">
    <h3 class="job-title">{{ job.title }}</h3>
    <p class="job-company">{{ job.company.name }}</p>
    <div class="job-actions">
        <a href="{% url 'job_detail' job.id %}" class="btn btn-primary">
            View Details
        </a>
    </div>
</div>

<!-- ❌ Incorrect -->
<div class="jobCard">
    <h3>{{job.title}}</h3>
    <p>{{job.company.name}}</p>
    <div>
        <a href="{% url 'job_detail' job.id %}">View Details</a>
    </div>
</div>
```

## 🧪 **Testing**

### **Run Tests**
```bash
# All tests
python manage.py test

# Specific tests
python manage.py test portalempleos.users.tests
python manage.py test portalempleos.users.tests.test_models

# With coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Generate HTML report
```

### **Escribir Tests**
```python
# ✅ Ejemplo de test
from django.test import TestCase
from django.contrib.auth import get_user_model
from portalempleos.users.models import User

class UserModelTest(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.user_data = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }
    
    def test_create_user(self):
        user = self.User.objects.create_user(**self.user_data)
        self.assertEqual(user.email, self.user_data['email'])
        self.assertTrue(user.check_password(self.user_data['password']))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser')
```

## 📚 **Documentation**

### **Docstrings**
```python
def search_jobs_by_location(city, radius_km=50):
    """
    Search jobs within a specific radius of a city.
    
    Args:
        city (str): City name to search for
        radius_km (int, optional): Search radius in kilometers. Defaults to 50.
    
    Returns:
        QuerySet: Set of jobs that match the criteria
        
    Raises:
        ValueError: If city is empty or radius is negative
        
    Example:
        >>> jobs = search_jobs_by_location("Mexico City", 25)
        >>> print(f"Found {jobs.count()} jobs")
    """
    if not city:
        raise ValueError("City cannot be empty")
    
    if radius_km < 0:
        raise ValueError("Radius must be positive")
    
    # Search logic...
    return Job.objects.filter(
        location__city__iexact=city,
        location__radius_km__lte=radius_km
    )
```

## 🔍 **Code Review**

### **Before Submitting**
- [ ] **Tests pass** locally
- [ ] **Code follows** project conventions
- [ ] **Documentation** is updated
- [ ] **Commits** have descriptive messages
- [ ] **Changes** are atomic and focused

### **During Review**
- **Respond** to review comments
- **Make** requested changes
- **Keep** conversation professional
- **Learn** from suggestions

## 🎉 **After Approval**

- **Your code** will be merged into the main project
- **You'll receive** credit in the Git history
- **Your contribution** will help thousands of users
- **You'll be** part of the project's history

## 📞 **Getting Help**

### **Resources**
- **📖 Documentation**: [docs.portalempleos.com.mx](https://docs.portalempleos.com.mx)
- **💬 Discord**: [Job Portal Community](https://discord.gg/portalempleos)
- **🐛 Issues**: [GitHub Issues](https://github.com/ramthedev/portalempleos/issues)
- **📧 Email**: contributions@portalempleos.com.mx

### **Community**
- **Join** our Discord server
- **Participate** in GitHub discussions
- **Share** your ideas and suggestions
- **Help** other contributors

## 🏆 **Recognition**

### **Outstanding Contributors**
- **🥇 Gold**: 10+ approved PRs
- **🥈 Silver**: 5+ approved PRs  
- **🥉 Bronze**: 1+ approved PRs

### **Contribution Areas**
- **🔧 Backend**: Django, APIs, database
- **🎨 Frontend**: Templates, CSS, JavaScript
- **🚀 DevOps**: Docker, CI/CD, infrastructure
- **📚 Docs**: Documentation, guides, examples
- **🧪 Testing**: Unit tests, integration
- **🌍 Localization**: Translations, i18n

---

**Thank you for contributing to making the world a better place, one job connection at a time!** 🚀

*Job Portal - Democratizing access to employment*
