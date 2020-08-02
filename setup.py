import os
import sys

def kill():
	os.system("ps aux | grep ython | grep daily_read_bot | awk '{print $2}' | xargs kill -9")

def setup():
	kill()
	if 'kill' in str(sys.argv):
		return 
	addtional_arg = ' '.join(sys.argv[1:])
	command = 'python3 -u daily_read_bot.py %s' % addtional_arg
	if 'debug' in addtional_arg:
		os.system(command + ' test')
	else:
		os.system('touch nohup.out')
		os.system('nohup %s & ' % command)
		if 'notail' not in sys.argv:
			os.system('tail -F nohup.out')

if __name__ == '__main__':
	setup()