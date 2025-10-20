import os
import gspread
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
    def __init__(self):
        """Initialize the Google Sheets connection."""
        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']
        
        creds_json = os.environ.get('GOOGLE_CREDENTIALS')
        if not creds_json:
            logger.error("GOOGLE_CREDENTIALS not found in environment variables")
            raise ValueError("GOOGLE_CREDENTIALS not found in environment variables")
        
        self.sheet_id = os.environ.get('GOOGLE_SHEET_ID')
        if not self.sheet_id:
            logger.error("GOOGLE_SHEET_ID not found in environment variables")
            raise ValueError("GOOGLE_SHEET_ID not found in environment variables")
        
        try:
            creds = ServiceAccountCredentials.from_json_keyfile_dict(
               eval(creds_json), scope)
            self.client = gspread.authorize(creds)
            self.spreadsheet = self.client.open_by_key(self.sheet_id)
            try:
                self.worksheet = self.spreadsheet.worksheet('Expenses')
            except gspread.exceptions.WorksheetNotFound:
                self.worksheet = self.spreadsheet.add_worksheet(
                    title='Expenses', rows=1000, cols=20)
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
        dict:
                - date: The date of the expense
                - amount: The amount spent
                - category: The expense category
                - description: A description of the expense
        """
        try:
            if isinstance(expense['date'], datetime.datetime):
                expense['date'] = expense['date'].strftime('%Y-%m-%d')
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.worksheet.append_row([
                expense['date'],
                # expense['currency'],
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
        try:
            records = self.worksheet.get_all_records()
            
            if records and 'Timestamp' in records[0]:
                records.sort(key=lambda x: x['Timestamp'], reverse=True)
            recent = records[:count]
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
        try:
            records = self.worksheet.get_all_records()
            if category:
                filtered_records = [r for r in records if r.get('Category', '').lower() == category.lower()]
            else:
                filtered_records = records
            total = sum(float(r.get('Amount', 0)) for r in filtered_records)
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
        try:
            records = self.worksheet.get_all_records()
            categories = set()
            for record in records:
                cat = record.get('Category', '').strip()
                if cat:
                    categories.add(cat)
            return sorted(list(categories))
        except Exception as e:
            logger.error(f"Error getting categories: {str(e)}")
            raise