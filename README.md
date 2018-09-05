Replaced by github.com/OAODEV/clubhouse-leadtime-extract

# pm-cli
Product management CLI for interacting with Clubhouse.io

currently a prototype, just does milestone calendar stuff.

## Clubhouse Milestone Calendar

### Usage

`CLUBHOUSE_API_KEY=<clubhouse_api_token> python proto.py`

or


```
docker build -t pm .
docker run -e CLUBHOUSE_API_TOKEN=<clubhouse_api_token> pm
```

Find the `app.yaml` and `clubhouse_api_token` in the keybase secret repo
