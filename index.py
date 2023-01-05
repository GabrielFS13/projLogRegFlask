import smtplib
from email.message import EmailMessage
from flask import Flask, render_template, request, redirect
import os 
from dotenv import load_dotenv
import mysql.connector
from random import randint
from twilio.rest import Client

from banco import Banco
load_dotenv()

#variaveis de email
mail_adrress = os.getenv("EMAIL_ADRRES")
mail_password = os.getenv("EMAIL_PASSWORD")

#variaveis para o envio de SMS
ac_sid = os.getenv("ACC_SID")
au_token = os.getenv("AUTH_TOKEN")
phone_num = os.getenv("PHONE_NUMBER")

#variaveis para conexao de BD
host = os.getenv("HOST")
bd_pass = os.getenv("PASSWORD")
user = os.getenv("USER")

mydb = mysql.connector.connect(
  host= host,
  user= user,
  password= bd_pass,
  database = 'db_projflask'
)


client = Client(ac_sid, au_token)
banco = Banco(mydb)

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
@app.route('/Login', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['password']

        myresult = banco.select(email, senha)

        if len(myresult) == 0:
            return redirect('/Register')
        else:
            rnd = randint(100, 999)
            mycursor = mydb.cursor()
            sql_query = f"SELECT num_tel FROM tb_contas WHERE email = '{email}';"
            mycursor.execute(sql_query)
            myresult = mycursor.fetchall()

            sms_message = client.messages.create(
                body = f"Seu codigo de verificação é esse: {rnd}",
                from_ = phone_num,
                to = myresult[0][0]
            )
            
            emailMSG = EmailMessage()
            emailMSG['Subject'] = 'Código de Verificação'
            emailMSG['From'] = mail_adrress
            emailMSG['To'] = email
            emailMSG.set_content(f'Seu código de verificação é: {rnd}')

            #Enviar o email
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login(mail_adrress, mail_password)
                smtp.send_message(emailMSG)
                
            
            

            return redirect('/Logged')

    return render_template('index.html')


@app.route('/Register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        if request.form['password'] != request.form['conf_password']:
            return "Senhas diferentes!"
        else:
            nome = request.form['nome']
            email = request.form['email']
            senha = request.form['password'] #criptografar, faz o favor
            num_tel = "+55" + request.form['telefone']

            #próximo passo Query SQL
            mycursor = mydb.cursor()
            sql_query = f"INSERT INTO tb_contas (nome, email, senha, num_tel) VALUES ('{nome}', '{email}', '{senha}', '{num_tel}');"
            mycursor.execute(sql_query)
            mydb.commit()
            #redirecionar para pagina de user ou login
            return redirect('/Logged')
    return render_template('register.html')


@app.route("/Logged")
def logged():
    return render_template("logged.html", username = "Gabriel")

if __name__ == "__main__":
    app.run(debug=True)