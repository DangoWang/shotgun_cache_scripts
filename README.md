# shotgun_cache_scripts
scripts to cache shotgun database to postgresql
主要用来将shotgun的数据库缓存到本地postgresql上面，以大大提高查询速度。

# event
trigger the cache method to cache the data in real time.
用来触发缓存函数以实现实时缓存

# generate_tables
create tables and columns for postgre from shotgun
建表和同步所有字段

# init data
cache all the data from shotgun
将所有shotgun数据缓存下来
