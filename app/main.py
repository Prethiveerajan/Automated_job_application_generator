
import streamlit as st
import smtplib
import pandas as pd
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from langchain_community.document_loaders import WebBaseLoader
from chains import Chain
from portfolio import Portfolio
from utils import clean_text

# Email Sending Function
def send_email(to_email, subject, body):
    sender_email = "raj0105200@gmail.com"  
    sender_password = "uuty mqch lxyb lkib"       

    try:
        # Create email message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # Set up SMTP server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Error sending email to {to_email}: {e}")
        return False

def create_streamlit_app(llm, portfolio, clean_text):
    st.title("📧 Targeted Mail Sender for recruiter")

    # Input for job URL and company name
    url_input = st.text_input("Enter a Job URL:", value="https://www.hcltech.com/jobs/technical-lead-12")
    company_name = st.text_input("Enter the Target Company Name:", value="HCL")
    submit_button = st.button("Generate and Send Emails")

    if submit_button:
        try:
            # Load job details from URL
            loader = WebBaseLoader([url_input])
            data = clean_text(loader.load().pop().page_content)
            portfolio.load_portfolio()
            jobs = llm.extract_jobs(data)

            # Load HR list from CSV and filter by company name
            hr_list = pd.read_csv("resource/Hr_list.csv")
            filtered_hr_list = hr_list[hr_list['Company'].str.contains(company_name, case=False, na=False)]

            if filtered_hr_list.empty:
                st.warning(f"No HR contacts found for company: {company_name}")
                return

            for job in jobs:
                skills = job.get('skills', [])
                links = portfolio.query_links(skills)
                email_body = llm.write_mail(job, links)

                for _, hr in filtered_hr_list.iterrows():
                    hr_name = hr['Name']
                    hr_email = hr['Email']
                    hr_location = hr['Location']

                    subject = f"Regarding {job['role']} at {company_name}"
                    personalized_email = email_body.replace("Dear Sir/Madam", f"Dear {hr_name}")

                    # Send email
                    if send_email(hr_email, subject, personalized_email):
                        st.success(f"Email sent to {hr_name} ({hr_email})")
                    else:
                        st.error(f"Failed to send email to {hr_name} ({hr_email})")
        except Exception as e:
            st.error(f"An error occurred: {e}")


if __name__ == "__main__":
    chain = Chain()
    portfolio = Portfolio()
    st.set_page_config(layout="wide", page_title="Targeted Mail Sender for recruiter", page_icon="📧")
    create_streamlit_app(chain, portfolio, clean_text)