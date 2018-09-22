import unittest
from app import app, db
from app.users import User

class UserModelClass(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] \
        = 'mysql+pymysql://Samuel:tirab33@localhost/assis_testing'
        app.config['SQLALCHEMY_ECHO'] = False
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_add_user(self):
        u = User(email='samuel@algorit.ma',
                 leadership=True)
        u.set_password('samuel@algorit.ma')
        db.session.add(u)
        db.session.commit()
        returned_u = User.query.filter_by(email='samuel@algorit.ma').first()
        self.assertEqual(returned_u.email, 'samuel@algorit.ma')

    def test_password_hashing(self):
        u = User(email='samuel@algorit.ma',
                 leadership=True)
        u.set_password('samuel@algorit.ma')
        self.assertFalse(u.check_password('samuel123'))
        self.assertTrue(u.check_password('samuel@algorit.ma'))

# to test, in Python console: python tests.py
if __name__ == '__main__':
    unittest.main(verbosity=2)
