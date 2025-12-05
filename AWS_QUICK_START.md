# AWS Deployment - Quick Start Guide
## For Presentation Next Week

**Deadline:** Before presentation
**Total Time:** 2-3 days (10-15 hours)

---

## Pre-Deployment Checklist

### Prerequisites (30 minutes)
- [ ] AWS account ready (you have this)
- [ ] AWS CLI installed: `winget install Amazon.AWSCLI`
- [ ] Terraform installed: `winget install Hashicorp.Terraform`
- [ ] Configure AWS credentials: `aws configure`
- [ ] Set up billing alerts (critical!)

---

## Day 1: Infrastructure Setup (4-6 hours)

### Morning Session (2-3 hours)

**Step 1: Configuration Questions (30 min)**
Answer these before we start:

1. **AWS Region:** us-east-1 (recommended) or eu-west-1?
2. **Database:** Confirm using SQLite on EC2?
3. **Domain:** Use IP address or buy domain?
4. **SSH Access:** Your IP address for security group?
5. **Environment Variables:** Review `.env` file

**Step 2: Create Terraform Modules (2 hours)**
I'll create:
- `terraform/modules/networking/` - VPC, security groups
- `terraform/modules/compute/` - EC2 instance
- `terraform/modules/storage/` - S3 buckets
- `terraform/modules/monitoring/` - CloudWatch

### Afternoon Session (2-3 hours)

**Step 3: Deploy Infrastructure (1 hour)**
```bash
cd terraform
terraform init
terraform plan
terraform apply
```

**Step 4: Verify Resources (30 min)**
- EC2 instance running
- S3 buckets created
- Security groups configured
- CloudWatch alarms set

**Step 5: Initial Server Setup (1-2 hours)**
```bash
ssh -i safarismart-key.pem ubuntu@<ec2-ip>
# Install Python, Nginx, dependencies
```

---

## Day 2: Application Deployment (4-6 hours)

### Morning Session (2-3 hours)

**Step 1: Clone Repository (15 min)**
```bash
cd /opt
git clone https://github.com/owuorviny109/SafariSmart.git safarismart
cd safarismart
```

**Step 2: Setup Python Environment (30 min)**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Step 3: Database Migration (1 hour)**
```bash
# Export from Render
pg_dump $RENDER_DATABASE_URL > render_backup.sql

# Import to SQLite
python manage.py migrate
python manage.py loaddata render_backup.json
```

**Step 4: Configure S3 for Media (30 min)**
```python
# Update settings.py
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_STORAGE_BUCKET_NAME = 'safarismart-media'
```

### Afternoon Session (2-3 hours)

**Step 5: Configure Nginx (1 hour)**
```bash
sudo nano /etc/nginx/sites-available/safarismart
# Configure reverse proxy
sudo systemctl restart nginx
```

**Step 6: Setup Gunicorn (30 min)**
```bash
# Create systemd service
sudo nano /etc/systemd/system/gunicorn.service
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
```

**Step 7: SSL Certificate (1 hour)**
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d safarismart.co.ke
```

---

## Day 3: Testing & Final Setup (2-3 hours)

### Morning Session (2-3 hours)

**Step 1: Application Testing (1 hour)**
- [ ] Homepage loads
- [ ] User registration works
- [ ] Login works
- [ ] Trip wizard works
- [ ] M-Pesa payments work
- [ ] Admin panel accessible
- [ ] Media files upload to S3

**Step 2: Performance Testing (30 min)**
- [ ] No cold starts (instant response)
- [ ] Database queries fast
- [ ] Images load from S3
- [ ] SSL certificate valid

**Step 3: Domain Setup (30 min - Optional)**
If using custom domain:
```bash
# Update DNS A record
safarismart.co.ke -> <ec2-elastic-ip>
```

**Step 4: Monitoring Setup (30 min)**
- [ ] CloudWatch alarms configured
- [ ] Email alerts working
- [ ] Logs streaming to CloudWatch
- [ ] Backup cron job running

---

## Presentation Preparation

### Demo Checklist
- [ ] App loads instantly (no cold starts)
- [ ] Create sample trip to show AI
- [ ] Test M-Pesa payment (sandbox)
- [ ] Show admin panel
- [ ] Demonstrate media persistence
- [ ] Show CloudWatch monitoring

### Talking Points
1. **Problem:** Render has cold starts, media loss, DB expiration
2. **Solution:** AWS deployment with EC2 + S3
3. **Benefits:** 
   - Always-on (no cold starts)
   - Permanent media storage
   - Professional infrastructure
   - Scalable architecture
4. **Cost:** $0 for 9 months, then $8/month

---

## Rollback Plan

If something goes wrong:
1. Keep Render running during migration
2. Can revert DNS to Render
3. Database backed up before migration
4. Can destroy AWS resources: `terraform destroy`

---

## Quick Reference

### Important Commands
```bash
# SSH into EC2
ssh -i safarismart-key.pem ubuntu@<ec2-ip>

# Restart services
sudo systemctl restart gunicorn nginx

# View logs
sudo journalctl -u gunicorn -f
sudo tail -f /var/log/nginx/error.log

# Django management
python manage.py migrate
python manage.py collectstatic
python manage.py createsuperuser

# Terraform
terraform plan
terraform apply
terraform destroy
```

### Important URLs
- EC2 Instance: `http://<ec2-ip>`
- S3 Bucket: `https://s3.console.aws.amazon.com`
- CloudWatch: `https://console.aws.amazon.com/cloudwatch`
- Admin Panel: `http://<ec2-ip>/admin/`

---

## Timeline Summary

| Day | Task | Time | Status |
|-----|------|------|--------|
| 1 | Terraform + Infrastructure | 4-6h | Pending |
| 2 | App Deployment + Migration | 4-6h | Pending |
| 3 | Testing + Domain Setup | 2-3h | Pending |
| **Total** | | **10-15h** | |

---

## Next Steps

1. **Confirm you're ready to start**
2. **Answer configuration questions**
3. **I create Terraform modules**
4. **You deploy infrastructure**
5. **We test together**

**Ready to begin?**
