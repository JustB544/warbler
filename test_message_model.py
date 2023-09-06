"""Message model tests."""

# run these tests like:
#
#    python -m unittest test_message_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

with app.app_context():
    
    db.create_all()


class MessageModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        with app.app_context():
            User.query.delete()
            Message.query.delete()
            Follows.query.delete()

            self.client = app.test_client()
            user = User(
                email="test@test.com",
                username="testuser",
                password="HASHED_PASSWORD"
            )
            db.session.add(user)
            db.session.commit()
            self.user_id = user.id
            with self.client as c:
                with c.session_transaction() as sess:
                    sess[CURR_USER_KEY] = user.id

    def test_message_model(self):
        """Does basic model work?"""
        with app.app_context():

            m = Message(text="test", user_id=self.user_id)
            db.session.add(m)
            db.session.commit()

            user = User.query.get(self.user_id)
            self.assertEqual(len(user.messages), 1)

    def test_delete_message(self):
        """Can you delete a message?"""
        with app.app_context():

            m = Message(text="test", user_id=self.user_id)
            db.session.add(m)
            db.session.commit()

            resp = self.client.post(f"messages/{m.id}/delete")
            
            self.assertEqual(resp.status_code, 302)

            user = User.query.get(self.user_id)
            self.assertEqual(len(user.messages), 0)