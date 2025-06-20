# Simple AI Newsletter Generator

## What This Project Does

1. **Scrapes News**: Visits local Sudbury news websites automatically
2. **Summarizes Articles**: Uses Mistral AI to create short, readable summaries  
3. **Creates Newsletter**: Builds a nice-looking HTML newsletter
4. **Saves Results**: Saves the newsletter as an HTML file you can open in your browser

## Prerequisites

- Python 3.8 or newer installed on your computer
- A Mistral AI account (free signup at https://console.mistral.ai/)
- Basic understanding of Python and command line

## Setup Instructions

### Step 1: Download the Project
```bash
# Clone or download this project to your computer
# Create a new folder and add all the project files
```

### Step 2: Create Virtual Environment
```bash
# Navigate to your project folder
cd simple_newsletter

# Create a virtual environment
python -m venv newsletter_env

# Activate the virtual environment
# On Windows:
newsletter_env\Scripts\activate

# On Mac/Linux:
source newsletter_env/bin/activate
```

### Step 3: Install Required Packages
```bash
# Install all required packages
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

### Step 4: Set Up Your API Key
1. Go to https://console.mistral.ai/ and create a free account
2. Copy your API key from the dashboard
3. Copy the `.env` file template and rename it to `.env`
4. Open `.env` and replace `your_api_key_here` with your actual API key

### Step 5: Create Output Folder
```bash
# Create the output folder where newsletters will be saved
mkdir output
```

## How to Run the Program

1. Make sure your virtual environment is activated
2. Run the main script:
```bash
python main.py
```

3. Watch the program work! It will:
   - Check your configuration
   - Visit news websites
   - Scrape articles
   - Create AI summaries
   - Build your newsletter
   - Save it as an HTML file

4. Open the generated HTML file in your web browser to read your newsletter!

## Understanding the Code

### main.py
The main script that does everything. Read through it to understand:
- How web scraping works with Playwright
- How to call AI APIs
- How to create HTML content
- How to save files in Python

### config.py
Simple configuration management:
- Loads settings from .env file
- Defines which websites to scrape
- Sets up folder paths

## Troubleshooting

### "No API key found"
- Make sure you copied your Mistral AI API key to the .env file
- Check that the .env file is in the same folder as main.py

### "No articles found"
- Check your internet connection
- Some websites might be temporarily unavailable
- Try running the program again later

### "Browser error"
- Make sure you ran `playwright install chromium`
- Try restarting your computer and running again

### "Module not found"
- Make sure your virtual environment is activated
- Try running `pip install -r requirements.txt` again

## Learning Objectives

By completing this project, the object of the project:

1. **Web Scraping**: How to automatically extract data from websites
2. **API Integration**: How to work with external AI services
3. **File Operations**: How to read and write files in Python
4. **HTML/CSS**: Basic web page structure and styling
5. **Error Handling**: How to make programs robust and user-friendly
6. **Project Organization**: How to structure a Python project

## Next Steps

Here is the expected function for the final project:

1. **Add More Sources**: Include more local news websites
2. **Better Styling**: Improve the HTML/CSS design
3. **Scheduling**: Run automatically every day
4. **NLP technique**: Improve the content by improving the input for the AI API (Prompt engineering)


## Project Structure

```
simple_newsletter/
├── main.py              # Main program (start here!)
├── config.py           # Configuration settings
├── requirements.txt    # Required Python packages
├── .env               # Your API keys (keep this private!)
├── output/            # Generated newsletters appear here
└── README.md          # This file
```
