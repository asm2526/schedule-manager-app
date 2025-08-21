import sqlite3 #using sqlite3
import hashlib #importing python password hasing


def hash_password(password):
    # hashing password
    return hashlib.sha256(password.encode()).hexdigest()
    # provides cryptographic hashing (SHA-256) to secure passwords, critical for app’s security.

def init_db():
    #initializing sql db and users table
    conn = sqlite3.connect('schedule_manager.db') 
    # creating database
    cursor = conn.cursor()
    # creating cursor object to execute SQl commands

    #creating users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')

    #removing test user if already there
    cursor.execute('DELETE FROM users WHERE username = ?', ('tester',))

    
    # adding a current sample user
    sample_username = "tester"
    sample_password = 'Testing123456!'
    password_hash = hash_password(sample_password)

    try:
        cursor.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)',
                       (sample_username, password_hash)) #question marks preventing SQL injection
        conn.commit()
        print(f"Sample user added: {sample_username}")
    except sqlite3.IntegrityError:
        print("Sample user already exists")
        #catching errors if the username already exists

    conn.close()
    #closing query

def verify_user(username, password):
    # verify if username and password match a databse record
    conn = sqlite3.connect('schedule_manager.db')
    cursor = conn.cursor()

    cursor.execute('SELECT password_hash FROM users where username = ?', (username,))
    result = cursor.fetchone() #fetching the first matching row

    conn.close()
    #closing connection

    if result:
            stored_hash = result[0]
            input_hash = hash_password(password)
            return stored_hash == input_hash
    return False

if __name__ == "__main__":
     init_db()
     # Testing verification
     test_result = verify_user("tester", "Testing123456!")
     print(f"verification test: {'Success' if test_result else 'Failed'}")
    
