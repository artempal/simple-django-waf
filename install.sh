RED_START='\033[37;1;41m'
RED_END='\033[0m'
NEWLINE=$'\n'
INSTALL_COMPONENTS=""
echo -n "Необходимо ли установить СУБД и веб-модуль? (y/n) "

read db_install
case "$db_install" in
    y|Y)
        INSTALL_COMPONENTS+=" db web"
        TEMPLATE_POSTGRES_PASSWORD=$(python -c 'import random; print("".join([random.choice("abcdefghijklmnopqrstuvwxyz0123456789") for i in range(10)]))')
        export TEMPLATE_POSTGRES_PASSWORD
        echo -e "${RED_START}Запишите пароль от СУБД${RED_END}: ${TEMPLATE_POSTGRES_PASSWORD}"
        export TEMPLATE_POSTGRES_HOST=db

        export TEMPLATE_DJANGO_KEY=$(python -c 'import random; print("".join([random.choice("abcdefghijklmnopqrstuvwxyz0123456789") for i in range(50)]))')
        echo -e "${RED_START}Запишите секретный ключ${RED_END}: ${TEMPLATE_DJANGO_KEY}"

        read -p "Введите домен или ip защищаемого сайта [https://localhost]: " TEMPLATE_APP_HOSTNAME
        TEMPLATE_APP_HOSTNAME=${TEMPLATE_APP_HOSTNAME:-https://localhost}
        export TEMPLATE_APP_HOSTNAME
        
        read -p "Введите порт работы прокси [444]: " TEMPLATE_PROXY_PORT
        TEMPLATE_PROXY_PORT=${TEMPLATE_PROXY_PORT:-444}
        export TEMPLATE_PROXY_PORT

        echo -n "Необходимо ли использовать HTTPS? (y/n) "

        read https
        case "$https" in
            y|Y)
                TEMPLATE_HTTPS_ON_PROXY=True
                export TEMPLATE_HTTPS_ON_PROXY
                ;;

            n|N)
                TEMPLATE_HTTPS_ON_PROXY=False
                export TEMPLATE_HTTPS_ON_PROXY
                ;;
            *) exit 0
                ;;
        esac

        read -p "Введите порт, на котором будет работать веб-консоль [8000]: " TEMPLATE_ADMIN_CONSOLE_PORT
        TEMPLATE_ADMIN_CONSOLE_PORT=${TEMPLATE_ADMIN_CONSOLE_PORT:-8000}
        export TEMPLATE_ADMIN_CONSOLE_PORT

        export TEMPLATE_DJANGO_ROOT_PASS=$(python -c 'import random; print("".join([random.choice("abcdefghijklmnopqrstuvwxyz0123456789") for i in range(8)]))')
        echo -e "${RED_START}Запишите пароль root от панели администрирования${RED_END}: ${TEMPLATE_DJANGO_ROOT_PASS}"

        ;;
    n|N)
        read -p "Введите хост СУБД: " TEMPLATE_POSTGRES_HOST
        export TEMPLATE_POSTGRES_HOST

        read -p "Введите пароль от СУБД: " TEMPLATE_POSTGRES_PASSWORD
        export TEMPLATE_POSTGRES_PASSWORD

        read -p "Введите секретный ключ: " TEMPLATE_DJANGO_KEY
        export TEMPLATE_DJANGO_KEY
        ;;
    *) exit 0
        ;;
esac

read -p "Введите название базы Postgres [simple-waf]: " TEMPLATE_POSTGRES_DBNAME
TEMPLATE_POSTGRES_DBNAME=${TEMPLATE_POSTGRES_DBNAME:-simple-waf}
export TEMPLATE_POSTGRES_DBNAME

read -p "Введите имя пользователя [waf]: " TEMPLATE_POSTGRES_USER
TEMPLATE_POSTGRES_USER=${TEMPLATE_POSTGRES_USER:-waf}
export TEMPLATE_POSTGRES_USER

export TEMPLATE_HTTPS_ON_PROXY=False

echo -n "Необходимо ли установить модуль Redis? (y/n) "

read redis_install
case "$redis_install" in
    y|Y)
        INSTALL_COMPONENTS+=" redis"
        TEMPLATE_REDIS_PASSWORD=$(python -c 'import random; print("".join([random.choice("abcdefghijklmnopqrstuvwxyz0123456789") for i in range(12)]))')
        export TEMPLATE_REDIS_PASSWORD
        echo -e "${RED_START}Запишите пароль Redis${RED_END}: ${TEMPLATE_REDIS_PASSWORD}"
        ;;
    n|N)

        ;;
    *) exit 0
        ;;
esac


echo -n "Необходимо ли установить модуль Proxy? (y/n) "

read proxy_install
case "$proxy_install" in
    y|Y)
        INSTALL_COMPONENTS+=" proxy"
        read -p "Введите внешний IP прокси: " TEMPLATE_PROXY_HOST
        export TEMPLATE_PROXY_HOST

        read -p "Введите адрес базы Redis [не использовать]: " TEMPLATE_REDIS_HOST
        TEMPLATE_REDIS_HOST=${TEMPLATE_REDIS_HOST:-None}
        export TEMPLATE_REDIS_HOST

        read -p "Введите пароль от Redis [не использовать]: " TEMPLATE_REDIS_PASSWORD
        TEMPLATE_REDIS_PASSWORD=${TEMPLATE_REDIS_PASSWORD:-None}
        export TEMPLATE_REDIS_PASSWORD

        echo -n "Необходимо ли сгенерировать сертификат? (y/n) "

        read cert
        case "$cert" in
            y|Y)
                mkdir certs
                openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout certs/mydomain.key -out certs/mydomain.crt -subj '/CN=localhost'

                ;;

            n|N)
                ;;
            *) exit 0
                ;;
        esac
        ;;

    n|N)
        ;;
    *) exit 0
        ;;
esac

echo -n "Необходимо ли установить модуль HAProxy? (y/n) "

read haproxy_install
case "$haproxy_install" in
    y|Y)
        INSTALL_COMPONENTS+=" haproxy"
        read -p "Введите порт HAProxy [443]: " TEMPLATE_HAPROXY_PORT
        TEMPLATE_HAPROXY_PORT=${TEMPLATE_HAPROXY_PORT:-443}
        export TEMPLATE_HAPROXY_PORT

        read -p "Введите порт для отслеживания статистики HAProxy [8080]: " TEMPLATE_HAPROXY_STATS_PORT
        TEMPLATE_HAPROXY_STATS_PORT=${TEMPLATE_HAPROXY_STATS_PORT:-8080}
        export TEMPLATE_HAPROXY_STATS_PORT

        if [ -z ${TEMPLATE_PROXY_PORT+x} ]; then
            read -p "Введите порт работы прокси [444]: " TEMPLATE_PROXY_PORT
            TEMPLATE_PROXY_PORT=${TEMPLATE_PROXY_PORT:-444}
            export TEMPLATE_PROXY_PORT
        fi

        echo -n "Введите через пробел IP адреса прокси:"
        read -a PROXIES
        TEMPLATE_PROXY_SERVERS_HAPROXY=""

        for PROXY in "${PROXIES[@]}"; do
           TEMPLATE_PROXY_SERVERS_HAPROXY+="server server_${PROXY} ${PROXY}:${TEMPLATE_PROXY_PORT} check${NEWLINE}   "
        done
        export TEMPLATE_PROXY_SERVERS_HAPROXY

        envsubst < config_templates/haproxy.cfg > haproxy.cfg
        ;;
    n|N)

        ;;
    *) exit 0
        ;;
esac



echo -n "Необходимо ли установить модуль Grafana? (y/n) "

read grafana_install
case "$grafana_install" in
    y|Y)
        INSTALL_COMPONENTS+=" grafana"
        read -p "Введите порт для работы Grafana [3000]: " TEMPLATE_GRAFANA_PORT
        TEMPLATE_GRAFANA_PORT=${TEMPLATE_GRAFANA_PORT:-3000}
        export TEMPLATE_GRAFANA_PORT

        echo -e "${RED_START}Запишите пароль admin от панели администрирования${RED_END}: admin"
        rm -rf grafana
        mkdir -p grafana/datasources
        envsubst < config_templates/grafana/datasources/postgres.yaml > grafana/datasources/postgres.yaml
        envsubst < config_templates/grafana/datasources/redis-ban.yaml > grafana/datasources/redis-ban.yaml
        envsubst < config_templates/grafana/datasources/redis-hash.yaml > grafana/datasources/redis-hash.yaml

        cp -a config_templates/grafana/dashboards grafana/dashboards
        ;;
    n|N)

        ;;
    *) exit 0
        ;;
esac

TEMPLATE_ADMIN_CONSOLE_PORT=${TEMPLATE_ADMIN_CONSOLE_PORT:-8000}
export TEMPLATE_ADMIN_CONSOLE_PORT

TEMPLATE_HAPROXY_PORT=${TEMPLATE_HAPROXY_PORT:-443}
export TEMPLATE_HAPROXY_PORT

TEMPLATE_HAPROXY_STATS_PORT=${TEMPLATE_HAPROXY_STATS_PORT:-8080}
export TEMPLATE_HAPROXY_STATS_PORT

TEMPLATE_GRAFANA_PORT=${TEMPLATE_GRAFANA_PORT:-3000}
export TEMPLATE_GRAFANA_PORT

TEMPLATE_REDIS_PASSWORD=${TEMPLATE_REDIS_PASSWORD:-password}
export TEMPLATE_REDIS_PASSWORD

envsubst < config_templates/.env > .env

envsubst < config_templates/docker-compose.yml > docker-compose.yml


docker-compose up -d --build ${INSTALL_COMPONENTS}