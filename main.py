from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from functools import wraps
import pymysql

app = Flask(__name__)

db_config = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': '1234',
    'db': 'dochi',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

app.config['JWT_SECRET_KEY'] = 'super-secret'
jwt = JWTManager(app)

def connect_db():
    return pymysql.connect(**db_config)

@app.route('/register', methods=['POST'])
def register():
    conn = None
    try:
        data = request.json
        user_id = data['user_id']
        username = data['username']
        password = data['password']
        name = data['name']
        military_id = data['military_id']
        unit = data['unit']
        m_rank = data['m_rank']
        phone = data['phone']
        profile_img = data['profile_img']

        conn = connect_db()
        with conn.cursor() as cursor:
            sql = "INSERT INTO User (user_id, username, password, name, military_id, unit, m_rank, phone, profile_img) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(sql, (user_id, username, password, name, military_id, unit, m_rank, phone, profile_img))
        conn.commit()
        
        return jsonify({"message": "User registered successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        username = data['username']
        password = data['password']
        
        conn = connect_db()
        with conn.cursor() as cursor:
            sql = "SELECT * FROM User WHERE username = %s AND password = %s"
            cursor.execute(sql, (username, password))
            user = cursor.fetchone()
            if user:
                access_token = create_access_token(identity=user['user_id'])
                return jsonify(access_token=access_token), 200
            else:
                return jsonify({"error": "Invalid credentials"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        try:
            data = jwt.decode(token.split()[1], app.config['JWT_SECRET_KEY'])
        except:
            return jsonify({'error': 'Token is invalid'}), 401
        return f(*args, **kwargs)
    return decorated

@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    return jsonify({'message': 'This is a protected endpoint'}), 200

@app.route('/contact', methods=['GET'])
@jwt_required()
def contact():
    current_user_id = get_jwt_identity()
    try:
        conn = connect_db()
        with conn.cursor() as cursor:
            sql = "SELECT profile_img, name, m_rank, unit FROM Contact WHERE user_id = %s"
            cursor.execute(sql, (current_user_id,))
            contacts = cursor.fetchall()
            return jsonify(contacts), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route('/contact_add', methods=['POST'])
@jwt_required()
def contact_add():
    current_user_id = get_jwt_identity()
    data = request.json
    name = data.get('name')
    military_id = data.get('military_id')
    
    try:
        conn = connect_db()
        with conn.cursor() as cursor:
            sql = "SELECT user_id FROM User WHERE username = %s AND military_id = %s"
            cursor.execute(sql, (name, military_id))
            result = cursor.fetchone()
            if result:
                contact_user_id = result['user_id']
                sql_insert = "INSERT INTO Contact (user_id, contact_user_id) VALUES (%s, %s)"
                cursor.execute(sql_insert, (current_user_id, contact_user_id))
                conn.commit()
                return jsonify({"message": "Contact added successfully"}), 200
            else:
                return jsonify({"error": "User with the provided name and military_id does not exist"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)
