from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlmodel import Session, select
from ..models import User, RefreshToken
from ..database import get_session
from ..auth import get_password_hash, verify_password, create_access_token, create_refresh_token, decode_access_token, hash_token, make_refresh_token_value
from pydantic import BaseModel, EmailStr
from datetime import datetime
from ..ratelimit import rate_limiter

router = APIRouter(prefix="/users", tags=["users"])


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str | None = None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    refresh_token: str | None = None


@router.post("/register", response_model=dict)
def register(u: UserCreate, session: Session = Depends(get_session)):
    stmt = select(User).where(User.email == u.email)
    existing = session.exec(stmt).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(email=u.email, hashed_password=get_password_hash(u.password), full_name=u.full_name)
    session.add(user)
    session.commit()
    session.refresh(user)
    return {"id": user.id, "email": user.email}

@router.post("/login", response_model=Token)
def login(form_data: UserCreate, response: Response, request: Request, session: Session = Depends(get_session), _rl: bool = Depends(rate_limiter)):
    stmt = select(User).where(User.email == form_data.email)
    user = session.exec(stmt).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    access = create_access_token({"sub": str(user.id)})
    # create an opaque refresh token value for client, store only its hash server-side
    refresh_val = make_refresh_token_value()
    refresh = create_refresh_token({"sub": str(user.id)})
    # store hash of the refresh secret (we combine random value and JWT to bind)
    combined = refresh_val + '|' + refresh
    token_hash = hash_token(combined)
    payload = decode_access_token(refresh)
    expires_at = None
    if payload and payload.get('exp'):
        expires_at = datetime.utcfromtimestamp(payload.get('exp'))
    ua = request.headers.get('user-agent')
    ip = request.client.host if request.client else None
    rt = RefreshToken(user_id=user.id, token=token_hash, expires_at=expires_at, user_agent=ua, ip_address=ip)
    session.add(rt)
    session.commit()
    session.refresh(rt)
    # Optionally set HttpOnly cookie if client requested via header
    use_cookie = False
    if request and request.headers.get('x-use-cookie') == '1':
        use_cookie = True
    if use_cookie and response is not None:
        # choose secure flag based on request scheme (allow test http to work)
        secure_flag = True if (request is not None and getattr(request.url, 'scheme', '') == 'https') else False
        # set cookie with the client-side refresh value (not the server hash)
        response.set_cookie('refresh_token', refresh_val + '|' + refresh, httponly=True, secure=secure_flag, samesite='lax')
        return {"access_token": access}
    return {"access_token": access, "refresh_token": refresh_val + '|' + refresh}


@router.post('/refresh', response_model=Token)
def refresh_token(payload: dict | None = None, session: Session = Depends(get_session), request: Request = None, response: Response = None, _rl: bool = Depends(rate_limiter)):
    # payload is expected to be {"refresh_token": "..."}, but if missing we also allow cookie-based flow
    token = None
    if isinstance(payload, dict):
        token = payload.get('refresh_token')
    # fallback to cookie if no token in body
    if not token and request and request.cookies.get('refresh_token'):
        token = request.cookies.get('refresh_token')
    if not token:
        raise HTTPException(status_code=400, detail='Missing refresh_token')
    # token is expected as client-provided combined value: <rand>|<jwt>
    if not isinstance(token, str):
        raise HTTPException(status_code=400, detail='Invalid token format')
    parts = token.split('|', 1)
    if len(parts) != 2:
        raise HTTPException(status_code=400, detail='Invalid token format')
    rand_part, jwt_part = parts[0], parts[1]
    data = decode_access_token(jwt_part)
    if not data:
        raise HTTPException(status_code=401, detail='Invalid refresh token')
    sub = data.get('sub')
    if not sub:
        raise HTTPException(status_code=401, detail='Invalid token')
    user = session.get(User, int(sub))
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    # validate stored refresh token by hashing the combined value and comparing
    token_hash = hash_token(token)
    stored = session.exec(select(RefreshToken).where(RefreshToken.token == token_hash)).first()
    if not stored or stored.revoked:
        raise HTTPException(status_code=401, detail='Refresh token revoked or not found')
    if stored.expires_at and stored.expires_at < datetime.utcnow():
        raise HTTPException(status_code=401, detail='Refresh token expired')
    # rotate: revoke old and issue new
    stored.revoked = True
    session.add(stored)
    access = create_access_token({"sub": str(user.id)})
    new_refresh = create_refresh_token({"sub": str(user.id)})
    # issue new client-side random value + jwt, store its hash
    new_rand = make_refresh_token_value()
    new_combined = new_rand + '|' + new_refresh
    payload_new = decode_access_token(new_refresh)
    expires_at = None
    if payload_new and payload_new.get('exp'):
        expires_at = datetime.utcfromtimestamp(payload_new.get('exp'))
    rt = RefreshToken(user_id=user.id, token=hash_token(new_combined), expires_at=expires_at)
    session.add(rt)
    session.commit()
    # If client used cookie-based refresh (cookie present), set new HttpOnly cookie and return only access_token
    if request and request.cookies.get('refresh_token') and response is not None:
        secure_flag = True if getattr(request.url, 'scheme', '') == 'https' else False
        response.set_cookie('refresh_token', new_combined, httponly=True, secure=secure_flag, samesite='lax')
        return {"access_token": access}
    return {"access_token": access, "refresh_token": new_combined}


@router.post('/logout')
def logout(payload: dict | None = None, session: Session = Depends(get_session), request: Request = None, response: Response = None):
    # Accept token via JSON or cookie; revoke stored hash and clear cookie if present
    token = None
    if isinstance(payload, dict) and payload.get('refresh_token'):
        token = payload.get('refresh_token')
    elif request and request.cookies.get('refresh_token'):
        token = request.cookies.get('refresh_token')
    if not token:
        raise HTTPException(status_code=400, detail='Missing refresh_token')
    token_hash = hash_token(token)
    stored = session.exec(select(RefreshToken).where(RefreshToken.token == token_hash)).first()
    if not stored:
        # still clear cookie if present
        if response is not None and request and request.cookies.get('refresh_token'):
            response.delete_cookie('refresh_token')
        return {"revoked": False}
    stored.revoked = True
    session.add(stored)
    session.commit()
    if response is not None and request and request.cookies.get('refresh_token'):
        response.delete_cookie('refresh_token')
    return {"revoked": True}
