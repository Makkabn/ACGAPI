from flask import Flask, jsonify, request, render_template
import jinja2
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError
from email.mime.text import MIMEText
import base64

app = Flask(__name__)
# If modifying these scopes, delete the file token.pickle.
#SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
SCOPES = ['https://mail.google.com/']

"""
Lista a lista de marcadores no Gmail do usuário.
"""
creds = None
# O arquivo token.pickle armazena os tokens de acesso do usuário, e é
# criado automaticamente quando o processo de autenticação é completado
# pela primeira vez.
if os.path.exists('token.pickle'):
    with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)
# Se não existirem  credenciais válidas, pede pro usuário se logar.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
         creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    # Salva as credenciais para a próxima vez.
    with open('token.pickle', 'wb') as token:
        pickle.dump(creds, token)

service = build('gmail', 'v1', credentials=creds)

# Chamada da API Gmail
results = service.users().labels().list(userId='me').execute()
labels = results.get('labels', [])

if not labels:
    print('Nenhum marcador encontrado')
else:
    print('Marcadores:')
    for label in labels:
        print(label['name'])

@app.route('/', methods = ['GET','POST'])
def envia_mensagem():
    """
    Args:
        de: Email de quem está enviando. O valor 'me' pode ser usado, representando
        o usuário autenticado no começo.
        para: Email de quem vai receber.
        assunto: O assunto da mensagem.
        texto: O corpo da mensagem.

    Retorna um objeto contendo um 'base64url encoded email object'.
    """
    if request.method == 'GET':
        return render_template('index.html')

    de = 'me'
    para = request.form["para"]
    assunto = request.form["assunto"]
    texto = request.form["texto"]
    message = MIMEText(texto)
    message['to'] = para
    message['from'] = de
    message['subject'] = assunto

    
    raw = base64.urlsafe_b64encode(message.as_bytes())
    raw = raw.decode()
    corpo = {'raw': raw}
    

    
    try:
        message = (service.users().messages().send(userId=de, body=corpo).execute())
        print ('Id da mensagem: %s' % message['id'])
        sucesso = True
        title = 'Mensagem Enviada!'
        return render_template("resultado.html", title = title, sucesso = sucesso)
    except Exception as error:
        print('Um erro ocorreu: %s' % error)
        sucesso =  False
        title = 'Erro'
        return render_template("resultado.html", erro = error, title = title, sucesso= sucesso)
    


if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=True)
