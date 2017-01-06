#! /bin/bash 

python spider.py
cat hupu.json.fresh >> hupu.json.inc
python trans.py
netstat -ant | grep 8983 | grep LISTEN
if [ $? -eq 0 ] ; then
curl 'http://localhost:8983/solr/hupu/update?commit=true' --data-binary @/root/hupu/data/solr.json.fresh -H 'Content-type:application/json'
else
/root/solr-6.2.0/bin/solr start
sleep 10
curl 'http://localhost:8983/solr/hupu/update?commit=true' --data-binary @/root/hupu/data/solr.json.fresh -H 'Content-type:application/json'
fi
