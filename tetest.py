import requests
from requests.auth import HTTPBasicAuth
import sys
from time import sleep

#possibly declare as global
# # print(sys.argv)

# user_id = sys.argv[1]
# user = sys.argv[2]
# pw =sys.argv[3]
# si = sys.argv[4]
# os_api_name = sys.argv[5]
# browser_api_name = sys.argv[6]
# fileHash = sys.argv[7]



class SI(object):
    def __init__(self, si, config_id, os_api_name):
        self.si = si
        self.config_id = config_id
        self.os_api_name = os_api_name

    def is_available(self):
        url = "https://crossbrowsertesting.com/jreese/checkImageState.php?si={}".format(self.si)
        resp = requests.get(url).text
        return bool(int(resp))

    def reserve(self, user_id):
        url = "http://crossbrowsertesting.com/reports/reserve.php?user_id={}&config_id={}&si={}".format(user_id, self.config_id, self.si)
        # print("reserving: " + url)
        requests.get(url, auth=HTTPBasicAuth('stupid', 'dumb'))

    def __str__(self):
        return str(self.si)+', '+str(self.config_id)+', '+self.os_api_name

    def __repr__(self):
        return str(self)

def pollSIAvailable(si):
    available = False
	#make time out
    # poll the image until it is available
    x = 0
    while not available and x < 3600:
        # print('Image not available to reserve. Sleeeeeeep')
        x += 5
        available = si.is_available()
        sleep(5)

    # return true once it is available
    # print('Image available; reserving!')
    return True

def pollTE(teId, user, pw):
    finished = False
    #makes assumption test will cease to be active at some point -- possibly put on timer
    # poll the test until it is completed
    while not finished:
        # print('Test not finished. Sleeeeeeeeeep')
        r = requests.get('http://crossbrowsertesting.com/api/v3/testexecute/'+str(teId),auth=HTTPBasicAuth(user, pw))\
        # # print(r.json())
        # print(r.json()['active'])

        # check that the test is active in the api
        if(not (r.json()['active'])):
            finished = True
        else:
            sleep(15)
    # print('Test finished!')
    return True


def checkBrowserTestedSuccessfullyOnSI(vnc_session_id):
	inRedis = False
 	key = 'checkSI:' + str(vnc_session_id)
 	x = 0
 	val = None
 	while x < 60 and not inRedis:
		sleep(1)
		x += 1
		url = "http://crossbrowsertesting.com/code/checkRedis.php?vnc_id=" + str(vnc_session_id)
		r = requests.get(url)
		if 'true' in r.text:
			inRedis = True
		# print('inRedis is ' + str(inRedis))
		# val = red.get(key)
		# # print(val)
		# # print('Got ' + str(val) + ' from redis for vnc session id ' + str(vnc_session_id))
		# if val == 'true':
 	# 		inRedis = True

	return inRedis

os_api_name_dict = {
    'Win7-C1': 19   ,
    'Win7x64-C1': 43,
    'Win8': 45      ,
    'Win8.1': 58    ,
    'Win10': 87
}

# def load_te_file():
# 	# open the test file
# 	# we only want to do this once
# 	# print('loading up test zip')
# 	tcproj = {'file':open(zip,'rb')}

# 	# post a request to our api containing the test object
# 	# we only want to do this once
# 	r = requests.post('http://crossbrowsertesting.com/api/v3/testexecute/projectsuite/',files=tcproj, data={'relative_path':'teproject\\test.pjs'},auth=HTTPBasicAuth(user,pw))

# 	fileHash = (r.json())['file_hash']
# 	# print('Posted file and got file hash! Running test...')
# 	return fileHash

def run_test(user_id, user, pw, si, os_api_name, browser_api_name, fileHash, i):
	if i == 2:
		pass
	curr_test_si = SI(si, os_api_name_dict[os_api_name], os_api_name)

	# check that the image is available before suspending it.
	available = pollSIAvailable(curr_test_si)
	if not available:
		# print(si + ' did not become available within one hour.')
		pass
	# print('polling SI ' + str(si))

	# image available, reserve it -- assumes we're quick enough to reserve it after confirming is available
	curr_test_si.reserve(user_id)
	sleep(10)
	# print('si reserved!!!')

	payload = {'file_hash':fileHash,'project_name':'TestProject1','test_name':'Script|Unit1|Test1','browser': os_api_name + '|' + browser_api_name, 'record_video': 'true'}
	# here, we actually start the test
	r = requests.post('http://crossbrowsertesting.com/api/v3/testexecute/',data=payload,auth=HTTPBasicAuth(user, pw))
	# print('Test is running! Polling...')

	# get the testId so we can poll until finished
	teId = (r.json())['test_execute_id']
	# print('Got test execute id:' + str(teId))

	test_is_finished = pollTE(teId, user, pw)
	#if times out after five minutes, it's considered failed
	if not test_is_finished:
		# print('test on ' + str(si) + ' did not finish within 5 minute time frame - considered failure')
		pass
	test_result = checkBrowserTestedSuccessfullyOnSI(teId)
	print(teId)
	# print("Test_Result: " + str(test_result))
	if not test_result:
		if i == 1:
			# print('got i = 1.. returning ' + str(test_result))
			return test_result
		# print('Test on SI:' + str(si) + ' did not pass on the ' + str(i+1) + ' try')
		sleep(120)
		run_test(user_id, user, pw, si, os_api_name, browser_api_name, fileHash, i+1)
	else:
		# print('this test was good!')
		# print('got test_result = ' + str(test_result) + '.. returning')
		return test_result

# run_test(user_id, user, pw, si, os_api_name, browser_api_name, fileHash, 0)

