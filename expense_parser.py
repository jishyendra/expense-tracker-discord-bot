import re
import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def parse_expense(message):
    """
    Parse an expense message into structured data.
    
    Supported formats:
    - "$10 lunch"
    - "10 lunch"
    - "$10.50 groceries at Walmart"
    - "20 gas"
    
    Args:
        message (str): The expense message to parse
        
    Returns:
        dict: A dictionary with the parsed expense data, or None if parsing failed
    """
    # Clean up the message
    message = message.strip()
    
    # Define regex patterns
    # Pattern 1: Amount + Category + Optional Description
    pattern1 = r'^\$?(\d+(?:\.\d+)?)\s+([a-zA-Z]+)(?:\s+(.+))?$'
    
    # Pattern 2: Amount + Category + "at/for" + Description
    pattern2 = r'^\$?(\d+(?:\.\d+)?)\s+([a-zA-Z]+)\s+(?:at|for)\s+(.+)$'
    
    try:
        # Try pattern 1
        match = re.match(pattern1, message)
        if match:
            amount, category, description = match.groups()
            
            # If description is None, set to empty string
            description = description if description else ''
            
            return {
                'date': datetime.datetime.now().strftime('%Y-%m-%d'),
                'amount': float(amount),
                'category': category.lower(),
                'description': description
            }
        
        # Try pattern 2
        match = re.match(pattern2, message)
        if match:
            amount, category, description = match.groups()
            
            return {
                'date': datetime.datetime.now().strftime('%Y-%m-%d'),
                'amount': float(amount),
                'category': category.lower(),
                'description': description
            }
        
        # Handle more complex formats
        # Look for a dollar amount
        amount_match = re.search(r'\$?(\d+(?:\.\d+)?)', message)
        if amount_match:
            amount = float(amount_match.group(1))
            
            # Remove the amount from the message
            remaining = message.replace(amount_match.group(0), '', 1).strip()
            
            # Extract the first word as the category
            parts = remaining.split(maxsplit=1)
            if len(parts) > 0:
                category = parts[0].lower()
                description = parts[1] if len(parts) > 1 else ''
                
                return {
                    'date': datetime.datetime.now().strftime('%Y-%m-%d'),
                    'amount': amount,
                    'category': category,
                    'description': description
                }
        
        # If we got here, parsing failed
        logger.warning(f"Failed to parse expense message: {message}")
        return None
        
    except Exception as e:
        logger.error(f"Error parsing expense message: {str(e)}")
        return None
