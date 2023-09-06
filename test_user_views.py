"""User view tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_user_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY
from seed import seed

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

with app.app_context():

    db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False
app.config['TESTING'] = True


class UserViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        seed()
        self.client = app.test_client()
    def tearDown(self):
        with self.client as c:
                with c.session_transaction() as sess:
                    sess[CURR_USER_KEY] = None
    def login_user(self):
        with app.app_context():
            self.testuser = User.signup(username="testuser",
                                        email="test@test.com",
                                        password="testuser",
                                        image_url=None)

            db.session.commit()
            with self.client as c:
                with c.session_transaction() as sess:
                    sess[CURR_USER_KEY] = self.testuser.id

    def test_followers_on_profile(self):
        """Can users see the followers and following of other users?"""

        
        with app.app_context():
            self.login_user()
            with self.client as c:
                
                resp = c.get("/users/5/following")

                html = resp.get_data(as_text=True)

                self.assertEqual(resp.status_code, 200)
                self.assertIn('<a href="/users/52" class="card-link">', html)

                resp = c.get("/users/5/followers")

                html = resp.get_data(as_text=True)

                self.assertEqual(resp.status_code, 200)
                self.assertIn('<a href="/users/23" class="card-link">', html)

    def test_followers_on_profile_no_login(self):
        """Can users NOT see the followers and following of other users when logged out?"""

        
        with app.app_context():
            with self.client as c:
                
                resp = c.get("/users/5/following")

                self.assertEqual(resp.status_code, 302)

                resp = c.get("/users/5/followers")

                self.assertEqual(resp.status_code, 302)

    def test_add_message_logged_out(self):
        """Can users add a message when logged out?"""
        
        with app.app_context():
            with self.client as c:
                
                resp = c.post("/messages/new", data={"text": "Hello"})

                self.assertEqual(resp.status_code, 302)

                resp = c.get("/")
                html = resp.get_data(as_text=True)
                self.assertIn("Access unauthorized", html)

    def test_delete_message_logged_out(self):
        """Can users delete a message when logged out?"""
        
        with app.app_context():
            with self.client as c:
                
                resp = c.post("/messages/959/delete")

                self.assertEqual(resp.status_code, 302)

                resp = c.get("/messages/959")
                html = resp.get_data(as_text=True)

                self.assertIn("Knowledge official attack media thing later.", html)

    def test_delete_other_users_message_logged_in(self):
        """Can users delete a message made by a different user when logged in?"""
        
        with app.app_context():
            self.login_user()
            with self.client as c:
                
                resp = c.post("/messages/959/delete")

                self.assertEqual(resp.status_code, 302)

                resp = c.get("/messages/959")
                html = resp.get_data(as_text=True)

                self.assertIn("Knowledge official attack media thing later.", html)


    
