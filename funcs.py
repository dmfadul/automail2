import os
import json
import utils
import unidecode
from engine import Session

# annexes_path = "/home/david/Files/automail/Annexes/"


def send_email(user, password, subject, text, recipient, paths_annexes):
    session = Session()
    session.login_mail(user, password)
    session.prepare_email(subject, text, recipient, conf_reading=True)

    if session.attach_annexes(paths_annexes):
        session.reset()
        return 1

    session.send()
    return 0


def multi_send(doc_name, curso, subject_text, main_text, login, passwd, c_name=None):   
    email_pdf_path = f"Annexes/trmemail/{doc_name}"
    # create folders with clean names for the files, and return the folder's names
    names = utils.prepare_annexes("Annexes", doc_name)
    if c_name is None:
        class_name = utils.prepare_email_list(pdf_path=email_pdf_path, names=names)
    else:
        class_name = c_name
        print(f"restarting {class_name}")

    with open(f"emails/{class_name}.txt", 'r') as f:
        lines = f.readlines()

    names_emails = []
    for line in lines:
        name, email = [item.strip() for item in line.split(',')]
        names_emails.append((name, email))

    if c_name is not None:
        with open(f"logs/{class_name}.log", 'r') as f:
            lines = f.readlines()
            test_names = []
            for line in lines:
                test_name = line.split(':')[0].strip()
                test_status = line.split(':')[1].strip()
                if test_status == "FAILED":
                    test_names.append(test_name)
            last_name = lines[-1].split(":")[0].strip()

        names_emails_copy = names_emails.copy()
        names_emails = []
        for i, name_email in enumerate(names_emails_copy):
            if name_email[0] in test_names:
                names_emails.append(name_email)
            if name_email[0] == last_name:
                names_emails.extend(names_emails_copy[i+1:])
                break

    session = Session()
    session.login_mail(login, passwd)

    num_fails = 0
    for item in names_emails:
        print(item)
        email_address = item[1]
        folder_name = unidecode.unidecode(item[0])

        script_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(script_dir, "Annexes", folder_name, doc_name)

        annex = [path]

        session.prepare_email(subject=f"{subject_text}{curso}", text=main_text, recipient=email_address)

        if session.attach_annexes(paths_annexes=annex) or email_address == "*":
            num_fails += 1
            if email_address == "*":
                print(f"NOT SENT: {item[0]} - Has no email address")
                result = f"{item[0]}: FAILED - NO EMAIL\n"
            else:
                print(f"NOT SENT: {item[0]} - Has no annex")
                result = f"{item[0]}: FAILED - NO ANNEX\n"

            with open(f"logs/{class_name}.log", 'a') as f:
                f.write(f"{result}")

            session.reset()
            continue

        if session.send():
            result = f"{item[0]}: success\n"
        else:
            result = f"{item[0]}: FAILED\n"

        with open(f"logs/{class_name}.log", 'a') as f:
            f.write(f"{result}")

    print(f"NUMBER OF FAILURES: {num_fails}")
    # session.end_session()
