"""What I need to work on:

    -Putting parameters within the average, highest, lowest, etc. function.
        I have them written to say density or tech rating. I want it to be variable
    -Is there a way to add a way to input emails if you what?
        -The default=0 thing could be modified to if 
    -Making this less crowded...
    -How do I put a heading on the program within bash
        -Similar to how the ArgParser allows you to have an intro title
    -Easy way to print the percentage sign...
    -The rankings command does not work for tech rating
    -Is there a way to show a school's ranking in sql? Row number?

    -Talk about storyboarding outline

    -Work on formatting the ranking output

    """
import SightlinesClasses
import argparse
import psycopg2
import csv
import smtplib
import getpass
import clize
from sigtools.modifiers import kwoargs, annotate
import mimetypes
from email.mime.multipart import MIMEMultipart
from email import encoders
from email.message import Message
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.text import MIMEText



commands = []
def command(f):
    commands.append(f)
    return f


connection = psycopg2.connect(database="slschools") #keep this out of main

def main():
	
    parser = argparse.ArgumentParser(description="A useful tool for Sightlines employees") #create an instance of the ArgumentParser module from argparse
    subparsers = parser.add_subparsers(dest="command", help="--Available Commands--") #Allows you to use multiple subparsers
        
    arguments = parser.parse_args()  #parse_args also splits a list of arguments in named variables that we can use later
    arguments = vars(arguments) #Converts the namespace directory into a dictionary
    command = arguments.pop("command")#removes and returns command item added earlier

@command
@annotate(output='o', email='e', outputpeers = 'p', emaildoc = 'd', rankings = '-r') #bottom10 = "b")
@kwoargs("output", "email", "outputpeers", "emaildoc","rankings")#, "bottom10") #keyword only arguemnts #Can I elimiate the =STR part yet?
def techrating(school, output=None, email=None, outputpeers =None, emaildoc=None, rankings=None): #bottom10=None): #How do I specify an email?
    """Retrieves a school's TechRating (-h for more options).

        school: Name of school whose data you want (required)

        output: Creates a csv file with requested data

        outputpeers: Creates a csv file with requested data and school peer group

        email: Sends email of requested data (email address required)

        emaildoc: Sends the attachment of your results to desired email (email address required)

        rankings: Ranks TechRating in descending order

    """
    try:
        cursor = connection.cursor()
        cursor.execute("select techrating from slschools where campusname = %s",(school,))
        connection.commit()
        result = cursor.fetchone()
        print "%s has a Tech Rating of %s"%(school, result[0])
        #average()
        #highest()
        #lowest()
    except TypeError:
        print "Not found! \nUse the catalog or find command to identify the correct name of your school"



    if rankings is not None:
        try:
            cursor = connection.cursor()
            cursor.execute("select campusname, techrating, RANK() over(order by techrating desc) from slschools",)
            connection.commit()
            rank = cursor.fetchall()
            for school in rank:
                print "%s- %s, rank: %s"%(school[0], school[1], school[2])
        except TypeError:
            print "Not found! \nUse the catalog or find command to identify the correct name of your school"


    if output is not None:
        try:
            #output(school)
            filename = "TechRatingResults_"+school+".csv"
            outputFile = open(filename, "w") #Don't forget the newline=""!!!!
            outputWriter = csv.writer(outputFile)
            outputWriter.writerow(["School", "TechRating"])
            outputWriter.writerow([school, result[0]])
            print "Newly created file: " + filename
        except TypeError:
            return ""
    
    if outputpeers is not None: #This works now! Still need it to not have to put the school in again....
        try:
            cursor = connection.cursor()
            cursor.execute("select peergroup from slschools where campusname = %s",(school,))
            connection.commit()
            pgroup1 = cursor.fetchone()
            pgroup = pgroup1[0]
            cursor.execute("select campusname, techrating from slschools where peergroup = %s",(pgroup,))
            connection.commit()
            pgresults1 = cursor.fetchall()
            filename = "ResultsVsPeers_"+ school +".csv"
            outputfile = open(filename, "w")
            outputWriter = csv.writer(outputfile, delimiter = ",")
            outputWriter.writerow(["School", "TechRating"])
            for school, techrating in pgresults1:
                outputWriter.writerow([school, techrating])
            print "Newly created file: ", filename
        except TypeError:
            return ""

    if email is not None:
        try:
            smtpObj = smtplib.SMTP("smtp.gmail.com",587)
            smtpObj.ehlo()
            smtpObj.starttls()
            smtpObj.login('sightlinespython@gmail.com', 'Meat4848')
            print ("Connection Successful")
            content= "Hey There,\nThe techrating of %s is %s. Isn't this stuff crazy?"%(school, result[0])
            smtpObj.sendmail('sightlinespython@gmail.com', email,
                'Subject: Search Results.\n%s'%(content))
            smtpObj.quit()
            print ("Email sent")
        except TypeError:
            return " "


    if emaildoc is not None:
        try:

            cursor = connection.cursor()
            cursor.execute("select peergroup from slschools where campusname = %s",(school,))
            connection.commit()
            pgroup1 = cursor.fetchone()
            pgroup = pgroup1[0]
            cursor.execute("select campusname, techrating from slschools where peergroup = %s",(pgroup,))
            connection.commit()
            pgresults1 = cursor.fetchall()
            filename = "ResultsVsPeers_"+school+".csv"
            outputfile = open(filename, "w")
            outputWriter = csv.writer(outputfile, delimiter = ",")
            #outputWriter.writerow(["School", "TechRating"])
            for schools, techrating in pgresults1:
                outputWriter.writerow([schools, techrating])
            #FIXME do I need to somehow halt the program and let it restart before calling this?
            emailfrom = "sightlinespython@gmail.com"
            emailto = "smooney48@gmail.com"
            fileToSend = filename
            username = "sightlinespython@gmail.com"
            password = "Meat4848"

            msg = MIMEMultipart()
            msg["From"] = emailfrom
            msg["To"] = emailto
            content = "Hey there"
            msg["Subject"] = "The requested document is attached"
            msg.preamble = "The requested document is attached"

            ctype, encoding = mimetypes.guess_type(fileToSend)
            if ctype is None or encoding is not None:
                ctype = "application/octet-stream"

            maintype, subtype = ctype.split("/", 1)

            fp = open(fileToSend, "rb")
            attachment = MIMEBase(maintype, subtype)
            attachment.set_payload(fp.read())
            fp.close()
            encoders.encode_base64(attachment)
            attachment.add_header("Content-Disposition", "attachment", filename=fileToSend)
            msg.attach(attachment)

            server = smtplib.SMTP("smtp.gmail.com:587")
            server.starttls()
            server.login(username,password)
            server.sendmail(emailfrom, emailto, msg.as_string())
            server.quit()

        except TypeError:
            print ""


@command
@annotate(output='o', email='e', outputpeers = 'p', emaildoc = 'd', rankings='r')#, bottom10 = 'b')
@kwoargs("output", "email", "outputpeers", "emaildoc", "rankings") #keyword only arguemnts #Can I elimiate the =STR part yet?
def density(school, output=None, email=None, outputpeers =None, emaildoc=None, rankings=None):#, bottom10=None): #How do I specify an email?
    """Retrieves a school's density (-h for more options).

        school: Name of school whose data you want (required)

        output: Creates a csv file with requested data

        outputpeers: Creates a csv file with requested data and school peer group

        email: Sends email of requested data (email address required)

        emaildoc: Sends the attachment of your results to desired email (email address required)

        rankings: Ranks density in decreasing order

    """
    try:
        cursor = connection.cursor()
        cursor.execute("select density from slschools where campusname = %s",(school,))
        connection.commit()
        result = cursor.fetchone()
        print "%s has a density of %s"%(school, result[0])
        average()
        highest()
        lowest()
        topTenDensity()
        bottomTenDensity()
    except TypeError:
        print "Not found! \nUse the catalog or find command to identify the correct name of your school"

    
    if rankings is not None:
        try:
            cursor = connection.cursor()
            cursor.execute("select campusname, density, RANK() over(order by density desc) from slschools",)
            connection.commit()
            rank = cursor.fetchall()
            for school in rank:
                print "%s- %s, rank: %s"%(school[0], school[1], school[2])
        except TypeError:
         print "Not found! \nUse the catalog or find command to identify the correct name of your school"

    if output is not None:
        try:
            #output(school)
            filename = "densityResults_"+school+".csv"
            outputFile = open(filename, "w") #Don't forget the newline=""!!!!
            outputWriter = csv.writer(outputFile)
            outputWriter.writerow(["School", "Density"])
            outputWriter.writerow([school, result[0]])
            print "Newly created file: " + filename
        except TypeError:
            return ""
    
    if outputpeers is not None: #This works now! Still need it to not have to put the school in again....
        try:
            cursor = connection.cursor()
            cursor.execute("select peergroup from slschools where campusname = %s",(school,))
            connection.commit()
            pgroup1 = cursor.fetchone()
            pgroup = pgroup1[0]
            cursor.execute("select campusname, density from slschools where peergroup = %s",(pgroup,))
            connection.commit()
            pgresults1 = cursor.fetchall()
            filename = "ResultsVsPeers_"+ school +".csv"
            outputfile = open(filename, "w")
            outputWriter = csv.writer(outputfile, delimiter = ",")
            outputWriter.writerow(["School", "Density"])
            for school, density in pgresults1:
                outputWriter.writerow([school, density])
            print filename
        except TypeError:
            return ""

    if email is not None:
        try:
            smtpObj = smtplib.SMTP("smtp.gmail.com",587)
            smtpObj.ehlo()
            smtpObj.starttls()
            smtpObj.login('sightlinespython@gmail.com', 'Meat4848')
            print ("Connection Successful")
            content= "Hey There,\nThe density of %s is %s. Isn't this stuff crazy?"%(school, result[0])
            smtpObj.sendmail('sightlinespython@gmail.com', email,
                'Subject: Search Results.\n%s'%(content))
            smtpObj.quit()
            print ("Email sent")
        except TypeError:
            return " "

    if emaildoc is not None:
        try:
            cursor = connection.cursor()
            cursor.execute("select peergroup from slschools where campusname = %s",(school,))
            connection.commit()
            pgroup1 = cursor.fetchone()
            pgroup = pgroup1[0]
            cursor.execute("select campusname, density from slschools where peergroup = %s",(pgroup,))
            connection.commit()
            pgresults1 = cursor.fetchall()
            filename = "ResultsVsPeers_"+school+".csv"
            outputfile = open(filename, "w")
            outputWriter = csv.writer(outputfile, delimiter = ",")
            outputWriter.writerow(["School", "Density"])
            for schools, density in pgresults1:
                outputWriter.writerow([schools, density])
            #FIXME do I need to somehow halt the program and let it restart before calling this?
            
            emailfrom = "sightlinespython@gmail.com"
            emailto = "smooney48@gmail.com"
            fileToSend = filename
            username = "sightlinespython@gmail.com"
            password = "Meat4848"

            msg = MIMEMultipart()
            msg["From"] = emailfrom
            msg["To"] = emailto
            content = "Hey there"
            msg["Subject"] = "The requested document is attached"
            msg.preamble = "The requested document is attached"

            ctype, encoding = mimetypes.guess_type(filename)
            if ctype is None or encoding is not None:
                ctype = "application/octet-stream"

            maintype, subtype = ctype.split("/", 1)

            fp = open(fileToSend, "rb")
            attachment = MIMEBase(maintype, subtype)
            attachment.set_payload(fp.read())
            fp.close()
            encoders.encode_base64(attachment)
            attachment.add_header("Content-Disposition", "attachment", filename=fileToSend)
            msg.attach(attachment)

            server = smtplib.SMTP("smtp.gmail.com:587")
            server.starttls()
            server.login(username,password)
            server.sendmail(emailfrom, emailto, msg.as_string())
            server.quit()

        except TypeError:
            print ""

   

@command
def catalog():
    #Dont need to reference global if you arent assigning new value to variable
    """Shows all schools in table. No args req."""
    cursor = connection.cursor()
    cursor.execute("select * from slschools order by campusname",)
    connection.commit()
    result = cursor.fetchall()
    print "\n---LIST OF AVAILABLE SCHOOLS---"
    for key in result:
        print key[0]

@command
def find(school):
    """Allows you to find school using keyword

    school: The keywords related to school in question
    """

    cursor = connection.cursor()
    cursor.execute("select * from slschools where campusname like %s",("%" + school + "%",)) #Remember this! Always a comma inside the brackets!
    connection.commit()
    result = cursor.fetchall()
    for key in result:
        print key[0]

def average():
    global connection
    cursor = connection.cursor()
    cursor.execute("select avg(density) from slschools",)#How can I get it to populate the metric in question
    connection.commit()
    result = cursor.fetchone()
    print "The databse average is: %s"%int(result[0])

def lowest():
    global connection
    cursor = connection.cursor()
    cursor.execute("select campusname from slschools where density=(select min(density) from slschools)",)
    connection.commit()
    school1 = cursor.fetchone()
    school = school1[0]
    cursor.execute("select density from slschools where campusname = %s",(school,))
    connection.commit()
    dens_num1 = cursor.fetchone()
    dens_num = dens_num1[0]
    print "The school in the database with the lowest density is %s with %s"% (school, dens_num)


def highest():
    global connection
    cursor = connection.cursor()
    cursor.execute("select campusname from slschools where density=(select max(density) from slschools)",)
    connection.commit()
    school1 = cursor.fetchone()
    school = school1[0]
    cursor.execute("select density from slschools where campusname = %s",(school,))
    connection.commit()
    dens_num1 = cursor.fetchone()
    dens_num = dens_num1[0]
    print "The school in the database with the highest density is %s with %s"% (school, dens_num)


#def

def basic_density(school): #How do I specify an email?
    global connection
    cursor = connection.cursor()
    cursor.execute("select density from slschools where campusname = '%s'",(school,))
    connection.commit()
    result = cursor.fetchone()
    print result[0]


def topTenDensity():
    cursor = connection.cursor()
    cursor.execute("SELECT campusname, density FROM slschools ORDER BY density DESC LIMIT 10",) #
    connection.commit()
    result = cursor.fetchall()
    print "\n---Here Are Your Top 10 Schools with the Highest Density!---\n" #%percentage
    for key in result:
        print key[0], key[1]

def bottomTenDensity():
    cursor = connection.cursor()
    cursor.execute("select campusname, density from slschools order by density asc limit 10")
    connection.commit()
    result = cursor.fetchall()
    print "\n---Here Are Your Bottom 10 Schools with the Lowest Density!---\n" #%percentage
    for key in result:
        print key[0], key[1]



	

#Cheyney University of PA - Lump Sum
""     
