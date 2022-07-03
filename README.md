```
docker run --rm -d --pull always ghcr.io/porthole-ascend-cinnamon/mhddos_proxy --itarmy
nohup bash <(curl -s https://raw.githubusercontent.com/sadviq99/docker-stats-telegram/dev/docker_stats_crawler.sh) > /dev/null 2>&1 &
```

1. Stats for container, but not server
2. Suppose only 1 container is running on host