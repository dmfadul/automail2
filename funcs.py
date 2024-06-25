import os
import json
import utils
import unidecode
import credentials
from engine import Session
from selenium.common.exceptions import ElementNotInteractableException

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


def multi_send(subject_text, main_text):
    try:
        _multi_send(subject_text=subject_text, main_text=main_text, restart=False)
    except Exception as e:
        print(f"Error preparing email: {e}")
        # _multi_send(subject_text=subject_text, main_text=main_text, restart=True)
        # Descobrir o erro e substituir. Deve ser 'NonInteractibleElement' ou algo assim.


def _multi_send(subject_text, main_text, restart=False):
    login = credentials.login
    passwd = credentials.passwd

    if not restart:
        curso, doc_name = utils.get_course_name()
        if curso == 1:
            return 1
        email_pdf_path = f"Annexes/trmemail/{doc_name}"
        names = utils.prepare_annexes("Annexes", doc_name)
        class_name = utils.prepare_email_list(pdf_path=email_pdf_path, names=names)

    else:
        with open("current_course.json", 'r') as f:
            current_course_dict = json.load(f)
            curso = current_course_dict["course"]
            doc_name = current_course_dict["doc_name"]
            class_name = current_course_dict["class_name"]
   
        print(f"restarting {class_name}")

    with open(f"emails/{class_name}.txt", 'r') as f:
        lines = f.readlines()

    names_emails = []
    for line in lines:
        name, email = [item.strip() for item in line.split(',')]
        names_emails.append((name, email))

    if restart:
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
    for name, email_address in names_emails:
        print(f"{name} - {email_address}")
      
        session.prepare_email(subject=f"{subject_text}{curso}", text=main_text, recipient=email_address)
        flag = session.attach_annexes_by_folder(name, doc_name)

        if flag or email_address == "*":
            num_fails += 1

            if flag:
                print(f"NOT SENT: {name} - Has no annex")
                result = f"{name}: FAILED - NO ANNEX\n"
            else:
                print(f"NOT SENT: {name} - Has no email address")
                result = f"{name}: FAILED - NO EMAIL\n"
            
            with open(f"logs/{class_name}.log", 'a') as f:
                f.write(f"{result}")

            session.reset()
            continue
        
        flag = session.send()
        utils.log(flag, name, class_name)

    print(f"NUMBER OF FAILURES: {num_fails}")
    # session.end_session()
