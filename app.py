import pandas as pd
import streamlit as st
import preprocessor
import Functions
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from collections import Counter

# Set page config
st.set_page_config(page_title="WhatsApp Chat Analyser", 
                   page_icon="💬", layout="wide", initial_sidebar_state="collapsed")

# Custom CSS for styling
st.markdown("""
    <style>
    .css-18e3th9 {
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    .css-1d391kg {
        background-color: #f9f9f9;
        border-radius: 10px;
        padding: 1rem;
    }
    .stTitle {
        color: #444;
        text-align: center;
        font-weight: bold;
    }
    .stHeader {
        text-align: center;
    }
    .footer {
        font-size: 12px;
        text-align: center;
        margin-top: 20px;
        color: #444;
        position: fixed;
        bottom: 0;
        width: 100%;
        background-color: transparent; /* Transparent background */
        padding: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

# Main title with emoji
st.title("💬 WhatsApp Chat Analyser")
st.markdown("<hr>", unsafe_allow_html=True)

# File uploader section
st.write("## 📂 Upload WhatsApp Chat File")
st.markdown("""
    <p style="text-align: center;">
    Drag and drop your WhatsApp chat export (without media) below to start analyzing!
    </p>""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("", type="txt", label_visibility='collapsed')
st.write("[How to export your WhatsApp chat](https://faq.whatsapp.com/1180414079177245/?locale=en_US&cms_platform=android)")

# Proceed if a file is uploaded
if uploaded_file is not None:
    # Progress bar for loading the chat
    st.write("⏳ Processing chat, please wait...")
    with st.spinner('Reading data...'):
        bytes_data = uploaded_file.getvalue()
        data = bytes_data.decode("UTF-8")
        df = preprocessor.preprocess(data)

    # Fetch user list and add selectbox
    users = df['user'].unique().tolist()
    if 'Group notification' in users:
        users.remove('Group notification')
    users.sort()
    users.insert(0, 'Including all')

    # Display user selection dropdown directly on the page
    selected_user = st.selectbox("🔍 Select User for Analysis", users)

    # Analysis button
    if st.button('Show Analysis'):
        st.markdown("<hr>", unsafe_allow_html=True)
        
        # Statistics Section
        st.write("## 📝 Statistics Overview")
        num_messages, length, media_attached, tot_urls = Functions.fetch_stats(selected_user, df)

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("📄 Total Messages", num_messages)
        col2.metric("📝 Total Words", length)
        col3.metric("🖼️ Media Files", media_attached)
        col4.metric("🔗 Total URLs", tot_urls)

        # Most active users (only for group chats)
        if selected_user == 'Including all':
            st.markdown("<hr>", unsafe_allow_html=True)
            st.write("## 👥 Most Active Users")
            most_active, act_df = Functions.most_active_users(df)
            fig, ax = plt.subplots()
            col1, col2 = st.columns(2)

            with col1:
                ax.bar(most_active.index, most_active.values, color='green')
                plt.xticks(rotation='vertical')
                st.pyplot(fig)
            with col2:
                st.dataframe(act_df)

        # Word Cloud Section
        st.markdown("<hr>", unsafe_allow_html=True)
        st.write("## ☁️ Word Cloud")
        df_wc = Functions.word_cloud(selected_user, df)
        fig, ax = plt.subplots()
        ax.imshow(df_wc)
        st.pyplot(fig)

        # Most common words
        st.markdown("<hr>", unsafe_allow_html=True)
        st.write("## 🔤 Most Common Words")
        temp = df if selected_user == "Including all" else df[df['user'] == selected_user]
        temp = temp[(temp['message'] != '<Media omitted>') & (temp['message'] != 'This message was deleted')]
        temp['cleaned_message'] = temp['message'].apply(Functions.remove_stopwords)
        
        words = []
        for m in temp['cleaned_message']:
            words.extend(m.split())
        
        df_word_freq = pd.DataFrame(Counter(words).most_common(20), columns=['Word', 'Frequency'])
        fig, ax = plt.subplots()
        plt.barh(df_word_freq['Word'], df_word_freq['Frequency'], color='blue')
        plt.gca().invert_yaxis()
        st.pyplot(fig)

        # Emoji analysis
        st.markdown("<hr>", unsafe_allow_html=True)
        st.write("## 😊 Emoji Analysis")
        emoji_df = Functions.emoji_analysis(selected_user, df)
        col1, col2 = st.columns(2)

        with col1:
            st.dataframe(emoji_df)
        with col2:
            fig, ax = plt.subplots()
            ax.pie(emoji_df['Count'].head(10), labels=emoji_df['Emoji'].head(10), autopct="%0.2f")
            st.pyplot(fig)

        # Monthly timeline
        st.markdown("<hr>", unsafe_allow_html=True)
        st.write("## 📅 Monthly Message Timeline")
        timeline = Functions.timeline_monthly(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(timeline['time'], timeline['message'], color='#FF5733')
        plt.xticks(rotation='vertical', fontsize=8, ticks=range(0, len(timeline['time']), 2))
        st.pyplot(fig)

        # Daily timeline
        st.write("## 🗓️ Daily Message Timeline")
        df_daily = Functions.timeline_daily(selected_user, df)
        fig, ax = plt.subplots(figsize=(18, 10))
        ax.plot(df_daily['just_date'], df_daily['message'], color='#33C9FF')
        ax.set_xticklabels(ax.get_xticks(), rotation='vertical', fontsize=15)
        date_format = mdates.DateFormatter('%d-%b-%Y')
        ax.xaxis.set_major_formatter(date_format)
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        st.pyplot(fig)

        # Busy days and months
        st.markdown("<hr>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.write("### 📆 Busy Days")
            busy_days = Functions.busy_days(selected_user, df)
            fig, ax = plt.subplots()
            plt.xticks(rotation='vertical')
            ax.bar(busy_days.index, busy_days.values, color='#FFA07A')
            st.pyplot(fig)
        with col2:
            st.write("### 📅 Busy Months")
            busy_months = Functions.busy_month(selected_user, df)
            fig, ax = plt.subplots()
            plt.xticks(rotation='vertical')
            ax.bar(busy_months.index, busy_months.values, color='#FFB6C1')
            st.pyplot(fig)

        # Active hours
        st.markdown("<hr>", unsafe_allow_html=True)
        st.write("## 🕒 Active Hours Heatmap")
        pivot_t = Functions.active_hours(selected_user, df)
        fig, ax = plt.subplots(figsize=(20, 6))
        sns.heatmap(pivot_t.fillna(0), cmap="coolwarm", ax=ax)
        st.pyplot(fig)

        # Sentiment analysis with progress bar
        st.markdown("<hr>", unsafe_allow_html=True)
        st.write("## ❤️ Sentiment Analysis of English Chats")

        # Initialize progress bar and status
        progress_bar = st.progress(0)
        status_text = st.empty()

        # Dummy breakdown of the sentiment analysis process
        progress = 0

        # Step 1: Preprocess data (simulate this step taking time)
        status_text.text("Preprocessing data...")
        en_df = Functions.readydf(selected_user, df)
        progress += 30
        progress_bar.progress(progress)  # Update progress after preprocessing

        # Step 2: Analyze sentiments (another chunk of work)
        status_text.text("Analyzing sentiments...")
        sentiment_counts = en_df['sentiment_category'].value_counts()
        progress += 50
        progress_bar.progress(progress)  # Update progress after sentiment analysis

        # Step 3: Visualize results
        status_text.text("Generating results...")
        fig, ax = plt.subplots()
        ax.pie(sentiment_counts, labels=sentiment_counts.index, autopct='%1.1f%%', startangle=90, colors=['#66b3ff', '#99ff99', '#ffcc99'])
        ax.set_aspect('equal')
        ax.set_title('Sentiment Distribution')
        progress += 20
        progress_bar.progress(progress)  
        
        # Show final visualization and remove progress bar
        st.pyplot(fig)
        progress_bar.empty()
        status_text.text("Sentiment analysis completed successfully!")

# Add footer
st.markdown("""
    <div class="footer">
    Built by Vipul Jadhav | Data Science & Engineering
    </div>
""", unsafe_allow_html=True)
