import RPi.GPIO as GPIO
import time
from  django.template import Template, Context
from django.conf import settings
import sys

# WHY ARE THERE NO COMMENTS?!
# PLEASE ADD THEM!!!

def main():
	settings.configure()
	
	# Setting Variable Defaults
    # Some of these should be available as cmd line options
	webpage = "/var/www/python.html"
	threshold = "30"
	avgnoise = 0	
	prev_normalized_noise = 0
	fromaddress = "laundry@rickelobe.com"
	toaddress = "7173421272@message.ting.com"	

	# Setting up Raspberry Pi GPIO pins
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(23, GPIO.IN)	
	
	# Loop Forever!
	while 1:
	
		# Setting variable defaults prior to gathering noise samples from Microphone
		samples = 0
		noise_sample = []
		normalized_noise = 0				

		# Gather 3 sets of 60 samples, 1 sample every 500ms from microphone
		while int(samples) <= 2:
		
			# Setting variable defaults
			noise = []
			reset = 0
		
			# Get 60 samples of noise data (1/0 = yes/no)
			while int(reset) <= 59:
				# Append current noise sample value (either 1 or 0) to list from GPIO pin #23
				noise.append(GPIO.input(23))
				# Write out current value
				sys.stdout.write(str(noise[reset]))
				sys.stdout.flush()
				# Increment the Counter
				reset += 1
				#Pause for 500 milliseconds
				time.sleep(.5)			
		
			# Sum the list of sample values
			avgnoise = (sum(noise))
		
			# Write out the SUM of the values
			print ""
			print "Noise level: %d/%d" % (avgnoise, reset)
			
			# Append the sum of values to the sample list
			noise_sample.append(avgnoise)
			
			# Increment the sample counter
			samples += 1
		
		# Get the average number or noisey samples (SUM of values divided by number of samples)
		normalized_noise = (sum(noise_sample) /	len(noise_sample))
		
		# Write out the information gathered
		print "Normalized Noise: %d" % normalized_noise
		print "Current tooNoisey result: %s" % tooNoisey(normalized_noise, threshold)
		print "Previous tooNoisey result: %s" % tooNoisey(prev_normalized_noise, threshold)
		
		# Determine whether the state has change from the last set of samples
        # if the state change, we need to send alerts, update webpage, etc
        # if not, do nothing
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
		
		# The current normalized vaule is now the previous value
		prev_normalized_noise = normalized_noise

# This function determines if the current noise level is higher than the set threshold
def tooNoisey(noise, threshold):
	if int(noise) >= int(threshold):
		return True
	if int(noise) < int(threshold):
		return False

#This function sends an email to the address specified with the supplies message
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
