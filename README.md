# Basic Deploy Tool

A simple systemd program that runs a command on your server when calling an API

### Install:
- Clone this project at `/opt` and run these commands from `/opt/basic-deploy-tool`:
  ```shell
    python3 -m virtualenv .venv
    . .venv/bin/activate
    pip install -r requirements.txt
  ```

### Config Deploy tokens and commands:
- Create `config.json` file next to the `main.py` file. The content of the file should be as `example-config.json` file.
- In the `deploy_token` field Insert a token. you can run this command to generate tokens:
  ``` python
    import secrets
    secrets.token_urlsafe(50)
  ```
- In the `shell_command` field insert the commands that you want to run on calling the webhook. For example you may run:
  ```shell
    cd /opt/my-site/ && git reset --hard && git pull && .venv/bin/python manage.py migrate && systemctl daemon-reload && systemctl restart my_site.service
  ```

### Config Systemd:
- run these commands:
  ```shell
    cd /etc/systemd/system/
    ln -s /opt/basic-deploy-tool/deploy_tool.service
    systemctl enable deploy_tool.service
    systemctl start deploy_tool.service
  ```

### Config Nginx
- You should route the traffic of path `/deploy-from-git` to the port 8005 where the deploy-tool is running.
- Add the configuration below to config file of your Nginx. It is located in `/etc/nginx/sites-available/`.
  ```
    location /deploy-from-git {
      proxy_pass http://127.0.0.1:8005;
    }
  ```
- If you want to change the path, modify Nginx configuration and `main.py` file.
- If you want to change the port, modify Nginx configuration and `deploy_tool.service` file then run this command: `systemctl daemon-reload; systemctl restart deploy_tool.service;`

### Config GitHub Action
- In your repository go to `settings > Secrets and variables > Actions` and click on `New repository secret` then in the name section insert `DEPLOY_TOKEN` and in the secret section insert the token you have generated before.
- Create a new workflow in GitHub Action from this code:
  ```yaml
    on:
      push:
        branches:
        - main
    
    jobs:
      deploy:
        runs-on: ubuntu-latest
        steps:
        - name: Send Deploy Request
          id: deploy
          uses: fjogeleit/http-request-action@v1
          with:
            url: 'https://<YOUR-SITE-DOMAIN>/deploy-from-git'
            method: 'GET'
            timeout: 20000
            customHeaders: '{"Authorization": "${{ secrets.DEPLOY_TOKEN }}"}'
        - name: Log Deploy Response
          run: |
            echo "detail: ${{ fromJson(steps.deploy.outputs.response).detail }}"
            echo "stdout: ${{ fromJson(steps.deploy.outputs.response).stdout }}"
            echo "stderr: ${{ fromJson(steps.deploy.outputs.response).stderr }}"
        - name: Check deploy failure
          if: ${{ failure() || !fromJSON(steps.deploy.outputs.response).success}}
          run: exit 1
  ```

### Congratulations
Now if you push on master the code automatically deployed on your server.
