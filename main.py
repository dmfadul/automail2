import credentials
import funcs


doc_name = "Certificado.pdf"  # Certificado.pdf ou Historico.pdf

# curso = "OPERADOR DE PISTOLA BERETTA APX"  # Nome do curso que será enviado no assunto
curso = "CURSO DE EXTENSÃO PARA HABILITAÇÃO NO MANUSEIO DE ARMA LONGA - FUZIL"
# curso = "CICLO DE PALESTRAS - PALESTRA ALUSIVA AO DIA DA MULHER"
# curso = "CICLO DE PALESTRAS - POLÍTICAS DE ATENDIMENTO SOCIOEDUCATIVAS NO ESTADO DO PARANÁ"
# curso = "CURSO DE ATENDIMENTO PRÉ-HOSPITALAR EM COMBATE"
# curso = "CURSO DE PRIMEIROS SOCORROS E SUPORTE BÁSICO À VIDA"
# curso = "CURSO DE PREVENÇÃO E COMBATE À INCÊNDIO"
# curso = "CURSO DE TÉCNICAS E PROCEDIMENTOS DE ARMA DE FOGO COM USO DE SIMULADOR DE TIRO"
# curso = "CURSO AVANÇADO DE PADRONIZAÇÃO DE PROCEDIMENTOS NA PCPR - INVESTIGAÇÃO DE CRIMES CONTRA A VIDA"


class_name = None
# class_name = "CRIMES-VIDA"  # add if sending is interrupted

subject_text = "Certidão de Conclusão de Curso - "
main_text = ''

# funcs.multi_send(
#                 doc_name=doc_name,
#                 curso=curso,
#                 subject_text=subject_text,
#                 main_text=main_text,
#                 login=credentials.login,
#                 passwd=credentials.passwd,
#                 c_name=class_name
#                 )

# the email creation is omitting the last entry --> seems to be working fine.

import utils

utils.get_course_name()