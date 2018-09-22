import unittest
from app import app, db
from app.users import User

class UserModelClass(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print('setUp Class')
        app.config['SQLALCHEMY_DATABASE_URI'] \
        = 'mysql+pymysql://Samuel:tirab33@localhost/assis_testing'
        app.config['SQLALCHEMY_ECHO'] = False
        db.create_all()

    @classmethod
    def tearDownClass(cls):
        print('tearDown Class')
        db.session.remove()
        db.drop_all()

    def setUp(self):
        print('SetUp')
        self.u = User(email='samuel@algorit.ma', leadership=True)
        self.u.set_password('samuel@algorit.ma')
        self.l = User(email='tiara@algorit.ma', leadership=True)
        self.l.set_password('tiara@algorit.ma')
        self.r = User(email='ardhito@algorit.ma')
        self.r.set_password('ardhito@algorit.ma')
        db.session.add(self.u)
        db.session.add(self.l)
        db.session.add(self.r)
        db.session.commit()

    def tearDown(self):
        print('tearDown')
        db.session.query(User).delete()
        db.session.commit()

    def test_user_creation(self):
        returned_u = User.query.filter_by(email='samuel@algorit.ma').one()
        returned_u2 = User.query.filter_by(email='ardhito@algorit.ma').one()
        self.assertEqual(returned_u.email, 'samuel@algorit.ma')
        self.assertFalse(returned_u2.leadership)

    def test_password_hashing(self):
        self.assertFalse(self.u.check_password('Samuel@algorit.ma'))
        self.assertTrue(self.u.check_password('samuel@algorit.ma'))

# to test, in console: python tests.py
if __name__ == '__main__':
    unittest.main(verbosity=2)
