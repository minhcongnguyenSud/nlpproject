# AI Newsletter Generator - Streamlit Edition

## What This Does

This program automatically creates newsletters for you using a modern web interface! Here's how it works:

1. **Gets News Articles** - Visits 10+ local Sudbury news websites and collects articles from the past week
2. **AI Makes Summaries** - Uses artificial intelligence to create short summaries  
3. **Creates Newsletter** - Makes a beautiful HTML newsletter
4. **Web Interface** - Clean, modern Streamlit web app for easy use

## Super Easy Setup

### What You Need First
- Python installed on your computer
- A free AI account (we'll show you how!)

### Step 1: Get Your AI Key
1. Go to https://console.mistral.ai/
2. Sign up for free
3. Get your API key (like a password for AI)

### Step 2: Setup the Program
```bash
# Copy the example file
cp .env.example .env

# Edit the .env file and add your API key
# Change: MISTRAL_API_KEY=your_api_key_here
```

### Step 3: Activate Environment & Install Requirements
```bash
# Activate the virtual environment
source .venv/bin/activate  # On Mac/Linux
# OR
.venv\Scripts\activate     # On Windows

# Install requirements
pip install -r requirements.txt
```

### Step 4: Test Everything Works
```bash
# Run basic setup tests
python tests/test_setup.py

# Or run all tests
python tests/run_tests.py

# Or run the simple validation test
python tests/simple_test.py
```

### Step 5: Run the Program!
```bash
# Start the Streamlit web interface
python -m streamlit run streamlit_app.py --server.port 8501
```

Then open your browser to: **http://localhost:8501**

That's it! Use the clean web interface to generate and view newsletters!

## How to Use the Web Interface

### Main Features:
1. **Generate Newsletter** - Click the big button to create a new newsletter
2. **View Recent Newsletters** - Browse all your generated newsletters
3. **Full-Page Viewer** - Click "View" to see newsletters in full-screen
4. **Download** - Save newsletters to your computer
5. **Auto-Refresh** - List updates automatically when new newsletters are created

### Two Ways to Use This

### Way 1: Streamlit Web Interface (Recommended!)
```bash
python -m streamlit run streamlit_app.py --server.port 8501
```
Then open your browser to: http://localhost:8501
- Clean, modern interface
- Full-page newsletter viewer
- Easy generation and management

### Way 2: Command Line (Simple)
```bash
python main.py          # Make a newsletter
python main.py --help   # Get help
```

## Understanding the Code (For Learning)

```text
streamlit_app.py           # ⭐ NEW! Modern web interface (START HERE!)
main.py                    # Command line version 
input/                     # Raw scraped articles (before AI processing)
output/                    # Final newsletters (after AI processing)
tests/                     # All test files organized here
├── run_tests.py          # Test runner for all tests
├── test_setup.py         # Setup validation test
├── simple_test.py        # Simple validation test
└── test_*.py             # Individual component tests
src/
├── core/config.py         # Settings and configuration  
├── utils/
│   ├── utils.py          # Helper functions
│   └── mistral_utils.py  # Mistral AI integration utilities
├── newsletter_generator/  # The main magic happens here
│   ├── scraper.py        # Gets articles from websites
│   ├── smart_analyzer.py # NLP content analysis
│   └── simple_categorized_summarizer.py  # AI summarization
└── web/                  # Old web components (deprecated)
WORKFLOW.md               # Complete project documentation
```

### Key Files & Folders (What Each Does)

- **streamlit_app.py** - ⭐ **NEW!** Modern web interface with full-page newsletter viewer
- **main.py** - Command line version (still works!)
- **tests/** - All test files organized in one place with proper structure
- **tests/run_tests.py** - Runs all tests automatically
- **input/** - Raw scraped articles saved as JSON files (great for learning!)
- **output/** - Final HTML newsletters ready to view in the web interface
- **src/utils/mistral_utils.py** - Handles Mistral AI API integration and communication
- **src/newsletter_generator/scraper.py** - Shows how to get FULL content from websites (enhanced!)
- **src/newsletter_generator/simple_categorized_summarizer.py** - Shows how to use AI APIs (artificial intelligence)
- **src/newsletter_generator/smart_analyzer.py** - Advanced NLP content analysis
- **WORKFLOW.md** - Complete technical documentation and workflow guide

## Common Problems & Easy Fixes

### "No API key found" 
```bash
# Fix: Make sure your .env file has your API key
# Edit .env file and add: MISTRAL_API_KEY=your_key_here
```

### "No articles found"
```bash
# Fix: Check your internet connection and try again
python main.py
```

### "Module not found" 
```bash
# Fix: Install the requirements
pip install -r requirements.txt
```

### "Browser error"
```bash
# Fix: Install the browser
playwright install chromium
```

## What You'll Learn

This project teaches you:

- **Modern Web Development**: Build clean interfaces with Streamlit
- **Web Scraping**: How to get FULL article content from multiple news sources automatically
- **AI APIs**: How to use artificial intelligence in your programs  
- **Full-Page UI**: Create responsive, full-screen document viewers
- **File Operations**: How to save and load files
- **Project Organization**: How to structure Python projects properly
- **Data Pipeline**: See the data flow from raw scraped text → AI summaries → final newsletter
- **Advanced NLP**: Content quality analysis and automatic categorization
- **Deduplication**: Remove duplicate articles from multiple sources
- **Testing**: How to organize and run tests for your code
- **Docker Deployment**: Container-based application deployment

**Pro Tip**: Check the `input/` folder to see raw scraped articles with FULL content before AI processing!

**Documentation**: Read `WORKFLOW.md` for complete technical documentation and workflow details!

## News Sources

The scraper gets articles from these 10+ Northern Ontario news sources:

- **sudbury.com** - The Sudbury Star newspaper
- **northernnews.ca** - Northern News coverage
- **baytoday.ca** - North Bay news and events
- **sootoday.com** - Sault Ste. Marie news
- **timminstoday.com** - Timmins local news
- **nugget.ca** - The North Bay Nugget
- **tbnewswatch.com** - Thunder Bay news coverage
- **nwonewswatch.com** - Northwestern Ontario news
- **northernontariobusiness.com** - Northern Ontario business news
- **news.ontario.ca** - Government of Ontario news
- **ctvnews.ca/northern-ontario** - CTV News Northern Ontario
- **cbc.ca/news** - CBC News coverage
- **thestar.com** - Toronto Star national coverage
- **nationalpost.com** - National Post coverage

**Enhanced Coverage**: The system now processes hundreds of articles from multiple sources, with advanced deduplication and AI-powered categorization for comprehensive Northern Ontario news coverage.

Perfect for staying informed about Northern Ontario!

## Docker Support 🐳

Run the newsletter generator in a containerized environment:

### Quick Docker Setup

1. **Build and run**:

   ```bash
   docker-compose up --build
   ```

2. **Access the application**:

   - Streamlit Interface: <http://localhost:8501>

### Docker Files

- `Dockerfile`: Main container configuration for Streamlit
- `docker-compose.yml`: Service orchestration
- `docker-compose.dev.yml`: Development environment
- `setup-docker.sh`: Automated setup script
- `restart-docker.sh`: Quick restart script

The Docker setup provides a clean, isolated environment with all dependencies pre-installed.
