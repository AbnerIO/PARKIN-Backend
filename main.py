from flask import Flask, request, jsonify, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user

app = Flask(__name__)
API_KEY = "Admin92%&#"

app.config['SECRET_KEY'] = 'DispMoviles'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///DataBase.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
# Login setup
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# CREATE TABLE IN DB
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    name = db.Column(db.String(100), unique=True)
    type = db.Column(db.String(10), nullable=False)  # Client/Admin/Owner
    password = db.Column(db.String(100), nullable=False)
    is_verified = db.Column(db.Boolean, nullable=False, default=False)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


class Spot(db.Model):
    __tablename__ = 'spots'
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    street = db.Column(db.String(100), nullable=False)
    street_number = db.Column(db.Integer, nullable=False)
    neighborhood = db.Column(db.String(100), nullable=False)
    car_spaces = db.Column(db.Integer, nullable=False)
    bicycle_spaces = db.Column(db.Integer, nullable=False)
    car_spaces_availables = db.Column(db.Integer, nullable=False)
    bicycle_spaces_availables = db.Column(db.Integer, nullable=False)
    bicycle_space_rent = db.Column(db.Float, nullable=False)
    car_space_rent = db.Column(db.Float, nullable=False)
    map_url = db.Column(db.String(100))

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


# with app.app_context():
#    db.create_all()
# Routes Funciones
@app.route("/solicitar_spot/<int:spot_id>")
def solicitar_spot(spot_id):
    if API_KEY == request.args.get("api_key"):
        vehicle_type = request.args.get("vehicle_type")
        if vehicle_type == "car":
            spot = db.session.query(Spot).filter_by(id=spot_id).first()
            spaces = int(request.args.get("spaces"))
            if spot:
                if spot.car_spaces_availables >= spaces:
                    spot.car_spaces_availables = spot.car_spaces_availables - spaces
                    db.session.commit()
                    return jsonify(response={"response": "Spots solicitados correctamnete"}), 200
                else:
                    return jsonify(error={"error": "No hay suficientes espacios"}), 400
        elif vehicle_type == "bicycle":
            spot = db.session.query(Spot).filter_by(id=spot_id).first()
            spaces = int(request.args.get("spaces"))
            if spot:
                if spot.bicycle_spaces_availables >= spaces:
                    spot.bicycle_spaces_availables = spot.bicycle_spaces_availables - spaces
                    db.session.commit()
                    return jsonify(response={"response": "Spots solicitados correctamnete"}), 200
                else:
                    return jsonify(error={"error": "No hay suficientes espacios"}), 400
        else:
            return jsonify(error={"error": "Ese vehiculo no existe. (car/bicycle)"}), 400
    else:
        return jsonify(error={"error": "No hay un spot con esa id"}), 400


@app.route("/devolver_spot/<int:spot_id>")
def devolver_spot(spot_id):
    if API_KEY == request.args.get("api_key"):
        spot = db.session.query(Spot).filter_by(id=spot_id).first()
        spaces = int(request.args.get("spaces"))
        vehicle_type = request.args.get("vehicle_type")
        if spot:
            if vehicle_type == "car":
                if spot.car_spaces >= (spot.car_spaces_availables + spaces):
                    spot.car_spaces_availables = spot.car_spaces_availables + spaces
                    db.session.commit()
                    return jsonify(response={"response": "Spots devueltos correctamente"}), 200
                else:
                    return jsonify(error={"error": "Ese spot no puede tener más espacios que devolver, estaría "
                                                   "sobrepasando su límite.)"}), 400
            elif vehicle_type == "bicycle":
                if spot.bicycle_spaces >= (spot.bicycle_spaces_availables + spaces):
                    spot.bicycle_spaces_availables = spot.bicycle_spaces_availables + spaces
                    db.session.commit()
                    return jsonify(response={"response": "Spots devueltos correctamente bicicletas"}), 200
                else:
                    return jsonify(error={
                        "error": "Ese spot no puede tener más espacios que devolver, estaría sobrepasando su límite. "
                                 "bicicletas)"}), 400
        else:
            return jsonify(error={"error": "No hay un spot con esa id"}), 400
    # Routes spots general


@app.route("/spots/get", methods=["GET"])
def get_spots():
    if API_KEY == request.args.get("api_key"):
        spots = db.session.query(Spot).all()
        spots = [spot.to_dict() for spot in spots]
        return jsonify(spots=spots), 200
    else:
        return jsonify(error={"error": "API KEY inválida"}), 200


@app.route("/spots/get/<int:spot_id>", methods=["GET"])
def get_spot(spot_id):
    if API_KEY == request.args.get("api_key"):
        spot = db.session.query(Spot).filter_by(id=spot_id).first()
        if spot:
            return jsonify(spot=spot.to_dict()), 200
        else:
            return jsonify(error={"error": "No hay un spot con esa id"}), 400
    else:
        return jsonify(error={"error": "API KEY inválida"}), 401


@app.route("/spots/add", methods=["POST"])
def add_spot():
    if API_KEY == request.args.get("api_key"):
        if request.method == "POST":
            new_spot = Spot(
                owner_id=request.args.get("owner_id"),
                city=request.args.get("city"),
                state=request.args.get("state"),
                country=request.args.get("country"),
                street=request.args.get("street"),
                street_number=request.args.get("street_number"),
                neighborhood=request.args.get("neighborhood"),
                car_spaces=request.args.get("car_spaces"),
                bicycle_spaces=request.args.get("bicycle_spaces"),
                map_url=request.args.get("map_url"),
                car_spaces_availables=request.args.get("car_spaces"),
                bicycle_spaces_availables=request.args.get("bicycle_spaces"),
                bicycle_space_rent=request.args.get("bicycle_space_rent"),  # USD
                car_space_rent=request.args.get("car_space_rent")  # USD
            )
            db.session.add(new_spot)
            db.session.commit()
            return jsonify(response={"success": "Spot añadido"}), 200
    else:
        return jsonify(error={"error": "API KEY inválida"}), 401


# Routes users general
@app.route("/users/get/<int:user_id>")
def get_user(user_id):
    if API_KEY == request.args.get("api_key"):
        user = db.session.query(User).filter_by(id=user_id).first()
        if user:
            user = user.to_dict()
            return jsonify(user=user), 200
        else:
            return jsonify(error={"error": "No hay usuario con ese id"}), 401
    else:
        return jsonify(error={"error": "API KEY inválida"}), 401


@app.route("/users/add", methods=["POST"])
def add_user():
    if API_KEY == request.args.get("api_key"):
        if request.method == "POST":
            if db.session.query(User).filter_by(name=request.args.get("name")).all():
                return jsonify(error={"Error": "Nombre ya usado"}), 400
            if db.session.query(User).filter_by(email=request.args.get("email")).all():
                return jsonify(error={"Error": "Email ya usado"}), 400
            hash_and_salted_password = generate_password_hash(
                request.args.get("password"),
                method='pbkdf2:sha256',
                salt_length=8
            )
            new_user = User(
                name=request.args.get("name"),
                email=request.args.get("email"),
                type=request.args.get("type"),
                password=hash_and_salted_password,
            )
            db.session.add(new_user)
            db.session.commit()
            return jsonify(response={"success": "Usuario añadido"}), 200
    else:
        return jsonify(error={"error": "API KEY inválida"}), 401


@app.route("/users/delete", methods=["DELETE"])
def delete_user():
    if API_KEY == request.args.get("api_key"):
        if request.method == "DELETE":
            user_id = request.args.get("id")
            db.session.query(User).delete(user_id)
            db.session.commit()
            return jsonify(response={"success": "Usuario eliminado."}), 200
        else:
            return jsonify(error={"error": "Error en la petición."}), 200
    else:
        return jsonify(error={"error": "API KEY inválida"}), 401


@app.route("/users/get")
def get_users():
    if API_KEY == request.args.get("api_key"):
        users = db.session.query(User).all()
        users = [user.to_dict() for user in users]
        for user in users:
            del user['password']
        return jsonify(users=users), 200
    else:
        return jsonify(error={"error": "API KEY inválida"}), 401


# Auth routes
@app.route("/login", methods=["POST"])
def login():
    if request.method == "POST":
        email = request.args.get('email')
        password = request.args.get('password')
        # Find user by email entered.
        user = User.query.filter_by(email=email).first()

        # Check stored password hash against entered password hashed.
        if not user:
            return jsonify(error={"error": "email no valido"}), 400
            # Password incorrect
        elif not check_password_hash(user.password, password):
            return jsonify(error={"error": "Contraseña incorrecta"}), 400
            # Email exists and password correct
        else:
            login_user(user)
            return jsonify(response={"success": "Logeado correctamente",
                                     "rol_de_usuario": user.type}), 200


@app.route("/logout")
@login_required  # Se requiere que el usuario este dentro del sistema para sacarlo
def logout():
    logout_user()
    return jsonify(response={"success": "Desloggeado correctamente"}), 200


if __name__ == '__main__':
    app.run(debug=True)
