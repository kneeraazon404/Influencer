# Influencer 📸

### Advanced Instagram Scraping & Automation Tool

**Influencer** is a comprehensive Python-based tool designed for automating interactions and extracting data from Instagram. Whether you are a marketer, researcher, or developer, this project provides a modular codebase to crawl profiles, fetch posts, analyze hashtags, and automate engagement like liking posts.

---

## 🚀 Key Features

- **Profile Crawler**: Extract detailed user profile information.
- **Post Crawler**: Scrape posts from specific users or hashtags.
- **Engagement Automation**: Auto-like posts based on hashtags to increase visibility.
- **Comment Fetcher**: Interactive tool to download comments from specific posts.
- **Headless Mode**: Run crawling tasks in the background without a visible browser window.

---

## 🛠️ Project Structure

The project is organized into modular scripts for different tasks:

- **`crawler.py`**: The main CLI tool for crawling posts, profiles, and hashtags.
- **`liker.py`**: A dedicated script for automating "likes" on posts under specific hashtags.
- **`fetchComments`**: A script to interactively fetch comments from a specific photo.
- **`inscrawler/`**: The core library containing the Selenium browser logic and scraping mechanisms.
- **`insta_scraper/`** & **`instagram/`**: Alternative scraping implementations and sandbox scripts.

---

## 📋 Prerequisites

- **Python 3.6+**
- **Google Chrome** browser installed.
- **ChromeDriver**: The project expects a `chromedriver` binary in `inscrawler/bin/chromedriver`.

---

## ⚙️ Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/kneeraazon404/Influencer.git
   cd Influencer
   ```

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Setup ChromeDriver**:
   - Download the version of [ChromeDriver](https://chromedriver.chromium.org/downloads) that matches your installed Chrome version.
   - Place the `chromedriver` executable in the `inscrawler/bin/` directory.
   - _Note: You may need to create the `bin` directory if it doesn't exist._

   ```bash
   mkdir -p inscrawler/bin
   mv /path/to/downloaded/chromedriver inscrawler/bin/
   chmod +x inscrawler/bin/chromedriver
   ```

---

## 📖 Usage

### 1. Crawling Data (`crawler.py`)

This script supports multiple modes. Run it from the command line:

**Fetch Posts by User:**

```bash
python crawler.py posts -u <username> -n <number_of_posts> -o ./output
```

_Example:_ `python crawler.py posts -u cleaning_services_nepal -n 50 -o ./output`

**Fetch Posts by Hashtag:**

```bash
python crawler.py hashtag -t <tag> -o ./output
```

_Example:_ `python crawler.py hashtag -t travel -o ./output`

**Fetch User Profile:**

```bash
python crawler.py profile -u <username> -o ./output
```

### 2. Auto-Liker (`liker.py`)

Automate liking posts to grow engagement.

```bash
python liker.py <hashtag> --number <count>
```

_Example_: Like 100 posts with the hashtag #coding:

```bash
python liker.py coding -n 100
```

### 3. Fetch Comments (`fetchComments`)

Run this interactive script to download comments from a specific post. You will need to provide your login credentials interactively to access the post details.

```bash
python fetchComments
```

---

## ⚠️ Disclaimer

This tool is for **educational purposes only**. Automated scraping and interaction with Instagram may violate their [Terms of Use](https://help.instagram.com/581066165581870). Use responsibly and at your own risk. The authors are not responsible for any account bans or restrictions.
