FROM nginx:latest

# 기존 default.conf 삭제
RUN rm /etc/nginx/conf.d/default.conf

# 사용자 설정 복사
COPY nginx.conf /etc/nginx/conf.d/nginx.conf
COPY nginx/.htpasswd /etc/nginx/.htpasswd
