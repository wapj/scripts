#!/bin/bash

GAMEDB=pokopoko_Game
LOGDB=pokopoko_Log

for ((i = 1; i < 11; i++));do
    if [ $i != 10 ];then
        echo "CREATE DATABASE ${GAMEDB}0$i character set utf8;"
        echo "CREATE DATABASE ${LOGDB}0$i character set utf8;"
        mysql -u root ${GAMEDB}0$i < pokopoko_Game.sql
        mysql -u root ${LOGDB}0$i < pokopoko_Log.sql
    else
        echo "CREATE DATABASE ${GAMEDB}$i character set utf8;"
        echo "CREATE DATABASE ${LOGDB}$i character set utf8;"
        mysql -u root ${GAMEDB}$i < pokopoko_Game.sql
        mysql -u root ${LOGDB}$i < pokopoko_Log.sql
    fi
done
