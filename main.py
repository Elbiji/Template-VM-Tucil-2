import os
import random
import base64
import secrets
import pyotp
from sqlmodel import Field, SQLModel, create_engine, Session, select
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import FileResponse
from typing import Annotated

# SQLite Database
sqlite_file_name = "motd.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

# MOTD Model
class MOTDBase(SQLModel):
    motd: str

class MOTD(MOTDBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    creator: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

# User Dictionary
users = {
    "sister": "ii2210_sister_1234",
    "bagas": "ii2210_bagas_5678"
}

# Fungsi Membuat Database dan Tabel
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    print("Database tables created successfully")
    with Session(engine) as session:
        existing_motds = session.exec(select(MOTD)).all()
        if not existing_motds:
            initial_motds = [
                MOTD(motd="Welcome to the new system!", creator="admin"),
                MOTD(motd="Don't forget to check your emails!", creator="admin"),
                MOTD(motd="Today's task: Review the new feature.", creator="admin")
            ]
            session.add_all(initial_motds)
            session.commit()
            print("Initial MOTDs added to the database.")

# Periksa Eksistensi Database
def check_db():
    if not os.path.exists(sqlite_file_name):
        print(f"Database file {sqlite_file_name} does not exist. Creating new tables.")
        create_db_and_tables()
    else:
        print(f"Database file {sqlite_file_name} found.")

# Cek Database Saat Startup
check_db()

# FastAPI Setup
app = FastAPI(docs_url=None, redoc_url=None)
security = HTTPBasic()

# Dependency untuk Session
def get_session():
    with Session(engine) as session:
        yield session
SessionDep = Annotated[Session, Depends(get_session)]

# Endpoint Index
@app.get("/")
async def root():
    return FileResponse("index.html")

# Endpoint GET /motd
@app.get("/motd")
async def get_motd(session: SessionDep):
    motds = session.exec(select(MOTD)).all()
    if not motds:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No MOTD available")
    random_motd = random.choice(motds)
    return {"message": random_motd.motd}

# Endpoint POST /motd
@app.post("/motd")
async def post_motd(message: MOTDBase, session: SessionDep, credentials: Annotated[HTTPBasicCredentials, Depends(security)]):

	current_password_bytes = credentials.password.encode("utf8")

	valid_username, valid_password = False, False

	try:

		if credentials.username in users:
			valid_username = True
			s = base64.b32encode(users.get(credentials.username).encode("utf-8")).decode("utf-8")
			totp = pyotp.TOTP(s=s,digest="SHA256",digits=8)
			valid_password = secrets.compare_digest(current_password_bytes,totp.now().encode("utf8"))

			if valid_password and valid_username:

				print(f"Received message: {message}")
				# Silahkan lengkapi dengan kode untuk menambahkan message of the day ke basis data
				new_motd = MOTD(motd = message.motd, creator = credentials.username)
				session.add(new_motd)
				session.commit()
				return {"message": "MOTD added succesfully."}

			else:

				raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid userid or password.") 

		else:

			raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid userid or password.")

	except HTTPException as e:

	    raise e


# Jalankan Server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=17787)
