# Running Jupyter server

docker build -t coffenbacher/reddit-extractor .;\
docker run -it \
    --net host \
    -e TUTUM_IP_ADDRESS=10.7.0.8 \
    -v /root/.jupyter:/root/.jupyter \
    -v /root/workspace/reddit-extractor/notebooks:/notebooks \
    -p 7777:7777 \
    -w /notebooks \
    coffenbacher/reddit-extractor jupyter notebook


Build and deploy with Docker:
docker build -t stats-collector-rethinkdb .;\
docker tag -f stats-collector-rethinkdb tutum.co/charlie/stats-collector-rethinkdb;\
docker push tutum.co/charlie/stats-collector-rethinkdb

Build and run with Docker:
docker build -t stats-collector-rethinkdb .;\
docker run  --env-file .env -e DEBUG_LEVEL=DEBUG -e BATCH_SIZE=2 --net host -it stats-collector-rethinkdb python worker.py competitive Amazon_GetCompetitivePricingForASIN

docker build -t stats-collector-rethinkdb .;\
docker run  --env-file .env -e DEBUG_LEVEL=DEBUG -e BATCH_SIZE=2 --net host -it stats-collector-rethinkdb python worker.py prices Amazon_GetLowestOfferListingsForASIN

docker build -t stats-collector-rethinkdb .;\
docker run  --env-file .env -e DEBUG_LEVEL=DEBUG -e BATCH_SIZE=2 --net host -it stats-collector-rethinkdb python worker.py valore Valore