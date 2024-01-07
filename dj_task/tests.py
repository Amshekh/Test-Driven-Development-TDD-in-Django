from django.test import TestCase
from .models import Task
from .forms import NewTaskForm, UpdateTaskForm

class TaskModelTest(TestCase):
    def test_task_model_exists(self):
        tasks = Task.objects.count()

        self.assertEqual(tasks, 0)

    def test_model_has_string_representation(self):
        task = Task.objects.create(title='First task')

        self.assertEqual(str(task), task.title)

class IndexWebPageTest(TestCase):
    def setUp(self):
        self.task = Task.objects.create(title='First task')

    def test_index_webpage_returns_correct_response(self):
        response = self.client.get('/')

        self.assertTemplateUsed(response, 'dj_task/index.html')
        self.assertEqual(response.status_code, 200)

    def test_index_webpage_has_task(self):
        response = self.client.get('/')

        self.assertContains(response, self.task.title)

class DetailWebPageTest(TestCase):
    def setUp(self):
        self.task = Task.objects.create(title='First task', description='The description')
        self.task2 = Task.objects.create(title='Second task', description='The description')

    def test_detail_webpage_returns_correct_response(self):
        response = self.client.get(f'/{self.task.id}/')    # f will ensure that you are formatting a string

        self.assertTemplateUsed(response, 'dj_task/detail.html')
        self.assertEqual(response.status_code, 200)

    def test_detail_webpage_has_correct_content(self):
        response = self.client.get(f'/{self.task.id}/')    # f will ensure that you are formatting a string

        self.assertContains(response, self.task.title)
        self.assertContains(response, self.task.description)
        self.assertNotContains(response, self.task2.title)

class NewWebPageTest(TestCase):
    def setUp(self):
        self.form = NewTaskForm

    def test_new_webpage_returns_correct_response(self):
        response = self.client.get('/new/')

        self.assertTemplateUsed(response, 'dj_task/new.html')
        self.assertEqual(response.status_code, 200)

    def test_form_can_be_valid(self):
        self.assertTrue(issubclass(self.form, NewTaskForm))
        self.assertTrue('title' in self.form.Meta.fields)
        self.assertTrue('description' in self.form.Meta.fields)


        form = self.form({            # Note: form is just a name of variable here and you can use any other name
            'title': 'The Title',
            'description': 'The Description'
        }) 

        self.assertTrue(form.is_valid())  # if the test run successfully it means that form can be submitted

        
    def test_new_webpage_from_rendering(self):
        response = self.client.get('/new/')

        self.assertContains(response, '<form')  # It will test if "new.html" contains form
        self.assertContains(response, 'csrfmiddlewaretoken')  # It will test if "new.html" contains csrf
        self.assertContains(response, '<label for')  # It will test if "new.html" contains label


        # Test invalid form

        response = self.client.post('/new/', {           
            'title': '',           # Title is a required field for valid form. If it's absent, it means form is invalid.
            'description': 'The Description'
        })

        self.assertContains(response, '<ul class="errorlist">')
        self.assertContains(response, 'This field is required.')

        # Test valid form

        response = self.client.post('/new/', {           
            'title': 'The Title',           
            'description': 'The Description'
        })

        self.assertRedirects(response, expected_url='/')
        self.assertEqual(Task.objects.count(), 1) # you have to make sure that the task is valid and saved in database.

class UpdateWebpageTest(TestCase):
    def setUp(self):
        self.form = UpdateTaskForm
        self.task = Task.objects.create(title='First task')

    def test_update_webpage_returns_correct_response(self):
        response = self.client.get(f'/{self.task.id}/update/')

        self.assertTemplateUsed(response, 'dj_task/update.html')
        self.assertEqual(response.status_code, 200)

    def test_form_can_be_valid(self):
        self.assertTrue(issubclass(self.form, UpdateTaskForm))
        self.assertTrue('title' in self.form.Meta.fields)
        self.assertTrue('description' in self.form.Meta.fields)


        form = self.form({            # Note: form is just a name of variable here and you can use any other name
            'title': 'The Title',
            'description': 'The Description'
        }, instance=self.task)   # this update we need to pass in self.task into the form, so you need to set instance here
                                 # you are passing instance just to nsure it's updating.
        self.assertTrue(form.is_valid())

        form.save()

        self.assertEqual(self.task.title, 'The Title')  # Testing if the database has been updated

    def test_form_can_be_invalid(self):

        form = self.form({            # Note: form is just a name of variable here and you can use any other name
            'title': '',  # If title is empty the form is supposed to be invalid
            'description': 'The Description'
        }, instance=self.task)

        self.assertFalse(form.is_valid())


    def test_update_webpage_from_rendering(self):
        response = self.client.get(f'/{self.task.id}/update/')

        self.assertContains(response, '<form')  # It will test if "update.html" contains form
        self.assertContains(response, 'csrfmiddlewaretoken')  # It will test if "update.html" contains csrf
        self.assertContains(response, '<label for')  # It will test if "update.html" contains label


        # Test invalid form

        response = self.client.post(f'/{self.task.id}/update/', {       
            'id': self.task.id,
            'title': '',           # Title is a required field for valid form. If it's absent, it means form is invalid.
            'description': 'The Description'
        }, instance=self.task)  # set the instance here

        self.assertContains(response, '<ul class="errorlist">')
        self.assertContains(response, 'This field is required.')

        # Test valid form

        response = self.client.post(f'/{self.task.id}/update/', {           
            'title': 'The Title',           
            'description': 'The Description'
        })

        self.assertRedirects(response, expected_url='/')
        self.assertEqual(Task.objects.count(), 1) # you have to make sure that the task is valid and saved in database.    
        self.assertEqual(Task.objects.first().title, 'The Title')  # Testing if the database has been updated and 'The Title' is being used not some other like 'First task'


class DeleteWebPageTest(TestCase):
    def setUp(self):
        self.task = Task.objects.create(title='First task')

    def test_delete_webpage_deletes_task(self):
        self.assertEqual(Task.objects.count(), 1)

        response = self.client.get(f'/{self.task.id}/delete/')  # writing code to delete this delete task and 
        
        self.assertRedirects(response, expected_url='/')  # redirect to the front webpage

        self.assertEqual(Task.objects.count(), 0)  # after delete task, there should be 0 task in database