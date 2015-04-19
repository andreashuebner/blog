import os
import sys
import unittest
import multiprocessing
import time
from urlparse import urlparse

from werkzeug.security import generate_password_hash
from splinter import Browser
sys.path.append('..')
sys.path.append('.')

# Configure your app to use the testing database
os.environ["CONFIG_PATH"] = "blog.config.TestingConfig"

from blog import app
from blog import models
from blog.database import Base, engine, session

class TestViews(unittest.TestCase):
    def setUp(self):
        """ Test setup """
        self.browser = Browser("phantomjs")

        # Set up the tables in the database
        Base.metadata.create_all(engine)

        # Create an example user
        self.user = models.User(name="Alice", email="alice@example.com",
                                password=generate_password_hash("test"))
        session.add(self.user)
        session.commit()

        self.process = multiprocessing.Process(target=app.run)
        self.process.start()
        time.sleep(2)


    def tearDown(self):
        """ Test teardown """
        # Remove the tables and their data from the database
        self.process.terminate()
        session.close()
        engine.dispose()
        Base.metadata.drop_all(engine)
        self.browser.quit()
        
    def testLoginCorrect(self):
        self.browser.visit("http://127.0.0.1:5000/login")
        self.browser.fill("email", "alice@example.com")
        self.browser.fill("password", "test")
        button = self.browser.find_by_css("button[type=submit]")
        button.click()
        self.assertEqual(self.browser.url, "http://127.0.0.1:5000/")

    def testLoginIncorrect(self):
        self.browser.visit("http://127.0.0.1:5000/login")
        self.browser.fill("email", "bob@example.com")
        self.browser.fill("password", "test")
        button = self.browser.find_by_css("button[type=submit]")
        button.click()
        self.assertEqual(self.browser.url, "http://127.0.0.1:5000/login")
   
    def testCreatedPostIsPresentInOverview(self):
        self.browser.visit("http://127.0.0.1:5000/login")
        self.browser.fill("email", "alice@example.com")
        self.browser.fill("password", "test")
        button = self.browser.find_by_css("button[type=submit]")
        button.click() 
        time.sleep(2)
        self.browser.visit("http://127.0.0.1:5000/post/add")
        self.browser.fill("title", "Test post Alice")
        self.browser.fill("content","This is only a test post")
        button = self.browser.find_by_css("button[type=submit]")
        button.click()
        time.sleep(2)
        self.browser.visit("http://127.0.0.1:5000")
        self.assertTrue(self.browser.is_text_present("Test post Alice"))
        self.assertTrue(self.browser.is_text_present("This is only a test post"))
        
    def testCreatedPostCanBeDeleted(self):
        self.browser.visit("http://127.0.0.1:5000/login")
        self.browser.fill("email", "alice@example.com")
        self.browser.fill("password", "test")
        button = self.browser.find_by_css("button[type=submit]")
        button.click() 
        time.sleep(2)
        self.browser.visit("http://127.0.0.1:5000/post/add")
        self.browser.fill("title", "Test post Alice")
        self.browser.fill("content","This is only a test post")
        button = self.browser.find_by_css("button[type=submit]")
        button.click()
        time.sleep(2)
        deletebuttons = self.browser.find_by_name("deletebutton")
        firstDeleteButton = deletebuttons.first
        firstDeleteButton.click()
        time.sleep(2)
        deletebuttons = self.browser.find_by_name("deletebutton")
        firstDeleteButton = deletebuttons.first
        firstDeleteButton.click()
        time.sleep(2)
        self.browser.visit("http://127.0.0.1:5000")
        self.assertFalse(self.browser.is_text_present("Test post Alice"))
        

if __name__ == "__main__":
    unittest.main()