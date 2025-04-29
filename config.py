# Configuration settings for the expense tracker bot

CONFIG = {
    # Sheet columns
    'SHEET_COLUMNS': ['Date', 'Amount', 'Category', 'Description', 'Timestamp'],
    
    # Default expense categories
    'DEFAULT_CATEGORIES': [
        'food',
        'groceries',
        'gas',
        'transportation',
        'utilities',
        'rent',
        'entertainment',
        'shopping',
        'health',
        'education',
        'travel',
        'other'
    ],
    
    # Bot settings
    'COMMAND_PREFIX': '!',
    'DEFAULT_RECENT_COUNT': 5,
    
    # App settings
    'BOT_PORT': 8000
}
