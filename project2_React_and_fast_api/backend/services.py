from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import jwt
import datetime as _dt
import passlib.hash as _hash

from database import Base, SessionLocal, engine
from models import User, Lead
from schemas import UserCreate, User as scUser, LeadCreate

oauth2schema = OAuth2PasswordBearer(tokenUrl="/api/token")

SECRET_KEY = "myjwtsecret"
ALGORITHM = "HS256"


def create_database():
    return Base.metadata.create_all(bind = engine)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


async def get_user_by_email(email: str, db: Session):
    return db.query(User).filter(User.email == email).first()


async def create_user_in_db(user: UserCreate, db: Session):
    user_obj = User(
                    email=user.email, 
                    hashed_password=_hash.bcrypt.hash(user.hashed_password)
                    )
    
    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)
    return user_obj


async def authenticate_user(email: str, password: str, db: Session):
    user = await get_user_by_email(db=db, email=email)

    if not user:
        return False

    if not user.verify_password(password):
        return False

    return user


async def create_token(user: User):
    encode = {"email": user.email, "id": user.id, "password": user.hashed_password}

    token = jwt.encode(encode, SECRET_KEY, ALGORITHM)

    return dict(access_token=token, token_type="bearer")


async def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2schema)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms= [ALGORITHM])
        user = db.query(User).get(payload["id"])
    except:
        raise HTTPException(status_code=401, detail="Invalid Email or Password")

    current_user = User(email=user.email, id=user.id)
    return current_user


async def service_create_lead(user: scUser, db: Session, lead: LeadCreate):
    new_lead = Lead(
                first_name=lead.first_name,
                last_name=lead.last_name,
                email=lead.email,
                company=lead.company,
                note=lead.note,
                owner_id=user.id
                )
    db.add(new_lead)
    db.commit()
    db.refresh(new_lead)
    return new_lead


async def service_get_leads(user: scUser, db: Session):
    leads = db.query(Lead).filter_by(owner_id=user.id)

    return [lead for lead in leads]


async def _lead_selector(lead_id: int, user: scUser, db: Session):
    lead = (db.query(Lead)
                        .filter_by(owner_id=user.id)
                        .filter(Lead.id == lead_id)
                        .first()
            )

    if lead is None:
        raise HTTPException(status_code=404, detail="Lead does not exist")

    return lead


async def get_lead(lead_id: int, user: scUser, db: Session):
    lead = await _lead_selector(lead_id=lead_id, user=user, db=db)

    return lead


async def service_delete_lead(lead_id: int, user: User, db: Session):
    lead = await _lead_selector(lead_id, user, db)

    db.delete(lead)
    db.commit()


async def service_update_lead(lead_id: int, lead: LeadCreate, user: scUser, db: Session):
    lead_db = await _lead_selector(lead_id, user, db)

    lead_db.first_name = lead.first_name
    lead_db.last_name = lead.last_name
    lead_db.email = lead.email
    lead_db.company = lead.company
    lead_db.note = lead.note
    lead_db.date_last_updated = _dt.datetime.utcnow()

    db.commit()
    db.refresh(lead_db)

    return lead_db
