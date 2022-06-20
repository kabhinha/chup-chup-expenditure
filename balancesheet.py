from email.message import EmailMessage
from string import Template
from pathlib import Path
import sqlite3
import smtplib
import time
import datetime
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))
mydb = sqlite3.connect("data.db")
cursor = mydb.cursor()

def sendmail(name, Id, passwd, to, subject):
    Today = str(datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S"))
    report = Template(Path("report.html").read_text()).substitute({"name": name, "today": str(Today)})
    mail = EmailMessage()
    mail["from"] = Id
    mail["to"] = to
    mail["subject"] = subject
    mail.set_content(report, "html")

    try:
        with smtplib.SMTP("SMTP.gmail.com", 587) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(Id, passwd)
            server.send_message(mail)
    except Exception as e:
        print("%s: %s"%(e.__class__.__name__, e))


def welcome(db):
    print(500*"\n")

    print(r"""
    \                /    |------    |         |------       --       |\      /|    |------
     \      /\      /     |          |         |           /    \     | \    / |    |      
      \    /  \    /      |------    |         |          |      |    |  \  /  |    |------
       \  /    \  /       |          |         |          |      |    |   \/   |    |      
        \/      \/        |------    |------   |------     \ -- /     |        |    |------
    
    """)
    pin = input("Enter your Pin: ")
    
    for Details in db:
        if pin==Details[1]:
            details = Details
            return details
    print("Invalid pin entered")
    time.sleep(2)
    exit()


def create_users():
    details = (input("Enter pin you want to create: "), input("Enter your name: "), input("Enter youe Email ID: "), input("Enter your password: "))

    cursor.execute(f"""
                        INSERT INTO users (`Pin`, `Name`, `Id`, `Passwd`)
                        VALUES (?, ?, ?, ?)
                    """, details)
    mydb.commit()


def update_report(records):
    with open("report.html", "w") as f:
        total = 0
        report = """
<!doctype html>
<html lang="en">
<head>
    <!-- Required meta tags -->
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <!-- CSS -->
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/css/bootstrap.min.css" integrity="sha384-9aIt2nRpC12Uk9gS9baDl411NQApFmC26EwAOH8WgZl5MYYxFfc+NcPb1dKGj7Sk" crossorigin="anonymous" />
    <style>
        .add {
            color: green;
            font-style: "italic bold";
        }

        .expense {
            color: red;
            font-style: italic bold;
        }

        .null {
            color: rgb(72, 212, 142);
            font-style: italic bold;
        }
    </style>
</head>
<body>
    <p><b>
        hey, $name
        <br/>&nbsp;&nbsp;your expenditure till $today is as follows:<br/><br/>
    </b></p>
    <table class="table">
        <thead>
            <tr>
                <th scope="col">S.NO</th>
                <th scope="col">Amount</th>
                <th scope="col">Item</th>
                <th scope="col">Date and time</th>
            </tr>
        </thead>
        <tbody>
    """
    
        for i in records:
            if i[2] in ("add", "aDD", 'AdD', "ADd", "ADD"):
                total += int(i[1])
                report += f"""
                <tr class="add">
                    <th scope="row">{i[0]}</th>
                    <td>+INR {i[1]}</td>
                    <td>  </td>
                    <td>{i[3]}</td>
                </tr>
        """
            elif i[1] in ("add", "aDD", 'AdD', "ADd", "ADD"):
                total += int(i[2])
                report += f"""
                <tr class="add">
                    <th scope="row">{i[0]}</th>
                    <td>+INR {i[2]}</td>
                    <td>  </td>
                    <td>{i[3]}</td>
                </tr>
        """

            else:
                total -= int(i[1])
                report += f"""
                <tr class="expense">
                    <th scope="row">{i[0]}</th>
                    <td>{"- INR " + i[1]}</td>
                    <td>{i[2]}</td>
                    <td>{i[3]}</td>
                </tr>
        """


        if total>0:
            bal = "add"

        elif total==0:
            bal = "null"

        else:
            bal = "expense"

        report += f"""
        </tbody>
    </table>
    <hr/>
    <table class= "table">
        <tr class="{bal}">
            <th scope="row"></th>
            <td><b>Total</b></td>
            <td>                     </td>
            <td>{total}/-</td>
        </tr>
    
    <!-- Optional JavaScript -->
    <!-- jQuery first, then Popper.js, then Bootstrap JS -->
    <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js" integrity="sha384-DfXdz2htPH0lsSSs5nCTpuj/zy4C+OGpamoFVy38MVBnE+IbbVYUew+OrCXaRkfj" crossorigin="anonymous"></script>
    <script src="https://cdn.jsdelivr.net/npm/popper.js@1.16.0/dist/umd/popper.min.js" integrity="sha384-Q6E9RHvbIyZFJoft+2mJbHaEWldlvI9IOYy5n3zV9zzTtmI3UksdQRVvoxMfooAo" crossorigin="anonymous"></script>
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/js/bootstrap.min.js" integrity="sha384-OgVRvuATP1z7JjHLkuOU7Xw704+h835Lr+6QL9UvYjZE3Ipu6Tp75j7Bh/kR0JKI" crossorigin="anonymous"></script>
</body>
</html>
    """
        f.write(report)


def engine():
    users = cursor.execute("SELECT rowid, * FROM users").fetchall()
    details = welcome(users)
    
    while True:
        Today = str(datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S"))
        manager = input(f"({details[2]})==> ")

        if manager.lower() in ("view", "show"):
            records = cursor.execute("SELECT rowid, * FROM memory").fetchall()
            for record in records:
                print(f"{record[0]}     {record[1]}     {record[2]}     {record[3]}")

        elif "sub" in manager.lower() or "send" in manager.lower():
            records = cursor.execute("SELECT rowid, * FROM memory").fetchall()
            update_report(records)
            manager = manager.split(" ")
            
            if len(manager)==4:
                sendmail(details[2], details[3], details[4], manager[1], manager[3])

            else:
                sub = ""
                for i in manager[3:]:
                    if i==manager[-1]:
                        sub += i
                
                    else:
                        i += " "
                        sub += i
                sendmail(details[2], details[3], details[4], manager[1], sub)

        elif manager.lower() in ("exit", "exit()", "byee", "byee()"):
            print(f"Thanks {details[2]}, for choosing us\n    your all entered records are saved in our database...")
            break

        elif manager.lower() in ("del", "d", "destroy"):
            cursor.execute("DELETE FROM memory WHERE 1")

        elif manager.lower() == "spd":
            id = cursor.execute("SELECT rowid FROM memory ORDER BY rowid DESC").fetchone()[0]

            cursor.execute(f'DELETE FROM memory WHERE rowid=={id}')
            mydb.cursor()

        else:
            try:
                if len(manager.split(" "))==2:
                    record = manager.split(" ") + [Today]
                    if record[0].lower()=="add":
                        record[0], record[1] = record[1], record[0]

                    cursor.execute("""
                                INSERT INTO `memory` (
                                    `Amount`,
                                    `Item`,
                                    `Date and time`
                                )
                                
                                VALUES (
                                    ?, ?, ?
                                )
                            """,
                            record)
                    mydb.commit()

                elif len(manager.split(" "))>2:
                    manager = manager.split(" ")
                    man = ""
                    for i in manager[1:]:
                        if i==manager[-1]:
                            man += i
                        else:
                            i += " "
                            man += i

                    if manager[0].lower()=="add":
                        manager[0], man = man, manager[0]
                    record = [manager[0]] + [man] + [Today]
                    cursor.execute("""
                                INSERT INTO `memory` (
                                    `Amount`,
                                    `Item`,
                                    `Date and time`
                                )
                                
                                VALUES (
                                    ?, ?, ?
                                )
                            """,
                            record)
                    mydb.commit()

                else:
                    print("Wrong record submitted")
            except Exception:
                print("Wrong record submited")


def main():
    try:
        cursor.execute("""
                    CREATE TABLE users (
                        `Pin` text,
                        `Name` text,
                        `Id` text,
                        `Passwd` text
                        )
                """)

        cursor.execute("""
                    CREATE TABLE memory (
                        `Amount` text,
                        `Item` text,
                        `Date and time` text
                    )
                """)
    except Exception:
        pass

    login = input("Do you want to login or signin\n=> ")
    if login.lower() in ("login", "log", "l"):
        create_users()
        engine()

    elif login.lower() in ("signin", "sign", "s"):
        engine()

    else:
        print("Error you have given a wrong input")
    mydb.close()

if __name__ == "__main__":
    main()
