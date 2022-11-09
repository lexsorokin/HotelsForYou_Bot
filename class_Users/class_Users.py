
class Users:
    all_users = dict()

    def __init__(self, user_id):
        self.name = None
        self.dest_name = None
        self.dest_id = None
        self.sort_order = None
        self.check_in = None
        self.check_out = None
        self.hotel_amount = None
        self.max_price = None
        self.min_price = None
        self.max_distance = None
        self.hotel_step = None
        self.photo_step = None
        self.final_data = None
        self.input_history = None
        self.messages_to_delete = []
        Users.add_user(user_id, self)

    @staticmethod
    def get_user(user_id):
        if Users.all_users.get(user_id) is None:
            new_user = Users(user_id)
            return new_user
        return Users.all_users.get(user_id)

    @classmethod
    def add_user(cls, user_id, user):
        cls.all_users[user_id] = user
