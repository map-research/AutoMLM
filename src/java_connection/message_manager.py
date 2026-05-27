"""
    File use to store read and write operation on messages send between Java and Python
"""
import sys
import tempfile
import os

temp_dir = tempfile.gettempdir()
#Folder dedicated for the message exchange
jtop_in_dir = temp_dir + "\\XModeler\\JtopIn\\"
jtop_out_dir = temp_dir + "\\XModeler\\JtopOut\\"

def readMessageContent(messageId):
    """
        Read the transmitted args from Java from file.
        Each line should represent on function argument
        The message file is deleted after the read process.
    """
    messagePath = jtop_in_dir + messageId
    lines = readFromFile(messagePath)
    os.remove(messagePath)
    log = ("Args:'{}'".format(lines))
    print(log, file=sys.stderr)
    return lines

def readFromFile(messagePath):
    with open(messagePath, 'r') as file:
        lines = [line.strip() for line in file.readlines()]
    return lines

def postResponse(messageId, response):
    """
       This function writes the Python respond to a file that serves for Java as message.
       Every element of the response is written to a new file row.

       Parameters:
       messageId (string): name of the file use for the communication of respond
       response : data that serves as response
       """
    log = ("Processed Response:'{}'".format(response))
    print(log, file=sys.stderr)
    messagePath = jtop_out_dir + messageId
    with open(messagePath, 'w') as file:
        if isinstance(response, set):
            for element in response:
                file.write(f"{element}\n")
        elif isinstance(response, str):
            file.write(response)
