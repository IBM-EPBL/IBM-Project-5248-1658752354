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



@app.route("/budgets",methods=["POST","GET"])
def budgets():
    if request.method == "POST":
        
        budgetname = request.form['budgetname']
        month = request.form['month']
        amt = request.form['amount']
        Groceries = request.form['Groceries']
        Housing = request.form['Housing']
        Utilities = request.form['Utilities']
        DiningOut = request.form['DiningOut']
        Shopping = request.form['Shopping']
        Travel = request.form['Travel']
        Entertainment = request.form['Entertainment']
        Others = request.form['Others']
        Savings = request.form['Savings']
        sum = int(Groceries)+int(Housing)+int(Utilities)+int(DiningOut)+int(Shopping)+int(Travel)+int(Entertainment)+int(Others)+int(Savings)          

# checking amount is equal or not 
# getting amount to calulate total is equal or not 
        error=False
        conn = ibm_db.connect(get_db_credential()," "," ") 
        sql = "SELECT * FROM income WHERE uname =?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,nameOfUser)
        ibm_db.execute(stmt)
        details = ibm_db.fetch_assoc(stmt) 
        if details:
            amount=ibm_db.result(stmt,1)
        else:
            error="First add the income in account"
    # inserting budget 
    
        if not error:
            if int(amt)==int(amount):
                if int(amt)==sum:
                            try:    
                                conn = ibm_db.connect(get_db_credential()," "," ") 
                                sql = "INSERT INTO budget VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)"
                                prep_stmt = ibm_db.prepare(conn, sql)
                                ibm_db.bind_param(prep_stmt, 1,nameOfUser )

                                ibm_db.bind_param(prep_stmt, 2, budgetname)
                                ibm_db.bind_param(prep_stmt, 3, month)
                                ibm_db.bind_param(prep_stmt, 4, amt)
                                ibm_db.bind_param(prep_stmt, 5,Groceries )
                                ibm_db.bind_param(prep_stmt, 6,Housing )
                                ibm_db.bind_param(prep_stmt, 7,Utilities )
                                ibm_db.bind_param(prep_stmt, 8, DiningOut)
                                ibm_db.bind_param(prep_stmt, 9, Shopping)
                                ibm_db.bind_param(prep_stmt, 10, Travel)
                                ibm_db.bind_param(prep_stmt, 11,Entertainment )
                                ibm_db.bind_param(prep_stmt, 12,Others )
                                ibm_db.bind_param(prep_stmt, 13,Savings )

                                    

                                ibm_db.execute(prep_stmt)
                                    
                            except:
                                print("error occured while registering")
                            finally:
                                ibm_db.close(conn)
                            return redirect("/budgets")
                else:
                    error="Total amount is not equal to budget amount"
            else:
                error="Budget amount is not equal to income"
            
        if error:
            return render_template("budgets.html",error=error)
        
        
    else:
        try:
            budgetlist=[]
            
            conn = ibm_db.connect(get_db_credential()," "," ") 
            sql = "SELECT * FROM budget WHERE uname =?"
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt,1,nameOfUser)
            ibm_db.execute(stmt)
            if ibm_db.fetch_row(stmt)!= False:
                for i in range(13):
                    budgetlist.append(ibm_db.result(stmt,i))
                print(budgetlist)
                x = budgetlist[2]
                budgetlist[2]= calendar.month_name[x]
                # print(calendar.Calendar.month_name[11])
                return render_template("budgets.html",budgetlist=budgetlist)
            
            else:
                return render_template("budgets.html")
                
                    
                
        except:
            print("error while displaying budget")
        
        

@app.route("/deletebudget")
def deletebudget():
    # getting amount and user name to delete budget 
    conn = ibm_db.connect(get_db_credential()," "," ") 
    sql = "SELECT * FROM income WHERE uname =?"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt,1,nameOfUser)
    ibm_db.execute(stmt)
    details = ibm_db.fetch_assoc(stmt) 
    if details:
        amount=ibm_db.result(stmt,1)
        
    # delete the budget     
    try:    
        conn = ibm_db.connect(get_db_credential()," "," ") 
            
        sql = "DELETE FROM budget WHERE uname=? and amount=?"
        prep_stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(prep_stmt, 1, nameOfUser)
        ibm_db.bind_param(prep_stmt, 2, amount)
        ibm_db.execute(prep_stmt)
            
    except:
        print("error occured while updating amount")
    finally:
        ibm_db.close(conn)
        
    return redirect("/budgets")
    

@app.route("/expenses",methods=["POST","GET"])
def expenses():
    

    if request.method == "POST":
        categorylist=[] 
        expenseamount=0   
        description = request.form['description']
        category = request.form['category']
        dateofexpense = request.form['dateofexpense']  
        amount = request.form['amount']
        try:
            expenseamountlist=[]
            sum=0
            conn = ibm_db.connect(get_db_credential()," "," ") 
            sql = "SELECT amount FROM expense WHERE uname=? and category=? "
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt,1,nameOfUser)
            ibm_db.bind_param(stmt,2,category)
            ibm_db.execute(stmt)
            
            # ibm_db.exec_immediate(conn,sql)
            
            while ibm_db.fetch_row(stmt)!= False:  
                expenseamountlist.append(ibm_db.result(stmt,0))
            for i in expenseamountlist:
                sum=int(sum)+int(i)
            
        except:
            print("error while checking expenses")
        # checking whether the expense is within the budget 
        try:
            
            conn = ibm_db.connect(get_db_credential()," "," ") 
            
            sql = "SELECT * FROM budget WHERE uname =?"
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt,1,nameOfUser)
            # # ibm_db.bind_param(stmt,2,category)
            ibm_db.execute(stmt)
            
            
            if ibm_db.fetch_row(stmt)!= False:
                val1=ibm_db.result(stmt,0)
                val2=ibm_db.result(stmt,1)
                val3=ibm_db.result(stmt,2)
                val4=ibm_db.result(stmt,3)
                val5=ibm_db.result(stmt,4)
                val6=ibm_db.result(stmt,5)
                val7=ibm_db.result(stmt,6)
                val8=ibm_db.result(stmt,7)
                val9=ibm_db.result(stmt,8)
                val10=ibm_db.result(stmt,9)
                val11=ibm_db.result(stmt,10)
                val12 =  ibm_db.result(stmt,11)
                val13=ibm_db.result(stmt,12)
                
                categorylist.append(["uname",val1])
                categorylist.append(["budgetname",val2])
                categorylist.append(["budgetmonth",val3])
                categorylist.append(["amount",val4])
                categorylist.append(["groceries",val5])
                categorylist.append(["housing",val6])
                categorylist.append(["utilities",val7])
                categorylist.append(["diningout",val8])
                categorylist.append(["shopping",val9])
                categorylist.append(["travel",val10])
                categorylist.append(["entertainment",val11])
                categorylist.append(["others",val12])
                categorylist.append(["savings",val13])
                print(categorylist)
                for i in categorylist:
                    if i[0]==category:
                        amt=i[1]
                                      
            else:
                error="budget is not created"
                return render_template("expenses.html",error=error)
                           
                
        except:
            print("error while displaying budget")
        # checking expense is within the budget or not 
        expenseamount=int(amt)-sum
        if int(amount)<=int(amt) and int(amount)<=expenseamount:
             
                    #  insert into db 
            try:    
                conn = ibm_db.connect(get_db_credential()," "," ") 
                sql = "INSERT INTO expense VALUES (?,?,?,?,?,?)"
                prep_stmt = ibm_db.prepare(conn, sql)
                ibm_db.bind_param(prep_stmt, 1, randomno())

                ibm_db.bind_param(prep_stmt, 2, nameOfUser)
                ibm_db.bind_param(prep_stmt, 3, description)
                ibm_db.bind_param(prep_stmt, 4, category)
                ibm_db.bind_param(prep_stmt, 5, dateofexpense)
                ibm_db.bind_param(prep_stmt, 6, amount)
                    
                ibm_db.execute(prep_stmt)      
            except:
                
                print("error occured while inserting expense")
            finally:
                ibm_db.close(conn)
         
            return redirect("/expenses")
        else:
            error=f"expense exceeds the budget amount for {category} category"
            return render_template("expenses.html",error=error)
    else:
        # display all the expenses    
        
        # try:
        expenselist=[]
        lis1=[]
        sum=0
        error="Currently no expenses"
        conn = ibm_db.connect(get_db_credential()," "," ") 
        sql = "SELECT * FROM expense WHERE uname=?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,nameOfUser)
        ibm_db.execute(stmt)
            
            # ibm_db.exec_immediate(conn,sql)
            
        while ibm_db.fetch_row(stmt)!= False:
            for i in range(6):
                 lis1.append(ibm_db.result(stmt,i))
            expenselist.append(lis1) 
            lis1=[]
            error=False
        
        if error:
            return render_template("expenses.html",error=error)
            
            
        # except:
        #     print("error while checking expenses")
        
        return render_template("expenses.html",expenselist=expenselist)


@app.route("/deleteexpense",methods=["POST","GET"])
def deleteexpense():
    if request.method == "POST": 
        id = request.form['id']
        uname = request.form['uname']
        try:    
            conn = ibm_db.connect(get_db_credential()," "," ") 
                
            sql = "DELETE FROM expense WHERE id=? and uname=?"
            prep_stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(prep_stmt, 1, id)
            ibm_db.bind_param(prep_stmt, 2, uname)
            ibm_db.execute(prep_stmt)
            
        except:
            print("error occured while deleting expense")
            
        finally:
            ibm_db.close(conn)
        return redirect("/expenses")


    
    
if __name__ == "__main__":
    
    app.run(debug=True)