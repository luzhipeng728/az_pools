#!/bin/bash
# run_every_10s.sh

# 定义检查和可能杀死进程的函数
check_and_kill_if_needed() {
    local threshold=30  # 定义内存使用率的阈值

    local uvicorn_pids=$(pgrep -f uvicorn)

    # 打印当前检查的时间，以便跟踪脚本执行
    echo "Checking uvicorn processes at $(date)"

    if [ -z "$uvicorn_pids" ]; then
        echo "No uvicorn processes found"
        return
    fi

    for pid in $uvicorn_pids; do
        local memory_usage=$(ps -p $pid -o %mem --no-headers | tr -d ' ' | cut -d'.' -f1)

        # 打印每个进程的内存使用情况，即使它没有超过阈值
        echo "Uvicorn process (PID: $pid) is using $memory_usage% of memory."

        if [ "$memory_usage" -gt "$threshold" ]; then
            echo "Uvicorn process (PID: $pid) memory usage ($memory_usage%) exceeds threshold ($threshold%). Killing..."
            kill $pid

            sleep 1

            if kill -0 $pid 2>/dev/null; then
                echo "Process (PID: $pid) did not terminate after initial kill, forcing kill."
                kill -9 $pid
            else
                echo "Process (PID: $pid) terminated successfully."
            fi
        fi
    done
}


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
  sleep 4
  check_and_kill_if_needed
done