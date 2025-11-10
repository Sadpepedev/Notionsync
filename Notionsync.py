“””
Notion Database Auto-Population Script
GitHub-safe version with environment variable configuration
“””

import requests
import json
from datetime import datetime
from typing import Dict, List, Optional
import os
from dotenv import load_dotenv
import logging
import sys

# Load environment variables

load_dotenv()

# Set up logging

logging.basicConfig(
level=logging.INFO,
format=’%(asctime)s - %(name)s - %(levelname)s - %(message)s’
)
logger = logging.getLogger(**name**)

class NotionDatabaseSync:
def **init**(self, notion_token: str = None, database_id: str = None):
“””
Initialize the Notion sync client

```
    Args:
        notion_token: Your Notion Integration Token (defaults to env var)
        database_id: The ID of your Notion database (defaults to env var)
    """
    self.notion_token = notion_token or os.getenv("NOTION_TOKEN")
    self.database_id = database_id or os.getenv("NOTION_DATABASE_ID")
    
    if not self.notion_token or not self.database_id:
        raise ValueError(
            "NOTION_TOKEN and NOTION_DATABASE_ID must be provided "
            "either as arguments or environment variables"
        )
    
    self.headers = {
        "Authorization": f"Bearer {self.notion_token}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    self.base_url = "https://api.notion.com/v1"

def create_page(self, data: Dict) -> Dict:
    """
    Create a new page (row) in the Notion database
    
    Args:
        data: Dictionary containing the row data
    
    Returns:
        Response from Notion API
    """
    url = f"{self.base_url}/pages"
    
    # Format the properties according to Notion's schema
    properties = self._format_properties(data)
    
    payload = {
        "parent": {"database_id": self.database_id},
        "properties": properties
    }
    
    try:
        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()
        logger.info(f"Successfully created page for UID: {data.get('uid')}")
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error creating page: {e}")
        if hasattr(e.response, 'json'):
            logger.error(f"Response: {e.response.json()}")
        raise

def _format_properties(self, data: Dict) -> Dict:
    """
    Format data into Notion property format
    
    Args:
        data: Raw data dictionary
    
    Returns:
        Formatted properties for Notion API
    """
    properties = {}
    
    # Map your data fields to Notion properties
    property_mapping = {
        "Name": ("name", "title"),
        "UID": ("uid", "rich_text"),
        "Status": ("status", "select"),
        "Reviewer Name": ("reviewer_name", "rich_text"),
        "Review Date": ("review_date", "date"),
        "Next Follow Up": ("next_follow_up", "date"),
        "Date Added": ("date_added", "date"),
        "Platform": ("platform", "select"),
        "Socials": ("socials", "rich_text")
    }
    
    for notion_prop, (data_key, prop_type) in property_mapping.items():
        value = data.get(data_key)
        
        if value is None:
            continue
        
        if prop_type == "title":
            properties[notion_prop] = {
                "title": [{"text": {"content": str(value)}}]
            }
        elif prop_type == "rich_text":
            properties[notion_prop] = {
                "rich_text": [{"text": {"content": str(value)}}]
            }
        elif prop_type == "select":
            properties[notion_prop] = {
                "select": {"name": str(value)}
            }
        elif prop_type == "date" and value:
            properties[notion_prop] = {
                "date": {"start": str(value)}
            }
    
    return properties

def check_if_exists(self, uid: str) -> Optional[str]:
    """
    Check if a record with given UID already exists
    
    Args:
        uid: The UID to check
    
    Returns:
        Page ID if exists, None otherwise
    """
    url = f"{self.base_url}/databases/{self.database_id}/query"
    
    filter_data = {
        "filter": {
            "property": "UID",
            "rich_text": {
                "equals": uid
            }
        }
    }
    
    try:
        response = requests.post(url, headers=self.headers, json=filter_data)
        response.raise_for_status()
        
        results = response.json().get("results", [])
        if results:
            return results[0]["id"]
    except requests.exceptions.RequestException as e:
        logger.error(f"Error checking existence: {e}")
        raise
    
    return None

def update_page(self, page_id: str, data: Dict) -> Dict:
    """
    Update an existing page in Notion
    
    Args:
        page_id: The ID of the page to update
        data: Dictionary containing the updated data
    
    Returns:
        Response from Notion API
    """
    url = f"{self.base_url}/pages/{page_id}"
    
    # Only update specific fields that might change
    update_fields = ["status", "platform", "socials", "reviewer_name", 
                    "review_date", "next_follow_up"]
    
    properties = {}
    for field in update_fields:
        if field in data:
            formatted = self._format_properties({field: data[field]})
            properties.update(formatted)
    
    payload = {"properties": properties}
    
    try:
        response = requests.patch(url, headers=self.headers, json=payload)
        response.raise_for_status()
        logger.info(f"Successfully updated page: {page_id}")
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error updating page: {e}")
        raise

def sync_from_database(self, records: List[Dict]) -> Dict:
    """
    Sync multiple records from your internal database to Notion
    
    Args:
        records: List of dictionaries containing record data
    
    Returns:
        Summary of sync operations
    """
    summary = {
        "created": 0,
        "updated": 0,
        "errors": 0,
        "error_details": []
    }
    
    for record in records:
        try:
            uid = record.get("uid")
            
            if not uid:
                logger.warning(f"Skipping record without UID: {record}")
                summary["errors"] += 1
                summary["error_details"].append({
                    "record": record,
                    "error": "Missing UID"
                })
                continue
            
            # Check if record exists
            existing_page_id = self.check_if_exists(uid)
            
            if existing_page_id:
                # Update existing record
                logger.info(f"Updating existing record: {uid}")
                self.update_page(existing_page_id, record)
                summary["updated"] += 1
            else:
                # Create new record
                logger.info(f"Creating new record: {uid}")
                self.create_page(record)
                summary["created"] += 1
                
        except Exception as e:
            logger.error(f"Error processing record {record.get('uid', 'unknown')}: {str(e)}")
            summary["errors"] += 1
            summary["error_details"].append({
                "record": record,
                "error": str(e)
            })
    
    logger.info(f"Sync Summary: Created: {summary['created']}, "
               f"Updated: {summary['updated']}, Errors: {summary['errors']}")
    
    return summary
```

class DatabaseConnector:
“””
Abstract base class for database connectors
Override the fetch_records method for your specific database
“””

```
@staticmethod
def get_connector(db_type: str = None):
    """
    Factory method to get the appropriate database connector
    
    Args:
        db_type: Type of database (postgresql, mysql, mongodb, sqlite)
    
    Returns:
        Database connector instance
    """
    db_type = db_type or os.getenv("DB_TYPE", "postgresql")
    
    connectors = {
        "postgresql": PostgreSQLConnector,
        "mysql": MySQLConnector,
        "mongodb": MongoDBConnector,
        "sqlite": SQLiteConnector
    }
    
    connector_class = connectors.get(db_type)
    if not connector_class:
        raise ValueError(f"Unsupported database type: {db_type}")
    
    return connector_class()

def fetch_records(self) -> List[Dict]:
    """
    Fetch records from the database
    Must be implemented by subclasses
    """
    raise NotImplementedError("Subclasses must implement fetch_records")
```

class PostgreSQLConnector(DatabaseConnector):
“”“PostgreSQL database connector”””

```
def fetch_records(self) -> List[Dict]:
    try:
        import psycopg2
        import psycopg2.extras
    except ImportError:
        logger.error("psycopg2 not installed. Run: pip install psycopg2-binary")
        return []
    
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT", 5432)
    )
    
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    query = os.getenv("DB_QUERY", """
        SELECT 
            uid, name, status, reviewer_name, 
            review_date, next_follow_up, date_added, 
            platform, socials
        FROM fud_outreach_tracker
        WHERE sync_status IS NULL OR sync_status != 'synced'
        ORDER BY date_added DESC
    """)
    
    cursor.execute(query)
    records = [dict(row) for row in cursor.fetchall()]
    
    cursor.close()
    conn.close()
    
    return records
```

class MySQLConnector(DatabaseConnector):
“”“MySQL database connector”””

```
def fetch_records(self) -> List[Dict]:
    try:
        import mysql.connector
    except ImportError:
        logger.error("mysql-connector-python not installed. Run: pip install mysql-connector-python")
        return []
    
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT", 3306)
    )
    
    cursor = conn.cursor(dictionary=True)
    
    query = os.getenv("DB_QUERY", """
        SELECT 
            uid, name, status, reviewer_name, 
            review_date, next_follow_up, date_added, 
            platform, socials
        FROM fud_outreach_tracker
        WHERE sync_status IS NULL OR sync_status != 'synced'
        ORDER BY date_added DESC
    """)
    
    cursor.execute(query)
    records = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return records
```

class MongoDBConnector(DatabaseConnector):
“”“MongoDB database connector”””

```
def fetch_records(self) -> List[Dict]:
    try:
        from pymongo import MongoClient
    except ImportError:
        logger.error("pymongo not installed. Run: pip install pymongo")
        return []
    
    connection_string = os.getenv("MONGO_CONNECTION_STRING") or \
        f"mongodb://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT', 27017)}/{os.getenv('DB_NAME')}"
    
    client = MongoClient(connection_string)
    db = client[os.getenv("DB_NAME")]
    collection = db[os.getenv("DB_COLLECTION", "fud_outreach_tracker")]
    
    # Find documents that haven't been synced
    query = {"sync_status": {"$ne": "synced"}}
    records = list(collection.find(query))
    
    # Convert ObjectId to string if present
    for record in records:
        if "_id" in record:
            record["_id"] = str(record["_id"])
    
    client.close()
    
    return records
```

class SQLiteConnector(DatabaseConnector):
“”“SQLite database connector”””

```
def fetch_records(self) -> List[Dict]:
    import sqlite3
    
    db_path = os.getenv("SQLITE_DB_PATH", "database.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    cursor = conn.cursor()
    
    query = os.getenv("DB_QUERY", """
        SELECT 
            uid, name, status, reviewer_name, 
            review_date, next_follow_up, date_added, 
            platform, socials
        FROM fud_outreach_tracker
        WHERE sync_status IS NULL OR sync_status != 'synced'
        ORDER BY date_added DESC
    """)
    
    cursor.execute(query)
    records = [dict(row) for row in cursor.fetchall()]
    
    cursor.close()
    conn.close()
    
    return records
```

def main():
“””
Main function to run the sync process
“””
try:
# Initialize the sync client
logger.info(“Initializing Notion sync client…”)
sync_client = NotionDatabaseSync()

```
    # Get the appropriate database connector
    db_type = os.getenv("DB_TYPE", "postgresql")
    logger.info(f"Connecting to {db_type} database...")
    
    connector = DatabaseConnector.get_connector(db_type)
    
    # Fetch data from your internal database
    logger.info("Fetching data from internal database...")
    records = connector.fetch_records()
    logger.info(f"Found {len(records)} records to sync")
    
    if not records:
        logger.info("No records to sync")
        return
    
    # Sync to Notion
    logger.info("Syncing to Notion...")
    summary = sync_client.sync_from_database(records)
    
    # Print summary
    print("\n" + "="*50)
    print("SYNC COMPLETE")
    print("="*50)
    print(f"✅ Created: {summary['created']} new records")
    print(f"📝 Updated: {summary['updated']} existing records")
    print(f"❌ Errors: {summary['errors']} failed records")
    
    if summary['error_details']:
        print("\nError Details:")
        for error in summary['error_details'][:5]:  # Show first 5 errors
            print(f"  - UID {error['record'].get('uid', 'unknown')}: {error['error']}")
    
    # Exit with error code if there were errors
    if summary['errors'] > 0:
        sys.exit(1)
        
except Exception as e:
    logger.error(f"Fatal error: {e}")
    sys.exit(1)
```

if **name** == “**main**”:
main()
