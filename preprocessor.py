import re
import pandas as pd

def preprocess(data):
    if re.search(r"\d{2}/\d{2}/\d{2}, \d{2}:\d{2} -", data[:20]):
        pattern = r"\d{2}/\d{2}/\d{2}, \d{2}:\d{2} -"
    elif re.search(r'\d{2}/\d{2}/\d{2}, \d{1,2}:\d{2} [apAP][mM] -', data[:20]):
        pattern = r'\d{2}/\d{2}/\d{2}, \d{1,2}:\d{2} [apAP][mM] -'
    elif re.search(r'\d{1,2}/\d{1,2}/\d{2}, \d{1,2}:\d{2}\s*[aApP][mM]\s*-', data[:20]):
        pattern = r'\d{1,2}/\d{1,2}/\d{2}, \d{1,2}:\d{2}\s*[aApP][mM]\s*-'
    else:
        pattern = None
    messages = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)
    lst = []
    for i in dates:
        new_date = re.sub(r'\u202f', ' ', i)
        lst.append(new_date)
    dates = lst
    df = pd.DataFrame({'message':messages, 'date':dates})
    if re.search(r'\d{2}/\d{2}/\d{2}, \d{1,2}:\d{2} [apAP][mM] -', df['date'][0]):
        df['date'] = pd.to_datetime(df['date'], format= "%d/%m/%y, %I:%M %p -")
    elif re.search(r'\d{1,2}/\d{1,2}/\d{2}, \d{1,2}:\d{2}\s*[aApP][mM]\s*-', df['date'][0]):
        df['date'] = pd.to_datetime(df['date'], format= "%m/%d/%y, %I:%M %p -")
    else:
        df['date'] = pd.to_datetime(df['date'], format= "%d/%m/%y, %H:%M -")
    name = []
    message = []
    for i in df['message']:
        if ':' in i:
            name.append(i.split(':',1)[0])
            message.append(i.split(':',1)[1])
        else:
            name.append('Group notification')
            message.append(i)

    df = pd.DataFrame({'date':df['date'], 'user':name, 'message': message})
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month_name()
    df['month_num'] = df['date'].dt.month
    df['day'] = df['date'].dt.day
    df['weekday'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute
    df['just_date'] = df['date'].dt.date    
    df['message'] = df['message'].str.strip()
    df = df[(df['message']!='Nudge!') & (df['message']!='Sent you a sticker') & (df['message']!='File transfer of type IMAGE')& (df['message']!='Sticker')]

    bucket= []
    for i in df['hour']:
        if i == 23:
            bucket.append(str(i) + '-' + str('00'))
        elif i == 0:
            bucket.append(str('00') + '-' + str(i + 1))
        else:
            bucket.append(str(i) + '-' + str(i+1))
    df['time_bucket'] = bucket 
    return df
    
