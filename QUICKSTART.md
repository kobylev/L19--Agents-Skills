# Quick Start Guide

Get up and running with the Homework Grading System in 10 minutes!

## Prerequisites Checklist

- [ ] Python 3.10+ installed
- [ ] Git installed
- [ ] Google Cloud account
- [ ] Gemini API key

## Installation (5 minutes)

### 1. Setup Environment

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure APIs

**Gmail API:**
1. Visit [Google Cloud Console](https://console.cloud.google.com/)
2. Create project → Enable Gmail API → Create OAuth Desktop credentials
3. Download `credentials.json` → Move to `config/`

**Gemini API:**
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create API key
3. Copy `.env.example` to `.env` and add key:
   ```bash
   cp .env.example .env
   # Edit .env: GEMINI_API_KEY=your_key_here
   ```

### 3. Create Student Mapping

```bash
python create_student_mapping.py
# This creates data/students_mapping.xlsx with example data
# Edit the file with your actual student emails and names
```

## First Run (5 minutes)

### 1. Start Application

```bash
python src/main.py
```

### 2. Authenticate Gmail

- Browser opens automatically
- Sign in to kobylev@gmail.com
- Grant permissions
- Done! Token saved for future use

### 3. Run Test Mode

1. Select **"1. Test Mode"** (processes 1 email)
2. Select **"5. Run All Steps"**
3. Watch the magic happen! ✨

### 4. Check Results

**Generated Files:**
```bash
ls data/output/
# file_1_2.xlsx - Email data
# file_2_3.xlsx - Grades
# file_3_4.xlsx - Feedback
```

**Gmail Drafts:**
- Open Gmail → Drafts folder
- See your generated draft!

## Workflow Overview

```
┌─────────────────────┐
│ 1. Search Emails    │ → Finds homework submissions
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│ 2. Clone & Grade    │ → Analyzes Python code
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│ 3. Generate Feedback│ → AI creates personalized messages
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│ 4. Create Drafts    │ → Saves in Gmail
└─────────────────────┘
```

## Processing Modes

### Test Mode (Recommended First)
- Processes 1 most recent email
- Perfect for testing
- Fast execution

### Batch Mode
- Process N emails (you choose)
- Good for weekly grading
- Balances speed and volume

### Full Mode
- Process ALL unread emails
- Use for end-of-term
- Longest execution time

## Email Requirements

Your students must send emails with:

**Subject:** (case-insensitive)
```
self check of homework 5
```

**Body:** (must include)
```
https://github.com/username/repository-name.git
```

## Grading Formula

```
Grade = (Lines in files >150) / (Total Python lines) × 100
```

**Example:**
- File1.py: 200 lines
- File2.py: 100 lines
- File3.py: 50 lines
- Total: 350 lines
- Large files (>150): 200 lines
- **Grade: 57.14%**

## Feedback Styles

| Grade Range | Style               | Description                      |
|-------------|---------------------|----------------------------------|
| 90-100      | Donald Trump        | Enthusiastic, superlatives       |
| 70-89       | Shahar Hason        | Witty, humorous                  |
| 55-69       | Constructive        | Encouraging, actionable advice   |
| <55         | Dudi Amsalem        | Brash, confrontational, firebrand |

## Troubleshooting

### "credentials.json not found"
```bash
# Check file location
ls config/credentials.json
# Should exist - if not, download from Google Cloud Console
```

### "No matching emails found"
- Verify emails are **unread**
- Check subject matches pattern exactly
- Test in Gmail search: `is:unread subject:"self check of homework"`

### "Failed to clone repository"
- Repository must be **public**
- URL must be valid GitHub URL
- Check network connection

### "Gemini API error"
```bash
# Check API key in .env
cat .env | grep GEMINI_API_KEY
# Should show: GEMINI_API_KEY=your_key_here
```

## Tips & Tricks

### Speed Up Processing
```bash
# Edit .env
MAX_CLONE_WORKERS=10     # More parallel clones (default: 5)
CLONE_TIMEOUT=30         # Faster timeout (default: 60)
GEMINI_REQUEST_DELAY=0   # No delay (may hit rate limit)
```

### Debug Mode
```bash
# Edit .env
LOG_LEVEL=DEBUG
# Check logs/debug.log for detailed info
```

### Reset Everything
1. Select menu option **"6. Reset"**
2. Confirm with `yes`
3. Deletes all generated files
4. Start fresh!

## Next Steps

✅ **You're ready!** Now you can:

1. **Add Real Students**
   - Edit `data/students_mapping.xlsx`
   - Add actual student emails and names

2. **Configure Preferences**
   - Edit `.env` for your settings
   - Adjust workers, timeouts, delays

3. **Process Real Homework**
   - Switch to Batch or Full mode
   - Grade all submissions at once

4. **Automate**
   - Set up cron job (Linux/Mac)
   - Schedule task (Windows)
   - Run automatically!

## Common Workflows

### Weekly Grading
```bash
python src/main.py
→ Select "2. Batch Mode"
→ Enter: 20  # Last week's submissions
→ Select "5. Run All Steps"
→ Done! Check Gmail drafts
```

### End of Semester
```bash
python src/main.py
→ Select "3. Full Mode"
→ Select "5. Run All Steps"
→ Go get coffee ☕ (takes ~30 min for 100 emails)
```

### Regrade with Different Feedback
```bash
python src/main.py
→ Select "3. Generate Feedback"  # Regenerate only
→ Select "4. Create Drafts"      # Recreate drafts
→ No need to clone repos again!
```

## Help & Support

📖 **Full Documentation:** [README.md](README.md)
🔧 **Installation Guide:** [INSTALL.md](INSTALL.md)
📋 **Specifications:** [PRD.md](PRD.md)

**Questions?** Check the logs:
```bash
tail -f logs/app.log  # Real-time log monitoring
```

---

**Happy Grading! 🎓**

Generated with ❤️ by Claude Code
