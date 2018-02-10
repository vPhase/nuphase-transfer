import smtplib 
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import time
import os
import os.path
import cfg

def send_email(): 
 reload(cfg) 
 os.system("make-monitor-plot %s %d" % (cfg.mon_pdf_file, cfg.mon_period)) 

 msg = MIMEMultipart() 
 me = os.environ["USER"] + "@" + os.environ["HOSTNAME"]  
 msg['From'] = me
 msg['To'] = cfg.email 
 msg['Subject'] = 'Daily NuPhase Monitoring Report' 

 pdf_file = open(cfg.mon_pdf_file)
 pdf_data = pdf_file.read() 
 pdf_file.close() 
 pdf_attach = MIMEApplication(pdf_data, 'pdf'); 
 pdf_attach.add_header('Content-Disposition', 'attachment', filename=os.path.basename(cfg.mon_pdf_file).replace(".pdf", "-%s.pdf" % (time.strftime("%Y-%m-%d"))))
 msg.attach(pdf_attach); 
 smtplib.SMTP('localhost').sendmail(me,[cfg.email], msg.as_string())











  
    


  

