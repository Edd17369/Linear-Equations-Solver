from flask import Flask, request, render_template, url_for, redirect, flash
import os
from dotenv import load_dotenv
from sympy import sympify

load_dotenv() 

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")



def linear_system_solver(system):
    error = None
    # Return index of the first non-zero value
    def fcn(arr, n): 
        for i in range(n):
            if arr[i]:
                return i
        return n+1
    # Matrix
    M = [i.split(',') for i in system[1:-1].split(';')]
    n, m = len(M[0]), len(M)
    matrix = ''
    for i in range(m):
        matrix += ( '& + &' ).join(['\\ '+M[i][j]+'\ x_{'+str(j+1)+'}' for j in range(n-1)])+' & = & '+M[i][n-1] + ' \\\ '
    
    x = [0 for i in range(n-1)]
    M = [[sympify(M[j][i]) for i in range(n)] for j in range(m)]
    M.sort(reverse=True)
    # Echelon matrix
    for i in range(m):
        index = fcn(M[i],n-1)
        if M[i][n-1] and index > n-1:
            error = 'Without Solution'
        if index < n: 
            M[i] = [M[i][k]/M[i][index] for k in range(n)]
            x[index] = 1
        for j in range(m):
            if j != i and index < n:
                M[j]=[M[j][k]-(M[i][k]*M[j][index]) for k in range(n)]  
    # Useful function  
    def construct_col(k, sgn, var):        
        col = ['0'+'\\ '+var for i in range(n-1)]
        l = [M[i][k] for i in range(m)]
        z = 0
        for i in range(n-1):
            if x[i]: 
                col[i] = str(sgn*l[i-z])+'\\ '+var
            else:
                z += 1
        return col
    # Output
    variables = ( ' \\\ ' ).join(['x_{'+str(j+1)+'}' for j in range(n-1)])
    values = ( ' \\\ ' ).join(construct_col(n-1,1,''))
    ans = []
    for i in range(n-1):
        if not x[i]:
            l = construct_col(i,-1, 'x_{'+str(i+1)+'}')
            l[i] = '1'+'\\ '+ 'x_{'+str(i+1)+'}'
            ans.append(( ' \\\ ' ).join(l))
    return {'matrix':matrix, 'variables':variables, 'values':values, 'ans': ans, 'error':error}



@app.route('/', methods=['GET', 'POST']) 
def solver():
    if request.method == 'POST':
        inp = request.form['matrix']
        try:
            sol = linear_system_solver(inp)
            error = sol['error']
            if error:
                flash(error)
                return render_template("index.html", matrix=inp)
            mtx = sol['matrix']
            var = sol['variables']
            val = sol['values']
            ans = sol['ans']
            return render_template('index.html', mtx=mtx, var=var, val=val, ans=ans, matrix=inp)
        except:
            flash("There has been a problem. Please check your system matrix")
            return render_template("form.html", matrix=inp)
    else:
        return render_template("index.html")






# To run the application you can either use the 'flask run' command or python’s -m switch with Flask. Before you can do that you
# need to tell your terminal the application to work with by exporting the FLASK_APP environment variable 'set FLASK_APP=hello.py'
# on command line and '$env:FLASK_APP = "mysolver.py"' en powershell

# To enable all development features (including debug mode) you can export the FLASK_ENV environment variable and set it to 
# development before running the server 'FLASK_ENV=development, default=production'
# $env:FLASK_ENV = "development"



