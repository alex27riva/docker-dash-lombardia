# Docker Lombardy dashboard
Lombardy docker image for [Covid-Dashboard](https://github.com/alex27riva/Covid-dashboard) thesis project.

## Building
`docker build -t alex27riva/dash_lombardia:latest .`

## Run
`docker run --restart=always --name dashboard_lombardia -d -p 8051:8050 alex27riva/dash_lombardia`