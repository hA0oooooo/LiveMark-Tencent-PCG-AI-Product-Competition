from sqlalchemy.orm import Session

from app.models import Account


def create(db: Session, data: dict) -> Account:
    account = Account(**data)
    db.add(account)
    db.commit()
    db.refresh(account)
    return account


def get(db: Session, account_id: int) -> Account | None:
    return db.query(Account).filter(Account.id == account_id).first()


def get_by_name(db: Session, name: str) -> Account | None:
    return db.query(Account).filter(Account.name == name).first()


def list_all(db: Session) -> list[Account]:
    return db.query(Account).order_by(Account.id.asc()).all()


def get_default(db: Session) -> Account | None:
    return db.query(Account).order_by(Account.id.asc()).first()


def update(db: Session, account: Account, data: dict) -> Account:
    for key, value in data.items():
        if value is not None:
            setattr(account, key, value)
    db.commit()
    db.refresh(account)
    return account
