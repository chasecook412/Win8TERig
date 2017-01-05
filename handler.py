import subprocess
import tetest
import csv
import requests
import sys
os_api_name_dict = {
    19: 'Win7-C1'   ,
    43: 'Win7x64-C1',
    45: 'Win8'      ,
    58: 'Win8.1'    ,
    87: 'Win10'     
}
# si = '1272'
# browser = 'Chrome50'

def get_configuration_api_names(os_api_name):
    """
    """
    windows_api_names = ['Win10', 'Win8.1', 'Win8', 'Win7-C1', 'Win7x64-C1']
    url = "https://crossbrowsertesting.com/api/v3/testexecute/browsers"
    resp = requests.get(url).json()
    configuration_list = []
    for os in resp:
        #if os['api_name'] in windows_api_names:
        if os['api_name'] == os_api_name:
            configuration_list.extend( [(os_api_name, browser['api_name']) for browser in os['browsers'] ])

    #duplicates in list... dedup
    configuration_list = list(dedupe(configuration_list))
    return configuration_list

def dedupe(items):
    seen = set()
    for item in items:
        if item not in seen:
            yield item
            seen.add(item)

def get_server_images_from_csv():
    """
    outputs:
    [{'conf_api_name': 'win7-c1', 'si': 42, 'conf_id': 19} ... ]

    """
    global os_api_name_dict
    # config_id = os_api_name_dict[os_api_name]
    with open('./sis.csv', 'r') as f:
        reader = csv.reader(f)
        blist = list(reader)
    # print(blist)
    # return [{'si':(int(pair[0])), 'conf_id': int(pair[1]), 'conf_api_name': os_api_name_dict[int(pair[1])]}  for pair in blist ]
    return blist# [(int(pair[0])), int(pair[1]), os_api_name_dict[int(pair[1])]  for pair in blist ]


def check_si_not_tested(si, browser):
    with open('log') as f:
        for line in f:
            if si in line and browser in line and 'passed' in line:
                return True
    return False


si_list = get_server_images_from_csv()

browsers = get_configuration_api_names('Win8')

# print(len(si_list))
for i in range(len(si_list)):
    # print(si_list[i][0])
    for j in range(len(browsers)):
        try:
            
            tested = check_si_not_tested(si_list[i][0], browsers[j][1])

            if not tested:
                passed = tetest.run_test('220680', 'chase@crossbrowsertesting.com', 'u81305495037f796', si_list[i][0],'Win8', browsers[j][1], '540aaff6e6dea3e442968d24cce4a819', 0)
                # print(passed)
                if passed:
                    print('RESULTS: ' + str(browsers[j][1]) + ' passed on SI: ' + str(si_list[i][0]))
                else:
                    print('RESULTS: ' + str(browsers[j][1]) + ' failed on SI: ' + str(si_list[i][0]) + '.')
                sys.stdout.flush()
        except Exception as ex:
            print('RESULTS: ' + str(browsers[j][1]) + ' failed on SI: ' + str(si_list[i][0]) + ' with exception: ' + str(ex))
            sys.stdout.flush()

# subprocess.Popen('python tetest.py 220680 chase@crossbrowsertesting.com u81305495037f796' + si + ' Win10 ' + browser + ' 540aaff6e6dea3e442968d24cce4a819')
# print('python tetest.py 220680 chase@crossbrowsertesting.com u81305495037f796' + si + ' Win10 ' + browser + ' 540aaff6e6dea3e442968d24cce4a819')
