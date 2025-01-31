curl --location --request POST 'http://localhost:8080/api/request' \
--header 'Content-Type: application/json' \
--data-raw '{
  "query": "В каком рейтинге (по состоянию на 2021 год) ИТМО впервые вошёл в топ-400 мировых университетов?\n1. ARWU (Shanghai Ranking)\n2. Times Higher Education (THE) World University Rankings\n3. QS World University Rankings\n4. U.S. News & World Report Best Global Universities",
  "id": 3
}'

curl --location --request POST 'http://localhost:8080/api/request' \
--header 'Content-Type: application/json' \
--data-raw '{
  "query": "В каком городе находится главный кампус Университета ИТМО?\n1. Москва\n2. Санкт-Петербург\n3. Екатеринбург\n4. Нижний Новгород",
  "id": 1
}'

curl --location --request POST 'http://localhost:8080/api/request' \
--header 'Content-Type: application/json' \
--data-raw '{
  "query": "В каком году Университет ИТМО был включён в число Национальных исследовательских университетов России?\n1. 2007\n2. 2009\n3. 2011\n4. 2015",
  "id": 2
}'
