import funcs

subject_text = "Certidão de Conclusão de Curso - "
main_text = 'Boa tarde, segue o certificado retificado referente à palestra sobre Desafios Operacionais no Combate ao Crime Organizado. Pedimos que desconsiderem o certificado anterior, tendo em vista que o curso e a carga horária estavam incorrretos.'


funcs.multi_send(subject_text=subject_text, main_text=main_text, restart=False)
