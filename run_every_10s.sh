#!/bin/bash
# run_every_10s.sh
while true; do
  curl 'http://localhost:80/update_keys/' \
    -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7' \
    -H 'Accept-Language: zh-CN,zh;q=0.9' \
    -H 'Cache-Control: max-age=0' \
    -H 'Connection: keep-alive' \
    -H 'Cookie: _ga=GA1.1.764944384.1708936219; _ga_8PRS69JJRL=GS1.1.1708936218.1.1.1708936928.0.0.0' \
    -H 'Sec-Fetch-Dest: document' \
    -H 'Sec-Fetch-Mode: navigate' \
    -H 'Sec-Fetch-Site: none' \
    -H 'Sec-Fetch-User: ?1' \
    -H 'Upgrade-Insecure-Requests: 1' \
    -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36' \
    -H 'sec-ch-ua: "Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"' \
    -H 'sec-ch-ua-mobile: ?0' \
    -H 'sec-ch-ua-platform: "macOS"'
  sleep 10
done