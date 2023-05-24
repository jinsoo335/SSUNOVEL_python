import sys
sys.path.append("")

import threading

from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from model import Novel
from scraping.kakao import kakao_scraping
from scraping.munpia import munpia_scraping
from scraping.ridi import ridi_scraping
from scraping.series import series_scraping

from session import SessionLocal



app = FastAPI()


mutex = threading.Lock()



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



@app.get("/scraping")
async def scraping():

    # 락 얻으려고 시도
    # 누군가 락을 가지고 있다면 대기하지 않고 False 반환
    # 락은 한 스레드내에서 공유한다.
    # 같은 스레드라면, 여러 락을 호출해서 사용할 수 있다.
    acquire = mutex.acquire(blocking=False)

    if not acquire:
        return {"message": "Already running."}, 400

    try:
        thread_ridi = threading.Thread(target=ridi_scraping)
        thread_munpia = threading.Thread(target=munpia_scraping)
        thread_kakao = threading.Thread(target=kakao_scraping)
        thread_series = threading.Thread(target=series_scraping)

        thread_ridi.start()
        thread_munpia.start()
        thread_kakao.start()
        thread_series.start()

        thread_ridi.join()
        thread_munpia.join()
        thread_kakao.join()
        thread_series.join()


    finally:
        mutex.release()

    return "ok", 200

@app.get('/novel')
def get_novels(db: Session = Depends(get_db)):
    novels = db.query(Novel).all()
    return novels