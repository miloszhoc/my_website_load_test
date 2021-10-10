import logging
from locust import HttpUser, task, TaskSet, SequentialTaskSet
from locust.user.wait_time import between

import re
import random
import os


class Login(SequentialTaskSet):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.csrf = ''

    @task
    def get_login_page(self):
        with self.client.get('/panel/login/', catch_response=True, name='Login Page') as response:
            if response.status_code == 200:
                match = re.findall('name="csrfmiddlewaretoken".*">', response.text)
                match = re.findall('value=.*"', match[0])
                self.csrf = match[0].strip('value="').strip('"')
            else:
                response.failure('can not reach login page')
                logging.critical(response.text)

    @task
    def login(self):
        with self.client.post('/panel/login/?next=/panel/',
                              data={'csrfmiddlewaretoken': self.csrf,
                                    'username': os.environ.get('username'),
                                    'password': os.environ.get('password')},
                              catch_response=True, name='Log in') as response:

            if 'Welcome!' in response.text:
                response.success()
            else:
                response.failure('user is not logged in')
                logging.critical(response.text)

    @task
    def get_projects_page(self):
        with self.client.get('/panel/projects/', catch_response=True, name='Projects page') as response:
            if 'healthcheck' in response.text:
                response.success()
            else:
                response.failure('can not reach project list page')
                logging.critical(response.text)

    @task
    def get_about_me_page(self):
        with self.client.get('/panel/about-me/1/', catch_response=True, name='AboutMe page') as response:
            if 'Save' in response.text:
                response.success()
            else:
                response.failure('can not reach About Me page')
                logging.critical(response.text)


class BrowseMainPage(TaskSet):

    @task
    def get_index(self):
        with self.client.get('/', catch_response=True, name='index page') as resp:
            if 'My name is Miłosz.' in resp.text:
                resp.success()
            else:
                resp.failure('can not reach index page')

    @task
    def get_project_info(self):
        project_id = random.randint(1, 9)
        with self.client.get('/project-details/{}'.format(project_id),
                             catch_response=True,
                             name='Project Details') as response:
            if 'last_commit' in response.text:
                response.success()
            else:
                response.failure('can not reach project {} details'.format(project_id))


class LoggedUser(HttpUser):
    wait_time = between(2, 5)

    tasks = [Login, BrowseMainPage]
