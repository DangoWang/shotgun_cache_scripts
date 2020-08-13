# scripts to cache shotgun database to postgresql
# 主要用来将shotgun的数据库缓存到本地postgresql上面，以大大提高查询速度。
# 脚本说明

## event
trigger the cache method to cache the data in real time.<br>
用来触发缓存函数以实现实时缓存

## generate_tables
create tables and columns for postgre from shotgun<br>
建表和同步所有字段

## initial_data
cache all the data from shotgun<br>
将所有shotgun数据缓存下来

## api
find and find_one wrapped method in form of shotgun_api3 but with query target of your postgresql server.<br>按照shotgun_api3的查询api方式封装了两个方法：find 和 find_one.这样你不必更改之前的代码了.

# 依赖
python2.7<br>
shotgun_api3<br>
psycopg2
