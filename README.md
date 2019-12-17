# iwell-deo

<div style="text-align:center;">
  <table >
    <tr>
      <a href="https://codeclimate.com/github/la-mar/iwell-deo/maintainability"><img src="https://api.codeclimate.com/v1/badges/35d6fa7af6b035c48b1c/maintainability" /></a>
      <a href="https://codeclimate.com/github/la-mar/iwell-deo/test_coverage"><img src="https://api.codeclimate.com/v1/badges/35d6fa7af6b035c48b1c/test_coverage" /></a>
      <a href="https://codecov.io/gh/la-mar/iwell-deo">
        <img src="https://codecov.io/gh/la-mar/iwell-deo/branch/master/graph/badge.svg" />
      </a>
      <a href="(https://circleci.com/gh/la-mar/iwell-deo">
        <img src="https://circleci.com/gh/la-mar/iwell-deo.svg?style=svg" />
      </a>
    </tr>
  </table>
</div>

## Getting Started

1. Install poetry package manager: `pip3 install poetry`
2. Install the dependencies from pyproject.toml: `poetry install`
3. Define the necessary environment variables (example below)
4. Run the app: `docker-compose up`

### Environment Variables

Example development configuration. Environment variables can either be defined at the system level or in a filed named '.env' in the project's root directory.

.env

```python

IWELL_CLIENT_ID=YOUR_CLIENT_ID
IWELL_CLIENT_SECRET=YOUR_CLIENT_SECRET
IWELL_URL=https://api.iwell.info/v1
IWELL_USERNAME=YOUR_USERNAME
IWELL_PASSWORD=YOUR_PASSWORD
IWELL_TOKEN_PATH=/oauth2/access-token

DATABASE_DRIVER="postgres"
DATABASE_USERNAME="iwell"
DATABASE_PASSWORD=""
DATABASE_HOST="localhost"
DATABASE_NAME="iwell"
DATABASE_SCHEMA="public"

SENTRY_DSN=""
SENTRY_ENABLED=false
LOG_LEVEL=10

FLASK_APP=iwell.manage.py
FLASK_ENV=development
APP_SETTINGS=iwell.config.DevelopmentConfig
SECRET_KEY=my_precious
```
