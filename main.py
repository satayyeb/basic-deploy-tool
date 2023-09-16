import json
import os

from fastapi import FastAPI, Depends, HTTPException, Request

app = FastAPI()

with open('config.json', 'r') as file:
    configs = json.load(file)


def verify_token(req: Request):
    if token := req.headers.get("Authorization", None):
        for config in configs:
            if token == config['deploy_token']:
                return config
    raise HTTPException(status_code=401, detail="Unauthorized")


@app.get("/deploy-from-git")
async def deploy(config: dict = Depends(verify_token)):
    os.system(config['shell_command'])
    return {'detail': 'Deployed'}