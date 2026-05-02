from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import AccountBenchmarkRead, AccountCreate, AccountRead, AccountUpdate
from app.services import account_service, analytics_service

router = APIRouter(prefix="/api/accounts", tags=["accounts"])


@router.post("", response_model=AccountRead)
def create_account(payload: AccountCreate, db: Session = Depends(get_db)):
    return account_service.create_account(db, payload)


@router.get("", response_model=list[AccountRead])
def list_accounts(db: Session = Depends(get_db)):
    return account_service.list_accounts(db)


@router.get("/default", response_model=AccountRead)
def get_default_account(db: Session = Depends(get_db)):
    return account_service.get_default_account(db)


@router.get("/{account_id}", response_model=AccountRead)
def get_account(account_id: int, db: Session = Depends(get_db)):
    return account_service.get_account(db, account_id)


@router.put("/{account_id}", response_model=AccountRead)
def update_account(account_id: int, payload: AccountUpdate, db: Session = Depends(get_db)):
    return account_service.update_account(db, account_id, payload)


@router.get("/{account_id}/benchmark", response_model=AccountBenchmarkRead)
def get_account_benchmark(account_id: int, db: Session = Depends(get_db)):
    return analytics_service.get_account_benchmark(db, account_id)
