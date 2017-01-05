import requests

user = 'chase@crossbrowsertesting.com'
pw ='u81305495037f796'

r = requests.get('http://crossbrowsertesting.com/api/v3/testexecute/', auth = (user, pw))

dic = r.json()
print(dic['testexecute'][0]['test_execute_id'])

