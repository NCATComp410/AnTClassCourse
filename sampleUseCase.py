import re
import yaml
import time
import paramiko


def connect_traffic_gen(params):
	'''
	This function is to connect to traffic generator and run traffic

	'''
	traffic_gen = paramiko.SSHClient()
	traffic_gen.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	try:
		print('Connecting to traffic generator {}'.format(params["traffic_gen"]["IP"]))
		traffic_gen.connect( params["traffic_gen"]["IP"], port=22, username = params["traffic_gen"]["Username"], password = params["traffic_gen"]["Password"], look_for_keys=False )
	except Exception as e:
		return False,'SSH Connection error! {}'.format(e)
	print('\nConnected to traffic generator...preparing to run traffc...')
	stdin,stdout,stderr = traffic_gen.exec_command('cd trex/v2.24;./runtrex')
	time.sleep(90)
	return True


def connect_csr1000v(params):
	'''
	This function is to connect to csr1000v and run 'show commnds'

	'''
	csr1000v = paramiko.SSHClient()
	csr1000v.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	try:
		print('\nConnecting to csr1000v {}'.format(params["csr1000v"]["IP"]))
		csr1000v.connect( params["csr1000v"]["IP"], port=22, username = params["csr1000v"]["Username"], password = params["csr1000v"]["Password"], look_for_keys=False )
	except Exception as e:
		return False,'SSH Connection error! {}'.format(e)
	
	print('\nConnected to csr1000v...checking for traffic on interfaces...')
	stdin,stdout,stderr = csr1000v.exec_command('show interfaces summary')
	output = stdout.readlines()
	pattern = r'.*?GigabitEthernet[\d+](\s*\d+){4}\s*([1-9]\d.*)'
	output = str(output)
	ret = re.search(pattern,output)
	if ret:
		return True, output
	else:
		return False, output
		

#Load the yaml file to read parameters needed for test
with open('params.yaml', 'r') as f:
	params = yaml.load(f)

#Connect to the csr1000v anf traffic generator and see if traffic is running between them.
status = connect_traffic_gen(params)
if status:
	print('\nTraffic generator is up and sending traffic...')
else:
	print('\nTraffic generator is not running...please give it a try again...')
	

status,output = connect_csr1000v(params)
if status:
	print('\nTraffic test Passed...\n\nThe RX/TX counters for interfaces got updated...\n\n{}'.format(output))
else:
	print('\nTraffic test failed...\n{}'.format(output))



