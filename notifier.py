import requests
from pygame import mixer 
from datetime import datetime, timedelta
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import getpass
import os
from os import path
import json


def play_sound():
    mixer.init()
    mixer.music.load('notify_sound.wav') 
    mixer.music.play()


def add_result_file(content):
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    with open('result.txt',"a") as f:
        f.write(content)
        f.write(f"refreshed on : {current_time}")
     

def send_mail(content,config_data):
    mail_content = 'Hello, \n The vaccine slots available in your area, Check all the available slots in you area below..\n'+content+'Thankyou'
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    mail_content+=("\n Refreshed at "+ current_time)
    #The mail addresses and password
    sender_address = config_data["email_sender"]
    sender_pass = config_data["password"]
    receiver_address = config_data["email_receiver"]
    #Setup the MIME
    message = MIMEMultipart()
    message['From'] = sender_address
    message['To'] = receiver_address
    message['Subject'] = 'Vaccination Slot Notifier : Slot Available'   #The subject line
    #The body and the attachments for the mail
    message.attach(MIMEText(mail_content, 'plain'))
    #Create SMTP session for sending the mail
    session = smtplib.SMTP('smtp.gmail.com', 587) #use gmail with port
    session.starttls() #enable security
    session.login(sender_address, sender_pass) #login with mail_id and password
    text = message.as_string()
    session.sendmail(sender_address, receiver_address, text)
    session.quit()
    print('Mail Sent')




def main():
    print('====================================================')
    print('-------------Vaccine Slot Notifier------------------')
    print('====================================================')

    file=open('config.json')
    config_data=json.load(file)
    age = config_data["age"]
    pincodes = config_data["pincodes"]
    num_days = config_data['number_of_days']
    
    print_flag = 'Y'

    print("Starting the vaccine slot Notifier........")

    actual = datetime.today()
    list_format = [actual + timedelta(days=i) for i in range(num_days)]
    actual_dates = [i.strftime("%d-%m-%Y") for i in list_format]

    while True:
        counter = 0
        for pincode in pincodes:    
            for given_date in actual_dates:

                URL = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByPin?pincode={}&date={}".format(pincode, given_date)
                header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'} 
                
                api_result = requests.get(URL, headers=header)
                mail_content=""
                if api_result.ok:
                    response_json = api_result.json()
                    if response_json["centers"]:
                        if(print_flag.lower() =='y'):
                            for center in response_json["centers"]:
                                for session in center["sessions"]:
                                    slot_result=""
                                    if (session["min_age_limit"] <= age and session["available_capacity"] > 0 ) :
                                        
                                        slot_result+=('Pincode: ' + str(pincode)+"\n")
                                        slot_result+=(f'Available on: {given_date}'+"\n")
                                        slot_result+=("\t"+ center["name"]+"\n")
                                        slot_result+=("\t"+ center["block_name"]+"n")
                                        slot_result+=("\t Price: "+center["fee_type"]+"\n")
                                        slot_result+=("\t Availablity : "+ str(session["available_capacity"])+"\n")
                                        if(session["vaccine"] != ''):
                                            slot_result+=("\t Vaccine type: "+session["vaccine"]+"\n")
                                        slot_result+="\n"
                                        mail_content+=slot_result
                                        counter = counter + 1
                                                            
                else:
                    print("No Response!")
                    
        if counter<1:
            print("No Vaccination slot available!")
        else:   
            send_mail(mail_content,config_data)
            play_sound()
            add_result_file(mail_content)
            print("Search Completed!")
            print('Refreshing the system...')
            print("System will check again slot availablity after 30 Minutes..")


        dt = datetime.now() + timedelta(minutes=30)

        while datetime.now() < dt:
            time.sleep(1)
        

if __name__ == "__main__":
    main()