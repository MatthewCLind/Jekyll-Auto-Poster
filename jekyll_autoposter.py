import os
import json
import random
from datetime import date
import pysftp

dates = str(date.today())

with open('config.json','r') as f:
    config = json.load(f)

# line of code from stackoverflow.com/a/40347279 
directories = [f.name for f in os.scandir('.') if f.is_dir()]

print(directories)

if len(directories) == 0:
    print('there is nothing here to post')
    raise SystemExit(0)

next_post_title = random.choice(directories)

os.chdir('./' + next_post_title)

new_post_path = config['site_root_path'] + '/_posts/' + dates
new_assets_path = config['site_root_path'] + '/assets/' + next_post_title

os.mkdir(new_assets_path)
post_fm = []

for item in os.listdir():
    if item[-9:] == '.markdown' or item[-3:] == '.md':
        with open(item, 'r') as post:
            temp = ''
            front_matter = False
            for line in post:
                if line == '---\n':
                    front_matter = not front_matter
                elif front_matter:
                    post_fm.append(line)
                else:
                    temp += line
            print(post_fm)
        with open(item, 'w') as post:
            post.write('---\n')
            for var, matter in config['front_matter'].items():
                post.write(var + ': ' + matter)
                post.write('\n')
            post.write('title: ' + next_post_title + '\n')
            for fm in post_fm:
                post.write(fm)
            post.write('---\n')
            post.write(temp)
        os.rename('./' + item, new_post_path + '-' + item)
    else:
        os.rename('./' + item, new_assets_path + '/' + item)

os.chdir('../')
os.rmdir('./' + next_post_title)

os.chdir(config['site_root_path'])
os.system('/usr/local/bin/jekyll build')


if 'SFTP' in config:
    creds = config['SFTP']
    with pysftp.Connection(creds['hostname'], username=creds['username'], password=creds['password']) as sftp:
        #sftp.chdir(creds['put_path'])
        sftp.put_r(config['site_root_path'] + '/' + '_site', creds['put_path'])
