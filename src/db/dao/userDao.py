from db.dao.alchemy import Alchemy


class UserDao(Alchemy):

    def __init__(self):
        super(UserDao, self).__init__()
        self.table = self.base.classes.users

    # def getUser(self, login):
    #     return self.session.query(self.Users).filter_by(login=login)


if __name__ == '__main__':
    d = UserDao()
    # res = d.get(login='pepa')
    res = d.getOne(login='pepa', enabled=None)
    print(res)
    if res:
        print(res.__dict__)
