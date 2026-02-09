
import sys
import os
from unittest.mock import MagicMock, patch

# Mock models before importing ai_service
sys.modules['models'] = MagicMock()
from models import Account, User, Category, Transaction, db

# Mock rapidfuzz if not installed (though it should be)
try:
    import rapidfuzz
except ImportError:
    sys.modules['rapidfuzz'] = MagicMock()

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from services.ai_service import AIService

def test_extraction():
    service = AIService()
    service.enabled = False # Force local extraction
    
    # Mock user and accounts
    user_id = 1
    
    # Mock database queries
    with patch('models.User.query') as mock_user_query, \
         patch('models.Account.query') as mock_account_query:
        
        # Setup mock user
        mock_user = MagicMock()
        mock_user.preferred_currency = 'COP'
        mock_user_query.get.return_value = mock_user
        
        # Setup mock accounts
        acc1 = MagicMock()
        acc1.name = "Alieress" # The real account name
        acc1.account_type = "checking"
        
        acc2 = MagicMock()
        acc2.name = "Nequi"
        
        mock_account_query.filter_by.return_value.all.return_value = [acc1, acc2]
        
        # Test case: User says "Aliexpress" instead of "Alieress"
        message = "En esa cuenta que se llama Aliexpress, ahora registra que compré un carro de lego y me gaste 170000 pesos."
        
        print(f"Testing message: '{message}'")
        print(f"Available accounts: {[acc1.name, acc2.name]}")
        
        result = service._extract_transaction_simple(user_id, message)
        
        print(f"\nResult: {result}")
        print(f"\nResult: {result}")
        if result and result.get('account') == 'Alieress':
            print("SUCCESS: Account 'Alieress' matched correctly!")
        else:
            print("FAILURE: Account 'Alieress' NOT matched.")
            print(f"Detected account: {result.get('account') if result else 'None'}")

if __name__ == "__main__":
    test_extraction()
