# Changelog

All notable changes to the Homework Grading System will be documented in this file.

## [1.0.1] - 2025-11-20

### Changed
- **Dudi Amsalem Feedback Style (Grade <55)**: Updated from humorous/motivational to brash/confrontational/firebrand speaking style
  - Updated prompt in `src/services/gemini_service.py` to reflect direct and blunt criticism, no sugar coating, challenging tone with tough love approach
  - Updated fallback feedback to be confrontational and wake-up call style
  - Updated documentation across all files (README.md, QUICKSTART.md, PRD.md, IMPLEMENTATION_SUMMARY.md)

### Details
The Dudi Amsalem feedback style for students scoring below 55% has been changed to better reflect a firebrand speaking style:

**Old Style:**
- Humorous, motivational
- Self-deprecating humor
- "We've all been there" vibe
- Empathetic and encouraging

**New Style:**
- Brash, confrontational
- Direct and blunt criticism
- No sugar coating
- Challenging tone that pushes students to do better
- Tough love approach
- Wake-up call style

**Example Fallback Message (Old):**
> "Hey, 45% is a start! We all struggle with code sometimes. I once spent 3 hours debugging a missing semicolon. Keep pushing!"

**Example Fallback Message (New):**
> "A 45%? Really? This is unacceptable work. You need to wake up and take this seriously. Stop making excuses and actually put in the effort. Your code quality reflects your commitment - and right now, it's severely lacking!"

### Files Modified
1. `src/services/gemini_service.py` - Updated prompt and fallback messages
2. `README.md` - Updated feedback style description
3. `QUICKSTART.md` - Updated feedback styles table
4. `PRD.md` - Updated feedback style specification and prompts
5. `IMPLEMENTATION_SUMMARY.md` - Updated features list

## [1.0.0] - 2025-11-20

### Added
- Initial release of Homework Grading System
- Complete implementation of 4-step processing workflow
- Interactive menu system (mode selection + main menu)
- Gmail API integration for email processing
- Multi-threaded repository cloning and analysis
- Gemini API integration for AI-powered feedback
- Email draft creation with student name mapping
- Excel file generation for all processing steps
- Comprehensive logging system
- Configuration management
- Input validation and security features
- Complete documentation suite (PRD, README, INSTALL, QUICKSTART guides)

### Features
- **Step 1**: Email search and parsing
- **Step 2**: Repository cloning and grading (multi-threaded)
- **Step 3**: AI feedback generation (4 styles)
- **Step 4**: Email draft creation
- **Modes**: Test, Batch, Full processing modes
- **Logging**: Colored console output and file logging
- **Security**: Email hashing, OAuth2, input validation

---

**Version Format:** [MAJOR.MINOR.PATCH]
- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes and minor updates
