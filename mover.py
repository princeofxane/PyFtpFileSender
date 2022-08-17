import os
import yaml
import ftplib
import time
import logging

# TODO
# 1. Check if there is enough free space before the file gets copied. 
# 2. Write a function for server healthcheck.
# 3. Write a function to sum up file size and check if can be copied.
# 4. Copy to local path.

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

mover_config = ''

# get configuration.
with open('mover_config.yaml', 'r') as stream:
	try:
		mover_config = yaml.safe_load(stream)
	except yaml.YAMLError as exception:
		print(exception)
		
auth_info = mover_config['authentication']
server_info = mover_config['server_info']
ftp_string = server_info['server'] + ':' + str(server_info['port'])

# + ftp connection.
ftp_session = ftplib.FTP()
ftp_session.connect(server_info['server'], server_info['port'])
logging.info('ftp server is online..')
ftp_session.login(auth_info['username'], auth_info['password'])
logging.info('authentication successful..')

# -> close the connection if path is not root.
if ftp_session.pwd() != '/':
	logging.error('not root directory..')
	ftp_session.close()

from_path = mover_config['from_path']
to_path = mover_config['to_path']

# -> change directory to photos.
ftp_session.cwd(to_path)

current_created_date = ''
doesExist = False

logging.info('files are being uploaded..')
for file in os.scandir(from_path):
	created_date = file.stat().st_mtime

	if current_created_date == created_date or current_created_date == '':

		# dir_name = datetime.fromtimestamp(created_date).strftime('%b_%Y')
		dir_name = time.strftime('%b_%Y', time.localtime(created_date))

		# create directory if doesn't exist.
		if dir_name not in ftp_session.nlst():
			ftp_session.mkd(dir_name)
		ftp_session.cwd(dir_name)
		
		# open file and read it in binary mode.
		file_content = open(from_path + file.name, 'rb')
	
		# check for redundancy.
		for name, facts in ftp_session.mlsd():
			if name == file.name:
				doesExist = True

		if not doesExist:
			# upload file.
			ftp_session.storbinary(f'STOR {file.name}', file_content)
			ftp_session.cwd('..')
		file_content.close()
		

logging.info('upload is done..')
