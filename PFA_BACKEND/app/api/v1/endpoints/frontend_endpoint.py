from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(
    prefix="/front"
)

@router.get("/",response_class=HTMLResponse)
def index():
    return """
    <html>
        <head>
            <title>PFA</title>
        </head>
        <body style=background:grey;>
            <h1>Hello PFA 🚀</h1>
            <p>To jest prosty HTML z FastAPI</p>

            <h2>Prześlij plik</h2>
            <form action="/api/v1/files/uploads/upload" method="post" enctype="multipart/form-data">
                <input type="file" name="file" />
                <button type="submit">Wyślij plik</button>
            </form>
        </body>
    </html>
    """