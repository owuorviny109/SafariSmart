# Codebase Cleanup Report

**Objective:** Audit the repository for redundant, unused, or experimental files prior to Neon DB migration.

---

## 1. Findings Summary

| Category | Count | Description |
| :--- | :--- | :--- |
| **Safe to Delete** | 6 | Utility scripts and temporary fixes that have served their purpose |
| **Conditionally Removable** | 3 | Files that may be needed for reference but are not critical to production |
| **Must Keep** | 4 | Configuration and deployment files critical to the app |

---

## 2. Safe to Delete (High Confidence)
These files are standalone scripts or one-off fixes that are not imported by the main application.

| File Path | Reason for Deletion | Verification |
| :--- | :--- | :--- |
| `fix_endif.py` | One-off script to patch a template syntax error. | Verify `templates/payments/sponsorship.html` has valid syntax. |
| `fix_template.py` | Redundant script similar to `fix_endif.py`. | Same as above. |
| `reset_password.py` | Hardcoded password reset script. Security risk if left in repo. | Use `python manage.py changepassword` instead. |
| `temp_destinations_section.html` | Temporary HTML snippet used during development. | Confirm contents are already in `landing.html`. |
| `temp_js.txt` | Temporary JavaScript snippet. | Confirm logic is moved to `static/js`. |
| `check_emails.py` | Ad-hoc email debugging script. | Use Django Shell or Admin for debugging. |

**Recommendation:** Delete these immediately to reduce noise.

---

## 3. Conditionally Removable (Medium Confidence)
These files are generally useful for debugging but not strictly required for the app to run.

| File Path | Reason | Verification |
| :--- | :--- | :--- |
| `test_s3_upload.py` | Ad-hoc script to test S3 permissions. | Useful to keep *locally* for debugging, but can be removed from prod. |
| `test_smtp.py` | Ad-hoc script to verify email config. | Same as above. |
| `load_config_data.py` | Initial data loader. | If data is already in DB, this is redundant. However, it's useful for setting up *new* environments. **Recommendation: Move to `core/management/commands/load_initial_data.py`** instead of deleting. |

---

## 4. Must Keep (Critical)
**DO NOT DELETE** the following files, as they are essential for deployment and operation:

| File Path | Critical Function |
| :--- | :--- |
| `build.sh` | **REQUIRED by Render** to build the app (install deps, migrate, collectstatic). |
| `render.yaml` | **REQUIRED by Render** for Infrastructure-as-Code definitions. |
| `AWS_DEPLOYMENT_PLAN.md` | Provides context for the current architecture. |
| `TASK.md` | Contains the current active migration plan. |

---

## 5. Clean Up Plan

### Step 1: Remove Temporary Scripts
Run the following commands to delete confirmed junk files:

```bash
# Delete safe-to-remove files
rm fix_endif.py fix_template.py reset_password.py temp_destinations_section.html temp_js.txt check_emails.py
```

### Step 2: Organize Debug Scripts (Optional)
Instead of deleting debugging tools, move them to a dedicated folder so they don't clutter the root:

```bash
mkdir -p dev_scripts
mv test_s3_upload.py test_smtp.py dev_scripts/
mv load_config_data.py dev_scripts/
```

### Step 3: Verify
Run the application locally to ensure no imports were broken (unlikely, as these are standalone scripts).

```bash
python manage.py check
```

---

**Status:** Ready to execute Step 1.
