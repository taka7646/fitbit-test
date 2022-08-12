# -*- coding: utf-8 -*-

from fastapi import Cookie, FastAPI, Query, Body, Request, Response, Header
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.encoders import jsonable_encoder
import fitbit
import pprint
import urllib.parse
import requests
import json
import base64
import secrets
import hashlib
import datetime
from typing import Union


from model import *
import db

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
setting = {}
with open("./setting.json") as f: 
    setting = json.load(f)


@app.get("/auth", response_class=HTMLResponse)
def auth(request: Request, age: int = Query(None)):
    params = setting.copy()
    url = "https://www.fitbit.com/oauth2/authorize?"
    url += "&".join(["{0}={1}".format(k, urllib.parse.quote(v)) for k, v in params.items()])
    res = templates.TemplateResponse("auth/index.html", {"request": request, "url": url, "setting": setting})
    return res

def token_updated(data: dict) -> None:
    print("refresh")
    pprint.pprint(data)
    user = db.session.query(User).filter(User.fitbit_id==data['user_id']).first()
    if not user:
        user = User(data)
        db.session.add(user)
        db.session.commit()
    else:
        user.update(data)
        db.session.commit()    

@app.get("/auth/result", response_class=HTMLResponse)
def auth_result(request: Request, code: str = Query(None)):
    print("code=" + code)
    data = {
        "code": code,
        "grant_type" : "authorization_code",
        "client_id": setting['client_id'],
        "redirect_uri": setting['redirect_uri'],
    }

    auth = "{client_id}:{client_secret}".format(**setting)
    auth = base64.b64encode(auth.encode("ascii")).decode("ascii")
    headers = {
        "Authorization": "Basic " + auth,
    }
    url = "https://api.fitbit.com/oauth2/token"
    res = requests.post(url, data, headers=headers)

    json = res.json()
    # pprint.pprint(json)
    user = db.session.query(User).filter(User.fitbit_id==json['user_id']).first()
    if not user:
        user = User(json)
        db.session.add(user)
        db.session.commit()
    else:
        user.update(json)
        user.update_session()
        db.session.commit()    

    # f = fitbit.Fitbit(setting['client_id'], setting['client_secret'], access_token=user.access_token, refresh_token=user.refresh_token, expires_at=user.expires_in, refresh_cb=token_updated)
    # activities = f.activities_list()
    # pprint.pprint(activities)

    res = templates.TemplateResponse("auth/result.html", {"request": request, "user": user})
    res.set_cookie(key="sid", value=user.session_id, expires=3600, httponly=False)
    return res

def get_login_user(request: Request) -> User:
    sid = request.cookies.get("sid")
    if sid is None:
        return None
    return db.session.query(User).filter(User.session_id==sid).first()


@app.get("/", response_class=HTMLResponse)
def index(request: Request, code: str = Query(None)):
    sid = request.cookies.get("sid")
    if sid is None:
        return RedirectResponse("/auth")
    user = db.session.query(User).filter(User.session_id==sid).first()
    if user is None:
        return RedirectResponse("/auth")
    return templates.TemplateResponse("index.html", {"request": request, "user": user})

@app.get("/heart-rate", response_class=HTMLResponse)
def heart_rate(request: Request, date: str = Query(None)):
    user = get_login_user(request)
    if user is None:
        return RedirectResponse("/auth")
    today = datetime.date.today()
    if date is None:
        date = today.isoformat()
    dates = []
    for i in range(0, 7):
        d = today - datetime.timedelta(days=i)
        dates.append(d.isoformat())
    f = fitbit.Fitbit(setting['client_id'], setting['client_secret'], access_token=user.access_token, refresh_token=user.refresh_token, expires_at=user.expires_at, refresh_cb=token_updated)
    data = f.intraday_time_series('activities/heart', date, detail_level='15min')
    data_set = data["activities-heart-intraday"]["dataset"]
    return templates.TemplateResponse("heart_rate.html", {"request": request, "user": user, "data_set":data_set, "date":date, "dates":dates})

# web api
@app.get("/api/heart-rate", response_class=JSONResponse)
def api_heart_rate(request: Request, date: str = Query(None), x_api_key: Union[str, None] = Header(default=None)):
    if x_api_key is not None:
        user = db.session.query(User).filter(User.api_key==x_api_key).first()
    if user is None:
        return RedirectResponse("/auth")
    today = datetime.date.today()
    if date is None:
        date = today.isoformat()
    f = fitbit.Fitbit(setting['client_id'], setting['client_secret'], access_token=user.access_token, refresh_token=user.refresh_token, expires_at=user.expires_at, refresh_cb=token_updated)
    data = f.intraday_time_series('activities/heart', date, detail_level='15min')
    data_set = data["activities-heart-intraday"]["dataset"]
    return JSONResponse(jsonable_encoder(data_set))
