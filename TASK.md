# Task: Migrate SafariSmart Database to Neon (Free Tier)

**Objective:** Restore database functionality by migrating from the (deleted) Render PostgreSQL instance to a persistent, free-tier Neon PostgreSQL database, while maintaining the application on Render.

---

## 1. Prerequisites Checklist
- [ ] Access to [Neon.tech](https://neon.tech)
- [ ] Access to [Render Dashboard](https://dashboard.render.com)
- [ ] Local development environment configured with Python 3.11+
- [ ] `dj_database_url` and `psycopg` installed locally

---

## 2. Neon Database Setup
1. **Create Project:**
   - Log in to Neon Console.
   - Create a new project named `safarismart`.
   - Select the region closest to your users (e.g., AWS Frankfurt `eu-central-1` or US East).
   
2. **Get Connection String:**
   - On the Dashboard, locate the **Connection Details**.
   - Select "Pooled connection" (Recommended for serverless).
   - Copy the connection string. It will look like:
     ```
     postgres://neondb_owner:***********@ep-icy-rain-123456.eu-central-1.aws.neon.tech/neondb?sslmode=require
     ```

---

## 3. Django Configuration Updates
*Note: These changes should already be applied in `settings.py` based on recent updates.*

1. **Verify `requirements.txt`:**
   Ensure these packages are present:
   ```text
   dj-database-url==2.1.0
   psycopg[binary]==3.2.3
   ```

2. **Verify `settings.py`:**
   Check that `DATABASES` is configured to use environment variables with a fallback:
   ```python
   import dj_database_url
   
   DATABASES = {
       'default': dj_database_url.config(
           default=config('DATABASE_URL', default='sqlite:///db.sqlite3'),
           conn_max_age=600,
           conn_health_checks=True,
       )
   }
   ```
   **Checkpoint:** Run `python manage.py check` locally to ensure no configuration errors.

---

## 4. Render Configuration
1. **Update Environment Variables:**
   - Go to Render Dashboard -> Select `safarismart` Web Service -> **Environment**.
   - Delete any old database variables (e.g., `RENDER_LEGACY_DB_URL`).
   - Add/Update `DATABASE_URL`:
     - **Key:** `DATABASE_URL`
     - **Value:** Paste the Neon connection string from Step 2.
   
2. **Verify Python Version:**
   - Ensure `PYTHON_VERSION` is set to `3.11.9` (matches local/tested).

---

## 5. Deployment & Migration
1. **Deploy Changes:**
   - Commit any changes to `settings.py` or `requirements.txt`.
   - Push to `main`:
     ```bash
     git add requirements.txt safarismart/settings.py
     git commit -m "chore: configure neon database support"
     git push origin main
     ```

2. **Wait for Build:**
   - Monitor the Render deployment logs.
   - **Verification:** Ensure the Build Command `./build.sh` runs successfully.

3. **Verify Migrations:**
   - The `build.sh` script should automatically run `python manage.py migrate`.
   - Check logs for: `Applying <app>.000X_initial... OK`.

4. **Create Superuser (If needed):**
   - Since the DB utilizes a fresh schema, you need a new admin.
   - Render Shell:
     ```bash
     python manage.py createsuperuser
     ```

---

## 6. Post-Migration Checks
1. **Connectivity:**
   - Visit the live site URL properly.
   - Navigate to `/admin` and log in with the new superuser.
   
2. **Persistence Test:**
   - Create a dummy Destination or Blog Post via Admin.
   - Trigger a manual interaction (e.g., sign up a test user).
   - **Verification:** Check the Neon Console "Tables" view to see the rows.

3. **Performance:**
   - Ensure pages load without database timeout errors.

---

## 7. Common Pitfalls & Solutions
- **Connection Limits:** If you see `too many clients`, ensure you are using the *Pooled* connection string from Neon, not the Direct one.
- **SSL Errors:** Neon requires SSL. Ensure `?sslmode=require` is at the end of the `DATABASE_URL`.
- **Missing Data:** Remember, the old Render DB is gone. This is a clean slate. You must re-populate initial data (fixtures) if you have them.

---

## 8. Completion Checklist
- [ ] `DATABASE_URL` updated in Render
- [ ] Deployment successful
- [ ] Database tables created in Neon
- [ ] Superuser created
- [ ] Admin panel accessible
- [ ] Site functionally verified

**Status:** Ready to Start
