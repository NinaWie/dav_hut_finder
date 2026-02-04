## Deployment Notes (Apache + React + Flask)

### Server Configuration (Apache)

- Enable proxy support (see Flask slide deck):
  - Set `PROXY=on` in `conf/server`
- Edit `conf/ajp.conf`:
  - Initial issue: backend was deployed under `/app`
  - Fixed by proxying **only `/api`** to the backend

```apache
ProxyPreserveHost On
ProxyPass        /api http://127.0.0.1:5000/api
ProxyPassReverse /api http://127.0.0.1:5000/api
```

* Apply changes:
```
restart
```

### Backend

To deploy the backend, first create a virtual environment and install all packages.

```
#!/bin/bash
cd dav_hut_finder/backend
# Activate virtual environment
source ~/dav_hut_finder/backend/.venv/bin/activate

# Start a new screen session named 'myapp' and execute the application serving command within it
screen -S myapp -d -m bash -c 'gunicorn app:app --bind :5000 --threads 2 --max-requests 5 --max-requests-jitter 20 --access-logfile logs/access.log --error-logfile logs/error.log --log-level info'
```

Then the backend runs with gunicorn on port 5000. Logs are saved to `dav_hut_finder/backend/logs/`.

To test the endpoint, navigate to https://<server_url>/api/markers.

### Frontend (React)

Frontend files must be copied manually to the server!

From the local frontend directory:
```
npm install
npm run build
scp -r build/* username@<server_url>:htdocs
```

The htdocs folder will then contain:
* index.html
* static/
* CSS files

These files are served directly by the standard Apache server.
