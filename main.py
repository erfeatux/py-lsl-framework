#!/bin/env python3

import uvicorn
from fastapi import FastAPI

from lslframework import App

app = FastAPI()
fw = App(app)


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
