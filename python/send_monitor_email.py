import smtplib 
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import time
import os
import os.path
import cfg

def send_email(): 
 reload(cfg) 
 os.system("make-monitor-plot %s %d" % (cfg.mon_file, cfg.mon_period)) 

 msg = MIMEMultipart() 
 me = os.environ["USER"] + "@" + os.environ["HOSTNAME"]  
 msg['From'] = me
 msg['To'] = cfg.email 
 msg['Subject'] = 'Daily NuPhase Monitoring Report' 

 the_file = open(cfg.mon_file)
 the_data = the_file.read() 
 the_file.close() 
 file_type = cfg.mon_file.split(".")[-1]; 
 attach = MIMEApplication(the_data, file_type); 
 attach.add_header('Content-Disposition', 'attachment', filename=os.path.basename(cfg.mon_file).replace(".%s" % (file_type,), "-%s.%s" % (time.strftime("%Y-%m-%d"), file_type)))
 msg.attach(attach); 
 smtplib.SMTP('localhost').sendmail(me,[cfg.email], msg.as_string())











  
    


  

