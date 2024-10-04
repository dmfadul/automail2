import os
import json
import utils
import unidecode
import credentials
from engine import Session
from selenium.common.exceptions import ElementNotInteractableException


def multi_send(subject_text, main_text, restart=False):
    while True:
        if not restart:
            curso, doc_name = utils.get_course_name()
            if curso == 1: return 1

            path = f"Annexes/trmemail/{doc_name}"
            names = utils.prepare_annexes("Annexes", doc_name)

            class_name = utils.prep_email_list(addr_path=path, names=names)
            names_emails = utils.get_class_email_addresses(class_name)

        elif restart:
            curso, doc_name, class_name = utils.get_restart_info()  
            all_names_emails = utils.get_class_email_addresses(class_name)
            names_emails = utils.get_restarted_names_emails(class_name, all_names_emails)
            print(f"restarting {class_name}")

        session = Session()
        session.login_mail(credentials.login, credentials.passwd)

        num_fails = 0
        for name, email_address in names_emails:
            print(f"{name} - {email_address}")

            session.prepare_email(subject=f"{subject_text}{curso}", text=main_text, recipient=email_address)
            flag = session.attach_annexes_by_folder(name, doc_name)

            if flag or email_address == "*":
                utils.log_error(flag, name, class_name)
                num_fails += 1
                # session.reset() # what does reset do? try deleting it.
                continue
            
            try:
                flag = session.send()
                restart = False
                utils.log(flag, name, class_name)

            except ElementNotInteractableException:
                print("Ocorreu um erro. Reiniciando...")
                restart = True
                session.end_session()

        if not restart:
            break

        print(f"NUMBER OF FAILURES: {num_fails}")
        # session.end_session()
