import os
import gspread
import json
from dotenv import load_dotenv
from oauth2client.service_account import ServiceAccountCredentials
import datetime
import logging
from config import CONFIG
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class ExpenseSheetManager:
    """
    Class to manage interactions with Google Sheets for expense tracking.
    """
    
    def __init__(self):
        """Initialize the Google Sheets connection."""
        # Define the scope and credentials
        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']
        
        # Get credentials from service account JSON
        creds_json = os.environ.get('GOOGLE_SHEETS_CREDENTIALS')
        if not creds_json:
            logger.error("GOOGLE_SHEETS_CREDENTIALS not found in environment variables")
            raise ValueError("GOOGLE_SHEETS_CREDENTIALS not found in environment variables")
        
        # Get the Google Sheet ID
        self.sheet_id = os.environ.get('GOOGLE_SHEET_ID')
        if not self.sheet_id:
            logger.error("GOOGLE_SHEET_ID not found in environment variables")
            raise ValueError("GOOGLE_SHEET_ID not found in environment variables")
        
        try:
            # Authenticate and create the client
            creds = ServiceAccountCredentials.from_json_keyfile_dict(
               keyfile_dict=creds_json, scopes=scope)
            self.client = gspread.authorize(creds)
            # Open the spreadsheet
            self.spreadsheet = self.client.open_by_key(self.sheet_id)
            # Check if the expenses worksheet exists, if not create it
            try:
                self.worksheet = self.spreadsheet.worksheet('Expenses')
            except gspread.exceptions.WorksheetNotFound:
                self.worksheet = self.spreadsheet.add_worksheet(
                    title='Expenses', rows=1000, cols=20)
                # Add headers
                self.worksheet.append_row([
                    'Date', 'Amount', 'Category', 'Description', 'Timestamp'
                ])
                
            logger.info("Successfully connected to Google Sheets")
            
        except Exception as e:
            logger.error(f"Error connecting to Google Sheets: {str(e)}")
            raise
    
    def add_expense(self, expense):
        """
        Add an expense to the Google Sheet.
        
        Args:
            expense (dict): A dictionary containing expense details:
                - date: The date of the expense
                - amount: The amount spent
                - category: The expense category
                - description: A description of the expense
                
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Format the date if it's a datetime object
            if isinstance(expense['date'], datetime.datetime):
                expense['date'] = expense['date'].strftime('%Y-%m-%d')
                
            # Add timestamp
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Append the expense to the worksheet
            self.worksheet.append_row([
                expense['date'],
                expense['amount'],
                expense['category'],
                expense['description'],
                timestamp
            ])
            
            logger.info(f"Added expense: {expense}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding expense to Google Sheets: {str(e)}")
            raise
    
    def get_recent_expenses(self, count=5):
        """
        Get the most recent expenses.
        
        Args:
            count (int): Number of recent expenses to retrieve
            
        Returns:
            list: List of expense dictionaries
        """
        try:
            # Get all records
            records = self.worksheet.get_all_records()
            
            # Sort by timestamp (newest first)
            if records and 'Timestamp' in records[0]:
                records.sort(key=lambda x: x['Timestamp'], reverse=True)
            
            # Limit to the requested count
            recent = records[:count]
            
            # Convert to our format
            expenses = []
            for record in recent:
                expenses.append({
                    'date': record.get('Date', ''),
                    'amount': record.get('Amount', 0),
                    'category': record.get('Category', ''),
                    'description': record.get('Description', '')
                })
                
            return expenses
            
        except Exception as e:
            logger.error(f"Error getting recent expenses: {str(e)}")
            raise
    
    def get_total_expenses(self, category=None):
        """
        Get total expenses, optionally filtered by category.
        
        Args:
            category (str, optional): Category to filter by
            
        Returns:
            tuple: (total, category_breakdown)
                - total: Total amount of expenses
                - category_breakdown: Dictionary of totals by category
        """
        try:
            # Get all records
            records = self.worksheet.get_all_records()
            
            # Filter by category if specified
            if category:
                filtered_records = [r for r in records if r.get('Category', '').lower() == category.lower()]
            else:
                filtered_records = records
            
            # Calculate total
            total = sum(float(r.get('Amount', 0)) for r in filtered_records)
            
            # Calculate breakdown by category
            breakdown = {}
            for record in records:
                cat = record.get('Category', 'Other')
                amt = float(record.get('Amount', 0))
                if cat in breakdown:
                    breakdown[cat] += amt
                else:
                    breakdown[cat] = amt
            
            return total, breakdown
            
        except Exception as e:
            logger.error(f"Error calculating total expenses: {str(e)}")
            raise
    
    def get_categories(self):
        """
        Get all unique expense categories.
        
        Returns:
            list: List of category names
        """
        try:
            # Get all records
            records = self.worksheet.get_all_records()
            
            # Extract unique categories
            categories = set()
            for record in records:
                cat = record.get('Category', '').strip()
                if cat:
                    categories.add(cat)
            
            return sorted(list(categories))
            
        except Exception as e:
            logger.error(f"Error getting categories: {str(e)}")
            raise
