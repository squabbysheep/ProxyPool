import redis
POOL = redis.ConnectionPool(url='redis://[:123456]@127.0.0.1:6379/db', max_connections=100)
conn = redis.Redis(connection_pool=POOL)

# conn = redis.Redis(host='127.0.0.1', port=6379, password=123456)
proxies = conn.smembers('JASON_POOL')
print(proxies)