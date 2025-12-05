# S3 Setup for SafariSmart (Render + S3)
## Simple Image Storage Solution

**Goal:** Use AWS S3 only for image storage while keeping everything else on Render

**Cost:** ~$0.02/month (basically free)

---

## Step 1: Create S3 Bucket (5 minutes)

### 1.1 Login to AWS Console
1. Go to https://console.aws.amazon.com/
2. Login with your AWS account

### 1.2 Create S3 Bucket
1. Go to S3 service
2. Click "Create bucket"
3. **Bucket name:** `safarismart-media-prod` (must be globally unique)
4. **Region:** us-east-1
5. **Block Public Access:** UNCHECK "Block all public access"
6. Check the warning acknowledgment
7. Click "Create bucket"

### 1.3 Configure Bucket
1. Click on your bucket name
2. Go to "Permissions" tab
3. Click "Bucket Policy"
4. Paste this policy:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::safarismart-media-prod/*"
        }
    ]
}
```

5. Click "Save changes"

---

## Step 2: Create IAM User (5 minutes)

### 2.1 Create User
1. Go to IAM service
2. Click "Users" → "Create user"
3. **User name:** `safarismart-s3-user`
4. Click "Next"

### 2.2 Set Permissions
1. Select "Attach policies directly"
2. Click "Create policy"
3. Select JSON tab
4. Paste this policy:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:GetObject",
                "s3:DeleteObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::safarismart-media-prod",
                "arn:aws:s3:::safarismart-media-prod/*"
            ]
        }
    ]
}
```

5. Click "Next"
6. **Policy name:** `SafariSmartS3Access`
7. Click "Create policy"
8. Go back to user creation, refresh policies
9. Search and select `SafariSmartS3Access`
10. Click "Next" → "Create user"

### 2.3 Create Access Keys
1. Click on the user you just created
2. Go to "Security credentials" tab
3. Click "Create access key"
4. Select "Application running outside AWS"
5. Click "Next" → "Create access key"
6. **IMPORTANT:** Copy and save:
   - Access key ID
   - Secret access key
7. Click "Done"

---

## Step 3: Update Django Settings (10 minutes)

### 3.1 Install Required Packages

Add to `requirements.txt`:
```
boto3==1.34.0
django-storages==1.14.2
```

### 3.2 Update settings.py

Add this to `safarismart/settings.py`:

```python
# AWS S3 Configuration
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME', 'safarismart-media-prod')
AWS_S3_REGION_NAME = 'us-east-1'
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}
AWS_DEFAULT_ACL = 'public-read'
AWS_LOCATION = 'media'

# Use S3 for media files
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_LOCATION}/'
```

### 3.3 Update .env file

Add these to your `.env`:
```
AWS_ACCESS_KEY_ID=your-access-key-id
AWS_SECRET_ACCESS_KEY=your-secret-access-key
AWS_STORAGE_BUCKET_NAME=safarismart-media-prod
```

---

## Step 4: Update Render Environment Variables (5 minutes)

1. Go to Render Dashboard
2. Select your web service
3. Go to "Environment" tab
4. Add these variables:
   - `AWS_ACCESS_KEY_ID` = your-access-key-id
   - `AWS_SECRET_ACCESS_KEY` = your-secret-access-key
   - `AWS_STORAGE_BUCKET_NAME` = safarismart-media-prod
5. Click "Save Changes"
6. Render will automatically redeploy

---

## Step 5: Test (5 minutes)

1. Wait for Render to finish deploying
2. Go to your admin panel
3. Upload a destination image
4. Check if image appears
5. Redeploy the app (to test persistence)
6. Image should still be there!

---

## Verification

**Check S3:**
1. Go to AWS S3 Console
2. Open your bucket
3. You should see uploaded images in `media/` folder

**Check Django:**
1. Inspect image URL in browser
2. Should be: `https://safarismart-media-prod.s3.amazonaws.com/media/...`

---

## Cost Breakdown

| Item | Free Tier | Your Usage | Cost |
|------|-----------|------------|------|
| Storage | 5 GB | ~0.5 GB | $0 |
| GET requests | 20,000/month | ~1,000/month | $0 |
| PUT requests | 2,000/month | ~100/month | $0 |
| **Total** | | | **$0/month** |

**After Free Tier (12 months):**
- Storage: $0.023/GB = ~$0.01/month
- Requests: ~$0.01/month
- **Total: ~$0.02/month**

---

## Troubleshooting

### Images not uploading
- Check AWS credentials in Render
- Check bucket policy allows public read
- Check IAM user has PutObject permission

### Images not displaying
- Check bucket is public
- Check CORS configuration
- Check image URL format

### Permission denied
- Verify IAM policy is correct
- Verify access keys are correct
- Check bucket name matches

---

## Rollback Plan

If something goes wrong:
1. Remove S3 settings from `settings.py`
2. Remove AWS env vars from Render
3. Redeploy
4. Back to local storage (images will be lost on redeploy)

---

## Next Steps

After this works:
1. Migrate existing images to S3
2. Set up lifecycle rules (delete old versions)
3. Consider CloudFront CDN for faster delivery (optional)

---

## Summary

**What you're doing:**
- ✅ Keep Render (free)
- ✅ Add S3 for images (~$0/month)
- ✅ Images persist forever
- ✅ No complex infrastructure
- ✅ No risk of high AWS bills

**Total time:** 30 minutes
**Total cost:** ~$0/month
