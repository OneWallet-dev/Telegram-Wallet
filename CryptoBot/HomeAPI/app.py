from typing import Union

from pydantic import BaseModel

from fastapi import FastAPI, Path, Form

app = FastAPI()


@app.post("/crypt_callback/{from_path}")
def crypt_callback(
        *,
        item: str = Form(),
        param: Union[str, None] = None,
        from_path: int = Path(title="The ID of the item to get", ge=0, le=1000)
):
    return {"RESULT": 1}
