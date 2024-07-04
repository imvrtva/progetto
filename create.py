#creare classi dinamiche e non

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), nullable=False)

    def is_active(self):
        return True

    def get_id(self):
        return str(self.id)

    def is_authenticated(self):
        return True