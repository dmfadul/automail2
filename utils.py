import os
import re
import fitz
import json
import PyPDF2
import shutil
from unidecode import unidecode


def prepare_annexes(path, new_name):
    if not os.path.isdir(path):
        raise ValueError("Provided path is not a directory")

    for item in os.listdir(path):
        full_path = os.path.join(path, item)

        if os.path.isfile(full_path):
            # Remove extension and accents from file name
            file_name_without_ext = os.path.splitext(item)[0]
            folder_name = unidecode(file_name_without_ext.strip())

            # Create a new directory for the file
            new_dir_path = os.path.join(path, folder_name)
            os.makedirs(new_dir_path, exist_ok=True)

            # Move and rename the file
            new_file_path = os.path.join(new_dir_path, new_name)
            shutil.move(full_path, new_file_path)

    entries = os.listdir(path)
    folders = [entry for entry in entries if os.path.isdir(os.path.join(path, entry))]

    return folders


def prepare_email_list(pdf_path, names):
    corp_email_regex = r'\b[A-Za-z._%+-][A-Za-z0-9._%+-]*@pc\.pr\.gov\.br\b'
    human_email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        num_pages = len(reader.pages)
        text = ""

        for page_num in range(num_pages):
            page = reader.pages[page_num]
            text += page.extract_text()

        text = unidecode(text)

        class_name = text[text.index("Turma:") + len("Turma:"):]
        class_name = class_name[:class_name.index("\n")].strip()

        email_list = text[text.index(class_name) + len(class_name):text.index("Nome RG CPF Fone e-mail")]
        email_list = [e.strip() for e in email_list.split(',')]
        email_list = [e for e in email_list if e not in ['', None]]

        text = text[text.index("Nome RG CPF Fone e-mail"):]

    name_idx = []
    for name in names:
        if '.' in name:
            name = name.split('.')[0].strip()

        if name.lower() == "trmemail":
            continue

        try:
            temp = (name, text.index(name))
            name_idx.append(temp)
        except ValueError:
            print('not approved: ', name)

    name_idx.sort(key=lambda x: unidecode(x[0]))
    name_idx.append(("end", len(text)-1))

    name_email_pairs = []
    for i in range(len(name_idx) - 1):
        name = name_idx[i][0]
        start, finish = name_idx[i][1], name_idx[i+1][1]
        fragment = text[start:finish]
        corp_email, human_email = None, None
        for email in email_list:
            if email in fragment:
                email_fragment = email
                corp_email = re.findall(corp_email_regex, email_fragment)
                human_email = re.findall(human_email_regex, email_fragment)
                break

        corp_email = re.findall(corp_email_regex, fragment) if corp_email is None else corp_email
        human_email = re.findall(human_email_regex, fragment) if human_email is None else human_email

        if corp_email:
            name_email_pairs.append((name, corp_email[0]))
        elif human_email:
            name_email_pairs.append((name, human_email[0]))
        else:
            name_email_pairs.append((name, '*'))

    class_name = class_name.replace("/", "_")
    print(class_name)

    with open(f"emails/{class_name}.txt", 'w') as f:
        for pair in name_email_pairs:
            f.write(f"{pair[0].strip()}, {pair[1].strip()}\n")

    with open("current_course.json", 'r') as f:
        course_dict = json.load(f)

    with open("current_course.json", 'w') as f:
        course_dict["class_name"] = class_name
        json.dump(course_dict, f)
        
    return class_name


def get_course_name():
    script_dir = os.path.dirname(os.path.abspath(__file__))    
    folder_path = os.path.join(script_dir, "Annexes")
    try:
        files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    except Exception as e:
        print(f"Error accessing folder: {e}")
        return 1
    
    for file in files:
        if file is None or file == "trmemail.pdf":      
            continue

        current_course, doc_name = get_info_from_pdf(os.path.join(folder_path, file))
        break

    with open("courses.json", 'r') as f:
        course_names = json.load(f)
    
    if not current_course in course_names:
        print(f"O CURSO {current_course} NÃO ESTÁ CADASTRADO.\nCADASTRAR CURSO {current_course}? S/n", end=" ")
        response = input(" ")
        if response.lower() == "s" or response == "":
            course_names.append(current_course)
            with open("courses.json", 'w') as f:
                json.dump(course_names, f, indent=4)
        else:
            print("CURSO NÃO CADASTRADO")
            return 1, 1

    with open("current_course.json", 'w') as f:
        json.dump({"course": current_course, "doc_name": doc_name}, f, indent=4)

    return current_course, doc_name


def get_info_from_pdf(file_path):
    try:
        document = fitz.open(file_path)
        
        for page_num in range(len(document)):
            page = document.load_page(page_num)  # Load page
            text = page.get_text("text")  # Extract text
            print(text)

            start_point = text.find('"')
            end_point = text.find('"', start_point + 1)

            course_name = text[start_point + 1:end_point]
            course_name = ' '.join(course_name.split())

            check_if_certificado = text.find("no dia")
            check_if_diploma = text.find("no período de")

            if check_if_certificado != -1 or check_if_diploma != -1:
                doc_name = "Certificado.pdf"
            else:
                doc_name = "Historico.pdf"
            
            return course_name, doc_name

        document.close()
        
    except Exception as e:
        print(f"Error reading PDF file: {e}")
