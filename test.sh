#!/bin/bash
# File Name : test-sogou-api.sh

curl 'https://translate.sogou.com/reventondc/translateV1' --data 'from=auto&to=zh-CHS&text=hell&useDetect=on&useDetectResult=on&needQc=1&oxford=on&isReturnSugg=on&s=d6502f425544ede0d9e315efaa774327' 2>/dev/null

cat << EOL
> POST /reventondc/translateV1 HTTP/1.1
> Host: translate.sogou.com
> User-Agent: curl/7.54.0
> Accept: */*
> Content-Length: 131
> Content-Type: application/x-www-form-urlencoded
EOL
