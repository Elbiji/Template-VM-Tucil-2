import secrets
import base64
import pyotp
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from starlette.responses import FileResponse
from sqlmodel import create_engine, Session, SQLModel 
from typing import Annotated
from model import MOTD, MOTDBase

# SQLite Database
sqlite_file_name = "motd.db"
sqlite_url = f"sqlite:////{sqlite_file_name}"
connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
def get_session():
    with Session(engine) as session:
        yield session
SessionDep = Annotated[Session, Depends(get_session)]

# FastAPI
app = FastAPI(docs_url=None, redoc_url=None)
security = HTTPBasic()

# Users - lengkapi dengan userid dan shared_secret yang sesuai
users = {"sister" : "ii2210_sister_", "bagas" : "ii2210_bagas_" } 

@app.get("/")
async def root():

    	# Silahkan lengkapi dengan kode untuk memberikan index.html
	return FileResponse("index.html")

@app.get("/motd")
async def get_motd():

	# Silahkan lengkapi dengan kode untuk memberikan message of the day
	motds = session.exec(select(MOTD)).all()
	if not motds:
		raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "No MOTD found.")

	random_motd = random.choice(motds)
	return {"message" : random_motd.message}

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
				
				# Silahkan lengkapi dengan kode untuk menambahkan message of the day ke basis data
				new_motd = MOTD(message = message.message)
				session.add(new_motd)
				session.commit()
				return {"message": "MOTD added succesfully."}

			
			else:

				raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid userid or password.") 
			
		else:

			raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid userid or password.")
		
	except HTTPException as e:

	    raise e

if __name__ == "__main__":
	import uvicorn	
	# Silahkan lengkapi dengan kode untuk menjalankan server
	uvicorn.run(app, host ="0.0.0.0", port=17787)
