from flask import Flask, redirect, render_template, request
import ibm_db
from dbconfig import get_db_credential
import random
import calendar
from markupsafe import escape
from datetime import datetime
import pandas as pd
        



app = Flask(__name__)

# finding current year 
def curyear():
    today = datetime.now()

    year = today.strftime("%Y")
    
    return year

# finding current month 

def curmon():  
    today = datetime.now() 
    month3 = today.strftime("%m")
    return month3

def fullmonth():
    today = datetime.now()
        
    month1 = today.strftime("%B")
    return month1

# generating ids 

randomlist=[]
def randomno():
    
    random_id=random.randrange(100,999)
    if random_id not in randomlist:
        randomlist.append(random_id)
        return random_id
    else:
        randomno()
        


        
# default values 
nameOfUser=" "


# conn = ibm_db.connect(get_db_credential()," "," ")

# sql = "SELECT * FROM user"
# print(sql)
# stmt = ibm_db.exec_immediate(conn, sql)
# student = ibm_db.fetch_row(stmt)
# print ("The Name is : ",  student)

@app.route("/", methods=["POST", "GET"])
def login():
    print(get_db_credential)

    if request.method == "POST":
        try:
            conn = ibm_db.connect(get_db_credential()," "," ") 
            userName = request.form['Uname']
            Password = request.form['pass']
            sql = "SELECT * FROM user WHERE uname =? and pwd=?"
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt,1,userName)
            ibm_db.bind_param(stmt,2,Password)
            ibm_db.execute(stmt)
            details = ibm_db.fetch_assoc(stmt)
            global nameOfUser
            nameOfUser=userName 
            if details:
                return redirect("/home")
                
            else:
                error="Invalid username or password"    
                return render_template("login.html",error=error)
        except:
            print("error occured while login")
        finally:
            ibm_db.close(conn)
           
    else:
        return render_template("login.html")


@app.route("/register",methods=["POST","GET"])
def register():
    if request.method == "POST":
        userName = request.form['Uname']
        Password = request.form['pass']
        email = request.form['email']
        
        conn = ibm_db.connect(get_db_credential()," "," ") 

        sql = "SELECT * FROM user WHERE uname =? "
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,userName)
        ibm_db.execute(stmt)
        details = ibm_db.fetch_assoc(stmt)
        if details:
            error = "Username already taken"
            return render_template("register.html",error=error)
        
        
        try:    
            conn = ibm_db.connect(get_db_credential()," "," ") 
            sql = "INSERT INTO user VALUES (?,?,?,?)"
            prep_stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(prep_stmt, 1, randomno())

            ibm_db.bind_param(prep_stmt, 2, userName)
            ibm_db.bind_param(prep_stmt, 3, Password)
            ibm_db.bind_param(prep_stmt, 4, email)
                

            ibm_db.execute(prep_stmt)
            global nameOfUser
            nameOfUser=userName 
             
        except:
            print("error occured while registering")
        finally:
            ibm_db.close(conn)
     
        return redirect("/home")
    
    else:       
        return render_template("register.html")




@app.route("/forgotpassword",methods=["POST","GET"])
def forgotpassword():
    if request.method == "POST":
        userName = request.form['Uname']
        Password = request.form['pass']
        try:    
            conn = ibm_db.connect(get_db_credential()," "," ") 
            
            sql = "UPDATE user SET pwd = ? WHERE uname=?"
            prep_stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(prep_stmt, 1, Password)
            ibm_db.bind_param(prep_stmt, 2, userName)
            ibm_db.execute(prep_stmt)
            
        except:
            print("error occured while updating password")
        finally:
            ibm_db.close(conn)
        success="Password changed successfully !"
       
        return render_template("forgotpassword.html",success=success)
    
    else:       
        return render_template("forgotpassword.html")



@app.route("/home",methods=["POST","GET"])
def home():
    if request.method == "GET":
        
        # getting amount  
        expenselist=[]
        lis2=[]
        conn = ibm_db.connect(get_db_credential()," "," ") 
        sql = "SELECT * FROM income WHERE uname =?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,nameOfUser)
        ibm_db.execute(stmt)
        details = ibm_db.fetch_assoc(stmt) 
        if details:
            amount=ibm_db.result(stmt,1)
        else:
            amount=0
        # grtting expenses 
        
        lis1=[]
        currentmonth=curmon()
        currentyear=curyear()
        dateofexpense=f'{currentyear}-{currentmonth}-00'
        enddate=f'{currentyear}-{currentmonth}-32'
        
        sum=0
        
        conn = ibm_db.connect(get_db_credential()," "," ") 
        sql = "SELECT amount FROM expense WHERE uname= ? and ( VARCHAR_FORMAT (dateofexpense,'YYYY-MM-DD') > ? and VARCHAR_FORMAT (dateofexpense,'YYYY-MM-DD')< ?);"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,nameOfUser)
        ibm_db.bind_param(stmt,2,dateofexpense)
        ibm_db.bind_param(stmt,3,enddate)
        ibm_db.execute(stmt)
            
            # ibm_db.exec_immediate(conn,sql)
            
        while ibm_db.fetch_row(stmt)!= False:     
            lis1.append(ibm_db.result(stmt,0))
        for i in lis1:
            sum=sum+int(i)    
        lis1=[]
        
        remaining=int(amount)-int(sum)
        
        if not remaining:
            remaining=0
        
        conn = ibm_db.connect(get_db_credential()," "," ") 
        sql = "SELECT * FROM expense WHERE uname= ? ORDER BY dateofexpense DESC LIMIT 5;"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,nameOfUser)
        ibm_db.execute(stmt)
          
        while ibm_db.fetch_row(stmt)!= False:
            for i in range(6):
                 lis2.append(ibm_db.result(stmt,i))
            expenselist.append(lis2) 
            lis2=[]
            

            # my_data = [remaining, sum]
            # my_labels = 'Remaining ', 'Spent '
            # my_colors = ['lightblue', 'lightsteelblue']
            # my_explode = (0, 0.1)
            # plt.pie(my_data, labels=my_labels, autopct='%1.1f%%', startangle=15, shadow=True, colors=my_colors, explode=my_explode)
            # plt.title('Your budget ')
            # plt.axis('equal')
            # plt.show()
                
    
        return render_template("home.html",amount=amount,remaining=remaining,expense=sum,expenselist=expenselist)


@app.route("/account",methods=["POST","GET"])
def account():
    if request.method == "POST":
        
        amount = request.form['amount']
        
        try:    
            conn = ibm_db.connect(get_db_credential()," "," ") 
            
            sql = "UPDATE income SET amount = ? WHERE uname=?"
            prep_stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(prep_stmt, 1, amount)
            ibm_db.bind_param(prep_stmt, 2, nameOfUser)
            ibm_db.execute(prep_stmt)
            global incomeofuser
            incomeofuser=amount
            
        except:
            print("error occured while updating amount")
        finally:
            ibm_db.close(conn)
        
        return redirect("/account")
        
    else:
        conn = ibm_db.connect(get_db_credential()," "," ") 
        sql = "SELECT * FROM income WHERE uname =?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,nameOfUser)
        ibm_db.execute(stmt)
        details = ibm_db.fetch_assoc(stmt) 
        if details:
            amount=ibm_db.result(stmt,1)
            
            
        else:
            conn = ibm_db.connect(get_db_credential()," "," ") 
            sql = "insert into income values(?,?)"
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt,1,nameOfUser)
            ibm_db.bind_param(stmt,2,0)
            ibm_db.execute(stmt)
            amount=0
      
        return render_template("account.html",userName="Welcome! "+nameOfUser,amount=amount)





    
    
if __name__ == "__main__":
    
    app.run(debug=True)