from app.emailDataBaseHandler import *
from app.LabelHandler import *
from datetime import datetime

labelMapping = create_Label_Map()

def return_Value_inside_Braces(CONDITION, PARAMETER):
    try:
        return CONDITION.split(f'{PARAMETER} {{')[1].split('}')[0].strip()
    except (IndexError, ValueError):
        return None

def build_SQL_Query_From_Conditions(CONDITION):
    subject_value = return_Value_inside_Braces(CONDITION, "SUBJECT")
    label_value = return_Value_inside_Braces(CONDITION, "LABEL")
    Has_Attachment = return_Value_inside_Braces(CONDITION, "ATTACHMENT") 
    if Has_Attachment:
        QUERY = f"SELECT * FROM emails WHERE SUBJECT LIKE '%{subject_value}%' AND LABEL NOT LIKE '%{label_value}%'"
    # QUERY = f"SELECT * FROM emails WHERE SUBJECT LIKE '%{subject_value}%'"
    return QUERY

def get_Rows_based_on_condition(CONDITION):
    QUERY = build_SQL_Query_From_Conditions(CONDITION)
    print(QUERY)
    conn, cursor = connectToDB()
    cursor.execute(QUERY)
    rows = cursor.fetchall()
    conn.close()    
    return rows 
    

def Process_Condition(CONDITION):
    subject_value = return_Value_inside_Braces(CONDITION, "SUBJECT")
    label_value = return_Value_inside_Braces(CONDITION, "LABEL")
    label_id = labelMapping[return_Value_inside_Braces(CONDITION, "LABEL")]
    Has_Attachment = return_Value_inside_Braces(CONDITION, "ATTACHMENT")
    rows = get_Rows_based_on_condition(CONDITION)
    for row in tqdm(rows):
        ID = row[0]
        SUBJECT = row[4]
        datetimeObj = datetime.strptime(row[2], "%a, %d %b %Y %H:%M:%S %z")
        Prefix = datetimeObj.strftime("%B_%y")
        if Has_Attachment == "True":
            PASS = return_Value_inside_Braces(CONDITION, "PASSWORD")
            Download_Folder = os.path.join(DOWNLOAD_FOLDER, label_value.replace("/","\\") )
            if not os.path.exists(Download_Folder):
                os.makedirs(Download_Folder)
            download_attachments_all(ID, target_dir=Download_Folder, Prefix=Prefix, PASS=PASS) 
        modify_email_labels(service, ID, add_labels=[label_id])   
