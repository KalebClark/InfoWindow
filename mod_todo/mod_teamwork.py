import urllib2, base64
import json
import logging


class ToDo:
    def __init__(self, opts):
        logging.debug("Todo API: TEAMWORK")
        self.company = opts['site']
        self.key = opts['api_key']
    
    def list(self):
        action = "tasks.json?sort=priority"
        request = urllib2.Request("https://{0}/{1}".format(self.company, action))
        request.add_header("Authorization", "BASIC " + base64.b64encode(self.key + ":xxx"))

        response = urllib2.urlopen(request)
        data = json.loads(response.read())
        items = []

        for task in data['todo-items']:
            if task['priority'] == 'high':
                priority = 1
            elif task['priority'] == 'medium':
                priority = 2
            elif task['priority'] == 'low':
                priority = 3
            elif task['priority'] == 'None':
                priority = 4
            else:
                priority = 8

            items.append({
                "content": task['content'],
                "priority": priority
            })   

        return items
