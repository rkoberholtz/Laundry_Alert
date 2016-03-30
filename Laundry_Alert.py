import RPi.GPIO as GPIO
import time
from  django.template import Template, Context
from django.conf import settings
import sys

# WHY ARE THERE NO COMMENTS?!
# PLEASE ADD THEM!!!

def main():
	settings.configure()
	
	webpage = "/var/www/python.html"
	threshold = "30"
	avgnoise = 0	
	prev_normalized_noise = 0
	fromaddress = "laundry@rickelobe.com"
	toaddress = "7173421272@message.ting.com"	

	GPIO.setmode(GPIO.BCM)
	GPIO.setup(23, GPIO.IN)	
	
	while 1:
	
		samples = 0
		noise_sample = []
		normalized_noise = 0				

		while int(samples) <= 2:
		
			noise = []
			reset = 0
		
			while int(reset) <= 59:
				noise.append(GPIO.input(23))
				sys.stdout.write(str(noise[reset]))
				sys.stdout.flush()
				reset += 1
				time.sleep(.5)			
		
			avgnoise = (sum(noise))
		
			print ""
			print "Noise level: %d/%d" % (avgnoise, reset)
			
			noise_sample.append(avgnoise)
			
			samples += 1
		
		normalized_noise = (sum(noise_sample) /	len(noise_sample))
		print "Normalized Noise: %d" % normalized_noise
		print "Current tooNoisey result: %s" % tooNoisey(normalized_noise, threshold)
		print "Previous tooNoisey result: %s" % tooNoisey(prev_normalized_noise, threshold)
		
		if (tooNoisey(normalized_noise, threshold) and (tooNoisey(prev_normalized_noise, threshold))):
			skip = True
		elif ((tooNoisey(normalized_noise, threshold) == False) and (tooNoisey(prev_normalized_noise, threshold) == False)):
			skip = True
		else:
			skip = False
		
		print "Are we skipping the alert/webpage update: %s" % str(skip)
		
		if tooNoisey(normalized_noise, threshold) and not skip:
			print "----          Laundry is IN USE             ----"
			print "--Updating status page and sending email alert--"
			publishWebpage(webpage, 'red', 'IN USE')
			sendEmail(fromaddress, toaddress, 'Laundry is IN USE')
		elif not tooNoisey(normalized_noise, threshold) and not skip:
			print "----         Laundry is AVAILABLE          ----"
			print "--Updating status page and sengin email alert--"
			publishWebpage(webpage, 'green', 'AVAILABLE')
			sendEmail(fromaddress, toaddress, 'Laundry is AVAILABLE')		
		
		prev_normalized_noise = normalized_noise

def tooNoisey(noise, threshold):
	if int(noise) >= int(threshold):
		return True
	if int(noise) < int(threshold):
		return False

def sendEmail(me, to, msg):
	import smtplib	
	from email.mime.text import MIMEText

	msg = MIMEText(msg)
	msg['Subject'] = ''
	msg['From'] = me
	msg['To'] = to
	s = smtplib.SMTP('localhost')
	s.sendmail(me, [to], msg.as_string())
	s.quit()		


def publishWebpage(htmlfile, color, status):

	f = open("/home/pi/template.conf",'r')
	template = f.read()
	f.close()
	t = Template(template)
	context = Context({"color": color, "status": status})
	
	newpage = t.render(context)
	
	f = open(htmlfile,'w')
	f.write(newpage)
	f.close()

if __name__ == "__main__":
	main()
