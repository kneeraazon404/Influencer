# Influencer

A production-ready Python-based Instagram scraping tool built on Selenium. Crawl user profiles, scrape posts by username or hashtag, and automate engagement — all from the command line.

[![Tests](https://img.shields.io/badge/tests-29%20passing-brightgreen)](tests/)
[![Python](https://img.shields.io/badge/python-3.8+-blue)](requirements.txt)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

---

## Features

- **Profile Crawler** — extract follower count, following, post count, bio, and profile photo
- **Post Crawler** — scrape posts (image URLs, captions, likes, comments) by username or hashtag
- **Full Post Details** — optionally collect mentions, hashtags, likers, and per-comment data
- **Auto-Liker** — automate likes on posts under a given hashtag
- **Headless Mode** — run without a visible browser window
- **Production Ready** — comprehensive test suite, error handling, and retry mechanisms

---

## Project Structure

```bash
Influencer/
├── crawler.py              # Main CLI entry point
├── liker.py                # Auto-like CLI entry point
├── inscrawler/
│   ├── __init__.py
│   ├── browser.py          # Selenium Chrome wrapper
│   ├── crawler.py          # InsCrawler class (login, scraping logic)
│   ├── fetch.py            # DOM extraction helpers
│   ├── settings.py         # Feature flags (fetch_comments, etc.)
│   ├── utils.py            # Helpers: retry, sleep, int parsing
│   ├── exceptions.py       # RetryException
│   ├── secret.py           # Credentials (gitignored — copy from secret.py.dist)
│   ├── secret.py.dist      # Credential template
│   └── bin/                # Optional local chromedriver override
├── tests/
│   ├── test_fetch.py       # Parser unit tests
│   ├── test_settings.py    # Settings/flags unit tests
│   └── test_utils.py       # Utility function unit tests
├── requirements.txt
├── pytest.ini
├── .flake8                 # Code quality configuration
└── LICENSE                 # MIT License
```

---

## Prerequisites

- Python 3.8+
- Google Chrome **or** Chromium installed
- ChromeDriver matching your browser version

ChromeDriver is auto-detected from `$PATH`. To use a project-local override, place the binary at `inscrawler/bin/chromedriver`.

---

## Installation

### Quick Start

```bash
git clone https://github.com/kneeraazon404/Influencer.git
cd Influencer
pip install -r requirements.txt
```

### Configuration

1. **Set up credentials:**

```bash
cp inscrawler/secret.py.dist inscrawler/secret.py
```

1. **Configure Instagram credentials:**

Edit `inscrawler/secret.py` — either set environment variables or hardcode values:

```python
import os

username = os.environ.get('USERNAME', 'your_username')
password = os.environ.get('PASSWORD', 'your_password')
```

1. **Environment Variables (Recommended):**

```bash
export USERNAME="your_instagram_username"
export PASSWORD="your_instagram_password"
```

### ChromeDriver Setup

ChromeDriver is auto-detected from `$PATH`. To use a project-local override, place the binary at `inscrawler/bin/chromedriver`.

**Ubuntu/Debian:**

```bash
sudo apt-get update
sudo apt-get install chromium-browser chromium-chromedriver
```

**macOS (with Homebrew):**

```bash
brew install chromedriver
```

**Windows:**
Download from [ChromeDriver downloads](https://chromedriver.chromium.org/downloads) and add to PATH.

---

## Usage

### Crawl posts by user

```bash
python crawler.py posts -u <username> -n <count> -o output.json
```

### Crawl posts by hashtag

```bash
python crawler.py hashtag -t <tag> -n <count> -o output.json
```

### Fetch user profile

```bash
python crawler.py profile -u <username>
```

### Fetch profile via page script data

```bash
python crawler.py profile_script -u <username>
```

### Full post details (comments, likes, likers, mentions)

```bash
python crawler.py posts_full -u <username> -n 10 \
  --fetch_comments \
  --fetch_likes_plays \
  --fetch_likers \
  --fetch_mentions \
  --fetch_hashtags
```

### Auto-like posts under a hashtag

```bash
python liker.py <hashtag> -n <count>
# Example: like up to 50 posts tagged #travel
python liker.py travel -n 50
```

Show browser window during any command (useful for debugging):

```bash
python crawler.py posts -u <username> -n 5 --debug
```

---

## Testing

### Run All Tests

```bash
pytest
```

### Run Tests with Coverage

```bash
pip install pytest-cov
pytest --cov=inscrawler --cov-report=html
```

### Run Specific Test Categories

```bash
# Parser tests
pytest tests/test_fetch.py -v

# Settings tests
pytest tests/test_settings.py -v

# Utility tests
pytest tests/test_utils.py -v
```

All 29 tests cover parsers, settings flags, utility functions, and the retry decorator with **100% pass rate**.

---

## Production Deployment

### Environment Setup

For production environments, use environment variables instead of hardcoded credentials:

```bash
# Production environment variables
export USERNAME="your_production_username"
export PASSWORD="your_production_password"
export PYTHONPATH="/path/to/influencer:$PYTHONPATH"
```

### Docker Deployment

Create a `Dockerfile` for containerized deployment:

```dockerfile
FROM python:3.9-slim

# Install Chrome and ChromeDriver
RUN apt-get update && apt-get install -y \
    chromium-browser \
    chromium-chromedriver \
    && rm -rf /var/lib/apt/lists/*

# Set up application
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

# Set environment variables
ENV USERNAME=""
ENV PASSWORD=""

CMD ["python", "crawler.py", "--help"]
```

### Monitoring and Logging

The tool includes built-in retry mechanisms and error handling. For production monitoring:

1. **Log scraping activities**
2. **Monitor rate limits**
3. **Track failed attempts**
4. **Implement alerting for login failures**

---

## Code Quality

### Linting

```bash
# Install flake8
pip install flake8

# Run linting
flake8 inscrawler/ crawler.py liker.py
```

### Code Style

The project follows PEP 8 guidelines with configuration in `.flake8`:

- Max line length: 79 characters
- Ignored: E203, E266, E501, W503, F403, F401

---

## Troubleshooting

### Common Issues

1. **ChromeDriver Version Mismatch**

   ```bash
   # Check Chrome version
   google-chrome --version

   # Download matching ChromeDriver
   # Place in inscrawler/bin/chromedriver
   ```

2. **Login Failures**
   - Verify credentials in `inscrawler/secret.py`
   - Check for 2FA requirements
   - Ensure Instagram account is not blocked

3. **Scraping Failures**
   - Instagram frequently updates DOM structure
   - Update CSS selectors in `inscrawler/fetch.py`
   - Use `--debug` flag to inspect issues

4. **Rate Limiting**
   - Implement delays between requests
   - Use randomized sleep intervals
   - Monitor for 429 HTTP responses

### Debug Mode

Use the `--debug` flag to run with visible browser window:

```bash
python crawler.py posts -u <username> -n 5 --debug
```

---

## API Reference

### Main Commands

| Command | Description | Example |
| --- | ----------- | ------- |
| `posts` | Crawl posts by user | `python crawler.py posts -u username -n 10 -o output.json` |
| `hashtag` | Crawl posts by hashtag | `python crawler.py hashtag -t travel -n 20 -o output.json` |
| `profile` | Get user profile info | `python crawler.py profile -u username` |
| `profile_script` | Get profile via script data | `python crawler.py profile_script -u username` |
| `posts_full` | Full post details | `python crawler.py posts_full -u username -n 10 --fetch_comments` |

### Options

| Option | Description |
| ------ | ----------- |
| `-u, --username` | Instagram username |
| `-t, --tag` | Hashtag name |
| `-n, --number` | Number of posts to fetch |
| `-o, --output` | Output JSON file |
| `--fetch_comments` | Include comment data |
| `--fetch_likes_plays` | Include like counts |
| `--fetch_likers` | Include liker information |
| `--fetch_mentions` | Include mention data |
| `--fetch_hashtags` | Include hashtag data |
| `--debug` | Show browser window |

---

## Maintenance

### Regular Updates

1. **Update dependencies:**

   ```bash
   pip install --upgrade -r requirements.txt
   ```

2. **Update ChromeDriver:**
   - Check Chrome version regularly
   - Download matching ChromeDriver
   - Test functionality after updates

3. **Monitor Instagram changes:**
   - Watch for DOM structure changes
   - Update CSS selectors as needed
   - Test scraping functionality weekly

### Security Considerations

- Never commit credentials to version control
- Use environment variables in production
- Rotate Instagram credentials regularly
- Monitor for account suspensions
- Respect Instagram's rate limits

---

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

---

## Disclaimer

This tool is for **educational purposes only**. Automated scraping and interaction with Instagram may violate their [Terms of Service](https://help.instagram.com/581066165581870). Use responsibly and at your own risk.

**Important:** Always respect Instagram's API guidelines and rate limits. The authors are not responsible for any account suspensions or legal issues resulting from misuse of this tool.
