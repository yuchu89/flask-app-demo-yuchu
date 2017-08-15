from flask import Flask, render_template, request, jsonify
from flask import Flask,jsonify, flash, redirect,json, render_template, request, session, abort
from flask.ext.mysql import MySQL
from werkzeug import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'yuchucao'
app.config['MYSQL_DATABASE_PASSWORD'] = 'hA218218'
app.config['MYSQL_DATABASE_DB'] = 'yuchucao'
app.config['MYSQL_DATABASE_HOST'] = 'yuchucao.cwvhmvliz9wg.us-east-1.rds.amazonaws.com'
mysql.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()

@app.route('/')
def main():
    if not session.get('logged_in'):
        return render_template('index.html')
    else:
        return "Hi there!  <a href='/logout'>Logout</a>"


@app.route('/logout')
def logout():
    session.pop('user',None)
    return redirect('/')

@app.route('/about')
def showAbout():
    return render_template('about.html')

@app.route('/contact')
def showContact():
    return render_template('contact.html')

@app.route('/showSignin')
def showSignin():
    return render_template('signin.html')

@app.route('/showSignUp')
def showSignUp():
	return render_template('form.html')

@app.route('/process', methods=['POST'])
def process():
    conn = mysql.connect()
    cursor = conn.cursor()
    try:
	email = request.form['email']
	name = request.form['name']
	if name and email:
                cursor.callproc('sp_createUser',(email,name ))
                data = cursor.fetchall()
                
                if str(data) == 'None':
                        conn.commit()
		        return jsonify({'name' : 'User Created!'})
                else:
                        return jsonify({'error':'Use Already Exists!'})

  	else:
                return jsonify({'error' : 'Missing data!'})

    except Exception as e:
       return (str(e))
    finally:
        cursor.close()
        conn.close()


@app.route('/validateLogin',methods=['POST'])
def validateLogin():
    conn = mysql.connect()
    cursor = conn.cursor()
    try:
        _username = request.form['inputEmail']
        _password = request.form['inputPassword']
 
 
 
        # connect to mysql
        cursor.callproc('sp_validateLogin',(_username,))
        data = cursor.fetchall()
 
 
 
 
        if len(data) > 0:
            if (str(data[0][2])==_password):
                session['user'] = data[0][1]
                return redirect('/userHome')
            else:
                #return jsonify({'error':str(data[0][2])})
                return render_template('error.html',error = 'Wrong Email address or Password.')
        else:
            return render_template('error.html',error = 'Wrong Email address or Password.')
 
 
    except Exception as e:
        return render_template('error.html',error = str(e))
    finally:
        cursor.close()
        conn.close()

@app.route('/showcustomer')       
def showCustomer():
    conn = mysql.connect()
    cursor = conn.cursor()
    try:

       query = "SELECT CUST_CODE,CUST_NAME,CUST_CITY from customer"
       cursor.execute(query)


       data = cursor.fetchall()

       return render_template("customer.html", data=data)

    except Exception as e:
       return (str(e))
    finally:
        cursor.close()
        conn.close()

@app.route('/view_entry/<id>')
def view_entry(id):
    conn = mysql.connect()
    cursor = conn.cursor()
    try:
       cursor.execute("select customer.CUST_CODE, customer.CUST_NAME, cust_city,cust_country,phone_no , ORD_NUM, ORD_AMOUNT,ADVANCE_AMOUNT, ORD_DESCRIPTION \
       from orders join customer on customer.CUST_CODE= orders.CUST_CODE where customer.CUST_CODE= %s order by ORD_NUM  ", (id))
    
       data = cursor.fetchall()
       return render_template('view_entry.html', data=data)

    except Exception as e:
       return (str(e))
    finally:
        cursor.close()
        conn.close()


@app.route('/userHome')
def userHome():
    return render_template('userHome.html')

if __name__ == '__main__':
        app.secret_key = os.urandom(12)
	app.run(debug=True)
