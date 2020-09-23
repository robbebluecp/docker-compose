"""=================================================

@Project    ：data
@IDE        ：PyCharm
@Author     ：Robbe
@Date       ：2020/9/20 11:30
@Desc       ：

Example:
    python3 -i redis -p 321
    python3 -i redis,mysql -p 233

=================================================="""


from pack import parseconfig
import re
import argparse

all = ['redis', 'mysql', 'rabbitmq', 'mongo']

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--images', help='images to build, like: redis or redis,mysql,mongo(seperated by ",")', default='all')
parser.add_argument('-p', '--password', help='a password for all images', default='321')
args = parser.parse_args()

images = args.images
password = args.password

if images.lower() == 'all':
    images = all
elif images.find(',') >= 0:
    images = images.split(',')
else:
    images = [images.strip()]

print('Image contains: 【%s】' % ','.join(images))
print('Password is：   【%s】' % password)

if password:
    f = open('config.cfg', 'r')
    cfg_text = f.read()
    cfg_text = re.sub('password=(.*?)\n', 'password=%s\n' % password, cfg_text)
    f.close()
    f = open('config.cfg', 'w')
    f.write(cfg_text)
    f.close()


config = parseconfig.ParseConfig('config.cfg').config
f = open('docker-compose-base.yml', 'r')
yml_text = f.read()
f.close()
char = ''
for key in config:
    if key not in images:
        continue
    ports = config[key].get('port', '')
    if isinstance(ports, str):
        for num, port in enumerate(ports.split(','), 1):
            config[key]['port%s' % num] = port
    items = re.search('# start %s([\s\S]+?)# end %s' % (key, key), yml_text).group(1)
    char += items % config[key]
    if key == 'redis':
        f = open('redis/config/redis_base.conf', 'r')
        mongo_text = f.read()
        mongo_text = mongo_text % config[key]
        f.close()
        f = open('redis/config/redis.conf', 'w')
        f.write(mongo_text)
        f.close()


char = """version: '3.1'\nservices:""" + char

f = open('docker-compose.yml', 'w')
f.write(char)
f.close()