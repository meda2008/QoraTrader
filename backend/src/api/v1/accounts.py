from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from src.database import get_db
from src.models.base import Account
from src.auth.security import get_current_active_user
from src.schemas.account import AccountResponse

router = APIRouter()

@router.get("/", response_model=List[AccountResponse])
async def get_accounts(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Get all accounts for the current user
    """
    accounts = db.query(Account).filter(Account.user_id == current_user.id).all()
    return accounts

@router.get("/{account_id}", response_model=AccountResponse)
async def get_account(
    account_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Get a specific account by ID
    """
    account = db.query(Account).filter(
        Account.id == account_id,
        Account.user_id == current_user.id
    ).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    return account