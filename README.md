# Using Flask to make a simple website

## Using docker
```docker build -t {image-name} .```
```docker volume create {volume-name}```
```docker run -dp 5000:5000 --mount type=volume,src={volume-name},target=/app/instance --name {container-name} {image-name}```
## Install dependencies
```pip install -e .```

## Run app
*First time*
```flask --app webGHT init-db```

```flask --app webGHT run --debug```
