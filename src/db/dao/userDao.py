from db.dao.alchemy import Alchemy


class UserDao(Alchemy):

    def __init__(self):
        super(UserDao, self).__init__()
        self.table = self.base.classes.users

    # def getUser(self, login):
    #     return self.session.query(self.Users).filter_by(login=login)


if __name__ == '__main__':
    ud = UserDao()
    # res = d.get(login='pepa')
    user = ud.getOne(login='pepa', enabled=None)
    print(user)
    if user:
        print(user.__dict__)
        print("orgid:", user.organisation_id)

        # user.organisation_id += 1
        # d.session.commit()  # needs to be done manually here or..
        ud.save()
