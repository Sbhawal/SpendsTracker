from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from app.emailConnector import create_service
from app.Constants import *
# from app.conditionManager import *
from PyPDF2 import PdfReader, PdfWriter

def init_gmail_service(client_file=CLIENT_SECRET_FILE_PATH, api_name=API_NAME, api_version=API_VERSION, scopes=SCOPES):
    return create_service(client_file, api_name, api_version, scopes)

service = init_gmail_service()

def _extract_body(payload):
    body = '<Text body not available>'
    if 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'multipart/alternative':
                for subpart in part['parts']:
                    if subpart['mimeType'] == 'text/plain' and 'data' in subpart['body']:
                        body = base64.urlsafe_b64decode(subpart['body']['data']).decode('utf-8')
                        break
            elif part['mimeType'] == 'text/plain' and 'data' in part['body']:
                body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                break
    elif 'body' in payload and 'data' in payload['body']:
        body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
    return body


def get_email_messages(from_date=None, to_date=None, service=service, user_id='me', label_ids=None, folder_name='INBOX', max_results=5, ):
    messages = []
    next_page_token = None

    if folder_name:
        label_results = service.users().labels().list(userId=user_id).execute()
        labels = label_results.get('labels', [])
        folder_label_id = next((label['id'] for label in labels if label['name'].lower() == folder_name.lower()), None)
        if folder_label_id:
            if label_ids:
                label_ids.append(folder_label_id)
            else:
                label_ids = [folder_label_id]
        else:
            raise ValueError(f"Folder '{folder_name}' not found.")

    query = []
    if from_date:
        query.append(f'after:{from_date}')
    if to_date:
        query.append(f'before:{to_date}')
    query_string = ' '.join(query)
    print(f"Getting emails from {from_date} to {to_date}")

    while True:
        result = service.users().messages().list(
            userId=user_id,
            labelIds=label_ids,
            maxResults=min(500, max_results - len(messages)) if max_results else 500,
            pageToken=next_page_token,
            q=query_string
        ).execute()

        messages.extend(result.get('messages', []))

        next_page_token = result.get('nextPageToken')

        if not next_page_token or (max_results and len(messages) >= max_results):
            break

    return messages[:max_results] if max_results else messages


def get_email_message_details(service, msg_id):
    message = service.users().messages().get(userId='me', id=msg_id, format='full').execute()
    payload = message['payload']
    headers = payload.get('headers', [])

    subject = next((header['value'] for header in headers if header['name'].lower() == 'subject'), None)
    if not subject:
        subject = message.get('subject', 'No subject')

    sender = next((header['value'] for header in headers if header['name'] == 'From'), 'No sender')
    recipients = next((header['value'] for header in headers if header['name'] == 'To'), 'No recipients')
    snippet = message.get('snippet', 'No snippet')
    has_attachments = any(part.get('filename') for part in payload.get('parts', []) if part.get('filename'))
    date = next((header['value'] for header in headers if header['name'] == 'Date'), 'No date')
    star = message.get('labelIds', []).count('STARRED') > 0
    label = ', '.join(message.get('labelIds', []))

    body = _extract_body(payload)

    return {
        'subject': subject,
        'sender': sender,
        'recipients': recipients,
        'body': body,
        'snippet': snippet,
        'has_attachments': has_attachments,
        'date': date,
        'star': star,
        'label': label,
    }


def download_attachments_parent(service, user_id, msg_id, target_dir):
    message = service.users().messages().get(userId=user_id, id=msg_id).execute()
    for part in message['payload']['parts']:
        if part['filename']:
            att_id = part['body']['attachmentId']
            att = service.users().messages().attachments().get(userId=user_id, messageId=msg_id, id=att_id).execute()
            data = att['data']
            file_data = base64.urlsafe_b64decode(data.encode('UTF-8'))
            file_path = os.path.join(target_dir, part['filename'])
            # print('Saving attachment to:', file_path)
            with open(file_path, 'wb') as f:
                f.write(file_data)

def decryptPDF(PDF_PATH, PASS):
    if STORE_DECRYPTED_PDFS:
        reader = PdfReader(PDF_PATH)
        if reader.is_encrypted:
            reader.decrypt(PASS)
        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)
        with open(PDF_PATH, "wb") as output_file:
            writer.write(output_file)
    else:
        return
    
def download_attachments_all(msg_id, target_dir="", user_id="me", Prefix = None, service = service, PASS=None):
    thread = service.users().threads().get(userId=user_id, id=msg_id).execute()
    for message in thread['messages']:
        for part in message['payload']['parts']:
            if part['filename']:
                att_id = part['body']['attachmentId']
                att = service.users().messages().attachments().get(userId=user_id, messageId=message['id'], id=att_id).execute()
                data = att['data']
                file_data = base64.urlsafe_b64decode(data.encode('UTF-8'))
                if Prefix:
                    file_path = os.path.join(target_dir, Prefix+"_"+part['filename'])
                else:
                    file_path = os.path.join(target_dir, part['filename'])
                # print('Saving attachment to:', file_path)
                with open(file_path, 'wb') as f:
                    f.write(file_data)
                if PASS:
                    decryptPDF(file_path, PASS)


def create_label(name, background_color=None, text_color=None, label_list_visibility='labelShow', message_list_visibility='show',  service=service):
    label = {
        'name': name,
        'labelListVisibility': label_list_visibility,
        'messageListVisibility': message_list_visibility,
    }
    if background_color or text_color:
        label['color'] = {}
        if background_color:
            label['color']['backgroundColor'] = background_color
        if text_color:
            label['color']['textColor'] = text_color
    created_label = service.users().labels().create(userId='me', body=label).execute()
    return created_label

def list_labels(service=service):
    results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])
    return labels

def get_label_details(service, label_id):
    return service.users().labels().get(userId='me', id=label_id).execute()

def modify_label(service, label_id, **updates):
    label = service.users().labels().get(userId='me', id=label_id).execute()
    for key, value in updates.items():
        label[key] = value
    updated_label = service.users().labels().update(userId='me', id=label_id, body=label).execute()
    return updated_label

def delete_label(service, label_id):
    service.users().labels().delete(userId='me', id=label_id).execute()

def map_label_name_to_id(service, label_name):
    labels = list_labels(service)
    label = next((label for label in labels if label['name'] == label_name), None)
    return label['id'] if label else None

def modify_email_labels(service,  message_id, user_id='me', add_labels=None, remove_labels=None):
    def batch_labels(labels, batch_size=100):
        return [labels[i:i + batch_size] for i in range(0, len(labels), batch_size)]
    
    if add_labels:
        for batch in batch_labels(add_labels):
            service.users().messages().modify(
                userId=user_id,
                id=message_id,
                body={'addLabelIds': batch}
            ).execute()

    if remove_labels:
        for batch in batch_labels(remove_labels):
            service.users().messages().modify(
                userId=user_id,
                id=message_id,
                body={'removeLabelIds': batch}
            ).execute()


