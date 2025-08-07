# Simple AI Newsletter Generator

## What This Does (Easy Explanation!)

This program automatically creates newsletters for you! Here's how it works:

1. **Gets News Articles** - Visits 5+ local Sudbury news websites and collects articles from the past week
2. **AI Makes Summaries** - Uses artificial intelligence to create short summaries  
3. **Creates Newsletter** - Makes a beautiful HTML newsletter
4. **Saves File** - Saves it so you can open it in your web browser

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
# Make sure .venv is activated first!
python main.py
```

That's it! Your newsletter will be saved as an HTML file!

## Two Ways to Use This

### Way 1: Command Line (Simple)
```bash
python main.py          # Make a newsletter
python main.py --help   # Get help
```

### Way 2: Web Dashboard (Cool!)
```bash
python -m src.api.server
```
Then open your browser to: http://localhost:8080
Click the button to generate newsletters!

## Understanding the Code (For Learning)

```text
main.py                    # Start here! Main program (easy to read)
input/                     # Raw scraped articles (before AI processing)
output/                    # Final newsletters (after AI processing)
tests/                     # All test files organized here
├── run_tests.py          # Test runner for all tests
├── test_setup.py         # Setup validation test
├── simple_test.py        # Simple validation test
└── test_*.py             # Individual component tests
src/
├── core/config.py         # Settings and configuration  
├── utils/utils.py         # Helper functions
├── newsletter_generator/  # The main magic happens here
│   ├── scraper.py        # Gets articles from websites
│   ├── smart_analyzer.py # NLP content analysis
│   ├── simple_categorized_summarizer.py  # AI summarization
│   └── newsletter.py     # Creates the HTML newsletter
└── api/server.py         # Web server for dashboard
WORKFLOW.md               # Complete project documentation
```

### Key Files & Folders (What Each Does)

- **main.py** - This is where everything starts! Easy to read and understand
- **tests/** - All test files organized in one place with proper structure
- **tests/run_tests.py** - Runs all tests automatically
- **input/** - Raw scraped articles saved as JSON files (great for learning!)
- **output/** - Final HTML newsletters ready to view
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

- **Web Scraping**: How to get FULL article content from multiple news sources automatically
- **AI APIs**: How to use artificial intelligence in your programs  
- **HTML Creation**: How to make web pages with Python
- **File Operations**: How to save and load files
- **Project Organization**: How to structure Python projects properly
- **Data Pipeline**: See the data flow from raw scraped text → AI summaries → final newsletter
- **Link Following**: Learn how to visit article pages for complete content
- **Testing**: How to organize and run tests for your code
- **Advanced NLP**: Content quality analysis and automatic categorization

**Pro Tip**: Check the `input/` folder to see raw scraped articles with FULL content before AI processing!

**Documentation**: Read `WORKFLOW.md` for complete technical documentation and workflow details!

## News Sources

The scraper gets articles from these Sudbury news sources:

- **greatersudbury.ca** - Official city news (works great!)
- **ctvnews.ca/northern-ontario** - CTV News Northern Ontario (works great!)
- **globalnews.ca/tag/sudbury-news/** - Global News Sudbury coverage (works great!)
- **thesudburystar.com** - The Sudbury Star newspaper (works great!)
- **sudbury.com** - Requires JavaScript (can't scrape with simple tools)

**Note**: Some modern websites (like sudbury.com) use JavaScript to load content, which means our simple scraper can't read them. This is normal - many news sites work this way. The other sources provide plenty of good articles!

Perfect for beginners!

## Advanced: Docker Setup

If you want to try Docker (optional):

```bash
make build    # Build the container  
make up       # Start the service
make down     # Stop everything
```

---

**Happy coding!**

Remember: The best way to learn is to read the code, run it, and try changing things!
