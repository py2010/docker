#!/bin/bash


f=`basename $0` #当前文件名d
p="$( cd "$( dirname "$0"  )" && pwd  )" #脚本目录c路径

base=`dirname "$p"` #sdj路径

cd $base #sdj



run() {
    #用于启动停止django网站进程
    arg1=$1
    # echo $arg1
    ifs=$IFS; IFS="\n"; 
    proc="$(ps -ef | grep -Ei '(c/d runworker|daphne|runserver 0.0.0.0:8088|c/d cert|python -u manage.py)' | grep -v 'grep')"

    if [ "$arg1" == "stop" ];then
        if [ -z "$2" ];then
            echo "Stopping....."
            echo -e $proc | awk '{print $2}' | xargs kill -9 2>/dev/null
        else
            echo "结束端口 <$2> 进程..."
            netstat -tnlp|grep :$2|awk '{print $7}' |awk -F '/' '{print $1}' | xargs kill -9 2>/dev/null
            #${s%/*}
        fi
    elif [ "$arg1" == "start" ];then
        pid=`echo -e $proc | awk '{print $2}'`
        if [ -z "$pid" ];then
            nohup $p/$f runworker --only-channels=websocket.* >& worker.log --threads 16 & #websocket后端进程只创建一个，以免发生多进程共享变量的问题
            nohup $p/$f runworker --only-channels=http.* --threads 4 >& worker_2.log & #python单进程只能使用单核CPU
            nohup $p/$f runworker --only-channels=http.* --threads 4 >& worker_3.log & #python单进程只能使用单核CPU
            nohup $p/$f cert 4 >& cert.log &
            nohup daphne -t 150 -b 0.0.0.0 -p 8088 --ws-protocol "graphql-ws" --proxy-headers sdj.asgi:channel_layer >& daphne.log &
            echo "Starting....."
            sleep 1
            ps aux | grep -Ei '(runworker|daphne|runserver 0.0.0.0:8088)' | grep -v 'grep'
        else
            echo -e $proc
            echo "已有相关进程运行中，忽略处理"
        fi

    elif [ "$arg1" == "state" ];then
        if [ -z "$proc" ];then
            echo "No running.."
        else
            echo -e $proc
        fi

    fi
    IFS=$ifs
}








arg1=$1
arg2=$2


if ([ "$arg1" -gt 0 ] 2>/dev/null && [ -z "$arg2" ]) ;then 
    arg2='0.0.0.0:'${arg1}
    arg1='runserver'

elif [ "$arg1" == "m1" ];then
	arg1='makemigrations'
elif [ "$arg1" == "m2" ];then
	arg1='migrate'
    if [ "$arg2" == "gs" ];then
        arg2='--database gslb'
    fi

elif [ "$arg1" == "u" ];then
    arg1='createsuperuser'

elif [ "$arg1" == "h" ];then
    arg1='help'
elif [ "$arg1" == "s" ];then
    arg1='shell'
    python manage.py shell
    exit



elif [ -z "$arg1" ];then
    arg1='runserver'
    arg2='0.0.0.0:8088'
#elif [ -z "$arg2" ];then
#    arg2='0.0.0.0:'${arg1}
#    arg1='runserver'

elif [ "$arg1" == "stop" ];then
    run $arg1 $2
    exit
elif [ "$arg1" == "start" ];then
    run $arg1
    exit
elif [ "$arg1" == "state" ];then
    run $arg1
    exit
elif [ "$arg1" == "restart" ];then
    run "stop"
    sleep 1
    run "start"
    exit


fi











#echo $arg1
#echo $arg2


python -u manage.py $arg1 $arg2 $3 $4


#c/daphne -b 0.0.0.0 -p 8088 --ws-protocol "graphql-ws" --proxy-headers sdj.asgi:channel_layer





