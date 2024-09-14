import re
from wordcloud import WordCloud
import pandas as pd
from string import punctuation
from collections import Counter
from langdetect import detect
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from afinn import Afinn

def fetch_stats(selected_user, df):
    if selected_user == "Including all":
        # fetch total nums of messages
        num_messages = df.shape[0]

        # fetch total words
        words = []
        for message in df['message']:
            words.extend(message.split())
        length = len(words)

        # fetch total number of media attached
        media_attached = df[df['message']=="<Media omitted>"].shape[0]

        # fetch number of urls
        url_list = []
        for message in df['message']:
            url_pattern = r'(https?://[^\s]+)'
            urls = re.findall(url_pattern, message)
            url_list.extend(urls)
        tot_urls = len(url_list)
        return num_messages, length, media_attached, tot_urls
    else:
        # fetch total nums of messages
        new_df= df[df['user'] == selected_user]
        num_messages = new_df.shape[0]
          
        # fetch total words
        words = []
        for message in new_df['message']:
            words.extend(message.split())
        length = len(words)

        # fetch total number of media attached
        media_attached = new_df[new_df['message']=="<Media omitted>"].shape[0]

        # fetch number of urls
        url_list = []
        for message in new_df['message']:
            url_pattern = r'(https?://[^\s]+)'
            urls = re.findall(url_pattern, message)
            url_list.extend(urls)
        tot_urls = len(url_list)
        return num_messages, length, media_attached, tot_urls
        
# find most active users
def most_active_users(df):
    most_active= df['user'].value_counts().head(10)
    act_df = round(df['user'].value_counts(normalize = True)*100,2).reset_index().rename(columns={'index':'Name', 'user':'Percent'})
    return most_active, act_df  


# remove stopwords

with open('stopwords.txt', 'r', encoding='utf-8') as file:
    stop_words = list(set(file.read().split()))
def remove_stopwords(text):
    # Remove numbers
    text = re.sub(r'\d+', '', text)
    # Remove punctuation
    text = re.sub(r'[^\w\s]', '', text)
    words = text.split()  # Split the text into words
    filtered_words = [word for word in words if word.lower().strip() not in set(stop_words)]  # Remove stop words
    return ' '.join(filtered_words)

# Create wordcloud
def word_cloud(selected_user, df):
    if selected_user != "Including all":
        df = df[(df['user'] == selected_user)&(df['message']!='<Media omitted>')&(df['message']!='Nudge!')]
    df = df[df['message']!='<Media omitted>']
    wc = WordCloud(width=500, height=500, min_font_size=10, background_color= 'white')
    df['cleaned_message'] = df['message'].apply(remove_stopwords)
    df_wc = wc.generate(df['cleaned_message'].str.cat(sep = " "))
    return df_wc



# emoji analysis

def emoji_analysis(selected_user, df):
    # Filter DataFrame based on selected_user and message content
    if selected_user != "Including all":
        df = df[(df['user'] == selected_user) & (df['message'] != '<Media omitted>')]

    # Define regex pattern to match individual emojis
    emoji_pattern = re.compile(
        u'['
        u'\U0001F600-\U0001F64F'  # Emoticons
        u'\U0001F300-\U0001F5FF'  # Symbols & Pictographs
        u'\U0001F680-\U0001F6FF'  # Transport & Map Symbols
        u'\U0001F700-\U0001F77F'  # Alchemical Symbols
        u'\U0001F780-\U0001F7FF'  # Geometric Shapes Extended
        u'\U0001F800-\U0001F8FF'  # Supplemental Arrows-C
        u'\U0001F900-\U0001F9FF'  # Supplemental Symbols and Pictographs
        u'\U0001FA00-\U0001FA6F'  # Chess Symbols
        u'\U0001FA70-\U0001FAFF'  # Symbols and Pictographs Extended-A
        u'\U00002702-\U000027B0'  # Dingbats
        u'\U000024C2-\U0001F251'  # Enclosed Characters
        u']+', re.UNICODE)

    # Function to extract and count individual emojis
    def extract_individual_emojis(text):
        # Find all emoji sequences in the text
        emoji_sequences = emoji_pattern.findall(text)
        # Split each sequence into individual emojis
        individual_emojis = []
        for sequence in emoji_sequences:
            individual_emojis.extend(list(sequence))  # Split sequence into individual emojis
        return individual_emojis

    # Extract and count emojis from the DataFrame
    emojis = []
    for message in df['message']:
        emojis.extend(extract_individual_emojis(message))

    # Count occurrences of each individual emoji
    emoji_counts = Counter(emojis)
    
    # Create DataFrame with individual emojis and their counts
    emoji_df = pd.DataFrame(emoji_counts.items(), columns=['Emoji', 'Count'])
    emoji_df = emoji_df.sort_values(by='Count', ascending=False).reset_index(drop=True)
    
    return emoji_df


## monthly message frequency
def timeline_monthly(selected_user, df):
    if selected_user != "Including all":
        df = df[df['user'] == selected_user]
    timeline = df.groupby(['year', 'month_num', 'month'])['message'].count().reset_index()
    time = []
    for i in range(timeline.shape[0]):
        time.append((timeline['month'][i] + '-' + str(timeline['year'][i])))
    timeline['time'] = time
    return timeline

## Daily message frequency

def timeline_daily(selected_user, df):
    if selected_user != "Including all":
        df = df[df['user'] == selected_user]
    df_daily = df.groupby('just_date').count()['message'].reset_index()
    return df_daily

## busy days

def busy_days(selected_user, df):
    if selected_user != "Including all":
        df = df[df['user'] == selected_user]
    return df['weekday'].value_counts()

## busy months

def busy_month(selected_user, df):
    if selected_user != "Including all":
        df = df[df['user'] == selected_user]
    return df['month'].value_counts()

## Acitve hours

def active_hours(selected_user, df):
    if selected_user != "Including all":
        df = df[df['user'] == selected_user]
    pivot_t = df.pivot_table(index = 'weekday', columns= 'time_bucket', values= 'message', aggfunc= 'count').fillna(0)
    return pivot_t   

## English Sentiment Analysis

def readydf(selected_user, df):
    if selected_user != "Including all":
        df = df[df['user'] == selected_user]

    url_pattern = r'(https?://[^\s]+)'
    emoji_pattern = re.compile(
        u'['
        u'\U0001F600-\U0001F64F'  # Emoticons
        u'\U0001F300-\U0001F5FF'  # Symbols & Pictographs
        u'\U0001F680-\U0001F6FF'  # Transport & Map Symbols
        u'\U0001F700-\U0001F77F'  # Alchemical Symbols
        u'\U0001F780-\U0001F7FF'  # Geometric Shapes Extended
        u'\U0001F800-\U0001F8FF'  # Supplemental Arrows-C
        u'\U0001F900-\U0001F9FF'  # Supplemental Symbols and Pictographs
        u'\U0001FA00-\U0001FA6F'  # Chess Symbols
        u'\U0001FA70-\U0001FAFF'  # Symbols and Pictographs Extended-A
        u'\U00002702-\U000027B0'  # Dingbats
        u'\U000024C2-\U0001F251'  # Enclosed Characters
        u']+', re.UNICODE)
    number_pattern = re.compile(r'\d+')
    punctuation_pattern = f"[{re.escape(punctuation)}]"
    
    def clean_text(text):
        text = re.sub(url_pattern, '', text)  # Remove URLs
        text = emoji_pattern.sub(r'', text)   # Remove Emojis
        text = re.sub(number_pattern, '', text)  # Remove numbers
        text = re.sub(punctuation_pattern, '', text)  # Remove punctuation
        return text
    
    df = df[(df['user'] != 'Group notification') & (df['message'] != '<Media omitted>') & (df['message'] != 'This message was deleted')]
    df['message'] = df['message'].str.replace('\u200d', '')
    df['message'] = df['message'].apply(clean_text)
    df = df[df['message'].str.strip().astype(bool)]  # Ensure non-empty messages
    df = df.dropna(subset=['message'])

    # Filter messages that are non-empty after cleaning
    df2 = df[df['message'].str.strip().astype(bool)][['message', 'user']]
    
    lang = []
    for text in df2['message']:
        if len(text.strip()) > 0:  # Only detect if the message is not empty
            try:
                language = detect(text)
                lang.append(language)
            except:
                lang.append("unknown")  # Handle detection errors gracefully
        else:
            lang.append("unknown")  # For empty or invalid messages
    df2['language'] = lang

    # Filter English messages
    en_df = df2[df2['language'] == 'en']

    def preprocessing(text):
        lemmatizer = WordNetLemmatizer()
        review = re.sub('[^a-zA-Z]', ' ', text)
        review = review.lower()
        review = review.split()

        nltk.download('stopwords')

        review = [lemmatizer.lemmatize(word) for word in review if not word in set(stopwords.words('english'))]
        return ' '.join(review)
    
    en_df['prep_msg'] = en_df['message'].apply(preprocessing)
    
    # Sentiment analysis
    af = Afinn()
    lst_score = []
    for i in en_df['prep_msg']:
        score = af.score(i)
        lst_score.append(score)
    
    sentiment_category = ['positive' if score > 0 
                          else 'negative' if score < 0 
                          else 'neutral' 
                          for score in lst_score]
    en_df['sentiment_category'] = sentiment_category

    return en_df



    








