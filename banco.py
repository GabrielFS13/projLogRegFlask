class Banco:
    def __init__(self, mydb):
        self.mydb = mydb

    def select(self, email, senha):
        mycursor = self.mydb.cursor()
        sql_query = f"SELECT email, senha FROM tb_contas WHERE email = '{email}' AND senha = '{senha}';"
        mycursor.execute(sql_query)
        myresult = mycursor.fetchall()

        return myresult

