# Notion FUD & Outreach Tracker Sync

Automatically sync data from your internal database to a Notion database. This tool is designed to populate and update a Notion FUD (Fear, Uncertainty, Doubt) & Outreach tracking table with data scraped from social media platforms.

## 🚀 Features

- **Auto-populate** Notion database from any SQL/NoSQL database
- **Duplicate prevention** using unique identifiers (UIDs)
- **Update existing records** when data changes
- **Support for multiple databases**: PostgreSQL, MySQL, MongoDB, SQLite
- **Comprehensive error handling** and logging
- **Batch processing** for large datasets
- **Environment-based configuration** for security

## 📋 Prerequisites

- Python 3.7 or higher
- Notion account with a database
- Internal database with your scraped data
- Notion Integration (API key)

## 🔧 Installation

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/notion-fud-tracker-sync.git
cd notion-fud-tracker-sync
```

1. **Install dependencies**

```bash
pip install -r requirements.txt
```

1. **Set up environment variables**

```bash
cp .env.example .env
# Edit .env with your actual credentials
```

## ⚙️ Configuration

### 1. Create a Notion Integration

1. Go to <https://www.notion.so/my-integrations>
1. Click “New integration”
1. Name it (e.g., “FUD Tracker Sync”)
1. Copy the Integration Token

### 2. Get Your Database ID

1. Open your Notion database
1. Copy the URL: `https://notion.so/workspace/[DATABASE_ID]?v=...`
1. Extract the database ID (32-character string)

### 3. Share Database with Integration

1. Open your Notion database
1. Click “…” menu → “Add connections”
1. Select your integration

### 4. Configure Environment Variables

Edit `.env` file:

```env
# Notion Configuration
NOTION_TOKEN=secret_xxx...
NOTION_DATABASE_ID=abc123...

# Database Configuration
DB_TYPE=postgresql
DB_HOST=localhost
DB_PORT=5432
DB_NAME=your_database
DB_USER=your_user
DB_PASSWORD=your_password
```

## 📊 Database Schema

Your internal database should have these fields:

|Field         |Type  |Description                                    |
|--------------|------|-----------------------------------------------|
|uid           |string|Unique identifier (e.g., FUD-202511102043)     |
|name          |string|Display name                                   |
|status        |string|Current status (Not started, In Progress, etc.)|
|reviewer_name |string|Assigned reviewer                              |
|review_date   |date  |Date of review                                 |
|next_follow_up|date  |Next follow-up date                            |
|date_added    |date  |When record was added                          |
|platform      |string|Platform (TrustPilot, Socials FUD, etc.)       |
|socials       |string|Social media platforms                         |

## 🏃 Usage

### Manual Run

```bash
python notion_sync.py
```

### Automated Scheduling

#### Using Cron (Linux/Mac)

```bash
# Add to crontab (runs every hour)
0 * * * * /usr/bin/python3 /path/to/notion_sync.py
```

#### Using Task Scheduler (Windows)

1. Open Task Scheduler
1. Create Basic Task
1. Set trigger and action to run the script

#### Using GitHub Actions

```yaml
name: Sync to Notion
on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours
  workflow_dispatch:  # Manual trigger

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - run: pip install -r requirements.txt
      - run: python notion_sync.py
        env:
          NOTION_TOKEN: ${{ secrets.NOTION_TOKEN }}
          NOTION_DATABASE_ID: ${{ secrets.NOTION_DATABASE_ID }}
          DB_TYPE: ${{ secrets.DB_TYPE }}
          DB_HOST: ${{ secrets.DB_HOST }}
          DB_NAME: ${{ secrets.DB_NAME }}
          DB_USER: ${{ secrets.DB_USER }}
          DB_PASSWORD: ${{ secrets.DB_PASSWORD }}
```

## 🔐 Security Best Practices

1. **Never commit `.env` file** - Use `.env.example` as template
1. **Use GitHub Secrets** for CI/CD pipelines
1. **Implement least privilege** - Use read-only DB credentials when possible
1. **Rotate API tokens** regularly
1. **Enable logging** for audit trails

## 📝 Logging

The script provides detailed logging:

```python
# Set log level in environment
LOG_LEVEL=DEBUG  # For verbose output
LOG_LEVEL=INFO   # For standard output
LOG_LEVEL=ERROR  # For errors only
```

Logs include:

- Connection status
- Records processed
- Errors encountered
- Sync summary

## 🛠️ Customization

### Adding Custom Fields

Edit the `_format_properties` method in `notion_sync.py`:

```python
property_mapping = {
    "Name": ("name", "title"),
    "UID": ("uid", "rich_text"),
    "Custom Field": ("custom_field", "select"),
    # Add more mappings...
}
```

### Custom Query

Set a custom query in `.env`:

```env
DB_QUERY=SELECT * FROM your_table WHERE created_at > NOW() - INTERVAL '1 day'
```

## 🐛 Troubleshooting

|Issue                     |Solution                                 |
|--------------------------|-----------------------------------------|
|401 Unauthorized          |Check your Notion token                  |
|404 Not Found             |Verify database ID and integration access|
|400 Bad Request           |Check property names match exactly       |
|Rate Limiting             |Add delays between requests              |
|Database Connection Failed|Verify credentials and network access    |

## 📚 API References

- [Notion API Documentation](https://developers.notion.com/)
- [Property Types Reference](https://developers.notion.com/reference/property-value-object)
- [Rate Limits](https://developers.notion.com/reference/request-limits)

## 🤝 Contributing

1. Fork the repository
1. Create a feature branch (`git checkout -b feature/improvement`)
1. Commit changes (`git commit -am 'Add new feature'`)
1. Push to branch (`git push origin feature/improvement`)
1. Create Pull Request

## 📄 License

MIT License - see <LICENSE> file for details

## 💡 Support

- Create an [Issue](https://github.com/yourusername/notion-fud-tracker-sync/issues) for bugs
- Start a [Discussion](https://github.com/yourusername/notion-fud-tracker-sync/discussions) for questions
- Check [Wiki](https://github.com/yourusername/notion-fud-tracker-sync/wiki) for detailed guides

## 🙏 Acknowledgments

- Built with [Notion API](https://developers.notion.com/)
- Inspired by social media monitoring needs
- Community contributions welcome!

-----

**Note**: This tool respects rate limits and implements best practices for API usage. Please ensure you comply with Notion’s Terms of Service when using this tool.
