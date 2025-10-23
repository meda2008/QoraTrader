from typing import Dict, List, Optional
from datetime import datetime
import logging
from src.models.base import Account, User
from src.database import get_db
from src.utils.error_handler import CustomException

logger = logging.getLogger(__name__)

class AccountService:
    """
    Service for managing accounts
    """
    
    def __init__(self):
        logger.info("Account service initialized")
    
    async def create_account(self, account_data: Dict) -> Account:
        """
        Create a new account
        """
        try:
            from sqlalchemy.orm import Session
            db: Session = next(get_db())
            
            # Validate input data
            required_fields = ['user_id']
            for field in required_fields:
                if field not in account_data:
                    raise CustomException(f"Missing required field: {field}", 400)
            
            # Verify the user exists
            user = db.query(User).filter(User.id == account_data['user_id']).first()
            if not user:
                raise CustomException(f"User with ID {account_data['user_id']} not found", 404)
            
            # Create account object
            account = Account(
                user_id=account_data['user_id'],
                account_type=account_data.get('account_type'),
                status=account_data.get('status'),
                balance=account_data.get('initial_balance', 100000.0),  # Default to 100k
                available_balance=account_data.get('initial_balance', 100000.0),
                market_value=0.0,
                total_pnl=0.0,
                daily_pnl=0.0,
                risk_level=account_data.get('risk_level')
            )
            
            # Add to database
            db.add(account)
            db.commit()
            db.refresh(account)
            
            logger.info(f"Account {account.id} created for user {account.user_id}")
            return account
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"Error creating account: {str(e)}")
            raise CustomException(f"Failed to create account: {str(e)}", 500)
        finally:
            db.close()
    
    async def get_account(self, account_id: str) -> Optional[Account]:
        """
        Get an account by ID
        """
        try:
            from sqlalchemy.orm import Session
            db: Session = next(get_db())
            
            account = db.query(Account).filter(Account.id == account_id).first()
            if not account:
                raise CustomException(f"Account with ID {account_id} not found", 404)
            
            return account
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"Error retrieving account {account_id}: {str(e)}")
            raise CustomException(f"Failed to retrieve account: {str(e)}", 500)
        finally:
            db.close()
    
    async def update_account(self, account_id: str, update_data: Dict) -> Optional[Account]:
        """
        Update an existing account
        """
        try:
            from sqlalchemy.orm import Session
            db: Session = next(get_db())
            
            account = db.query(Account).filter(Account.id == account_id).first()
            if not account:
                raise CustomException(f"Account with ID {account_id} not found", 404)
            
            # Update allowed fields
            updatable_fields = {
                'status', 'balance', 'available_balance', 'market_value', 
                'total_pnl', 'daily_pnl', 'risk_level'
            }
            
            for field, value in update_data.items():
                if field in updatable_fields:
                    setattr(account, field, value)
            
            db.commit()
            db.refresh(account)
            
            logger.info(f"Account {account.id} updated")
            return account
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"Error updating account {account_id}: {str(e)}")
            raise CustomException(f"Failed to update account: {str(e)}", 500)
        finally:
            db.close()
    
    async def get_accounts_by_user(self, user_id: str) -> List[Account]:
        """
        Get all accounts for a specific user
        """
        try:
            from sqlalchemy.orm import Session
            db: Session = next(get_db())
            
            accounts = db.query(Account).filter(Account.user_id == user_id).all()
            return accounts
        except Exception as e:
            logger.error(f"Error retrieving accounts for user {user_id}: {str(e)}")
            raise CustomException(f"Failed to retrieve accounts: {str(e)}", 500)
        finally:
            db.close()
    
    async def get_account_balance(self, account_id: str) -> Dict[str, float]:
        """
        Get detailed balance information for an account
        """
        try:
            account = await self.get_account(account_id)
            if not account:
                raise CustomException(f"Account with ID {account_id} not found", 404)
            
            return {
                "account_id": account.id,
                "balance": float(account.balance),
                "available_balance": float(account.available_balance),
                "market_value": float(account.market_value),
                "total_pnl": float(account.total_pnl),
                "daily_pnl": float(account.daily_pnl)
            }
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"Error retrieving balance for account {account_id}: {str(e)}")
            raise CustomException(f"Failed to retrieve balance: {str(e)}", 500)
    
    async def deposit_funds(self, account_id: str, amount: float) -> bool:
        """
        Deposit funds to an account
        """
        try:
            from sqlalchemy.orm import Session
            db: Session = next(get_db())
            
            if amount <= 0:
                raise CustomException("Deposit amount must be positive", 400)
            
            account = db.query(Account).filter(Account.id == account_id).first()
            if not account:
                raise CustomException(f"Account with ID {account_id} not found", 404)
            
            # Update account balance
            account.balance += amount
            account.available_balance += amount
            account.updated_at = datetime.utcnow()
            
            db.commit()
            logger.info(f"Deposited {amount} to account {account.id}, new balance: {account.balance}")
            return True
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"Error depositing funds to account {account_id}: {str(e)}")
            raise CustomException(f"Failed to deposit funds: {str(e)}", 500)
        finally:
            db.close()
    
    async def withdraw_funds(self, account_id: str, amount: float) -> bool:
        """
        Withdraw funds from an account
        """
        try:
            from sqlalchemy.orm import Session
            db: Session = next(get_db())
            
            if amount <= 0:
                raise CustomException("Withdrawal amount must be positive", 400)
            
            account = db.query(Account).filter(Account.id == account_id).first()
            if not account:
                raise CustomException(f"Account with ID {account_id} not found", 404)
            
            if account.available_balance < amount:
                raise CustomException("Insufficient available balance", 400)
            
            # Update account balance
            account.balance -= amount
            account.available_balance -= amount
            account.updated_at = datetime.utcnow()
            
            db.commit()
            logger.info(f"Withdrew {amount} from account {account.id}, new balance: {account.balance}")
            return True
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"Error withdrawing funds from account {account_id}: {str(e)}")
            raise CustomException(f"Failed to withdraw funds: {str(e)}", 500)
        finally:
            db.close()