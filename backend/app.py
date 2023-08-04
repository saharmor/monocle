import ast
from flask import Flask, request
from flask_cors import CORS
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

def clean_image_data(image_data):
    # Transform the input byte array into a list for easier manipulation
    byte_list = list(image_data)[2:] # remove unnecessary prefix (b')

    # Define the sequence to truncate after
    end_sequence = [0xFF, 0xD9]

    # Check if the sequence is in the byte array
    if end_sequence[0] in byte_list:
        # Find the first index of the end sequence
        index = byte_list.index(end_sequence[0])

        # Check if the sequence is not at the end of the byte array
        if index < len(byte_list) - 1:
            # If the next byte matches the second part of the end sequence, truncate the byte array
            if byte_list[index + 1] == end_sequence[1]:
                byte_list = byte_list[:index + 2]

    # Convert the list back to bytes
    truncated_byte_array = bytes(byte_list)

    return truncated_byte_array

@app.route('/receive-img', methods=['POST'])
def receive_image():
    image_data = request.files['file']
    dest_email = request.form.get('destEmail')
    image_style = request.form.get('imageStyle')

    cleaned_image_data = clean_image_data(image_data.read())
    image_name = f'image_{datetime.now()}.jpeg'
    byte_content = bytes(cleaned_image_data.decode('unicode_escape'), 'latin1')
    
    with open(image_name, 'wb') as f:
        f.write(byte_content)
    
    import subprocess
    subprocess.call(['open', image_name])

    # image_path = generate_image_controlnet(image_name, image_style)
    # send_email(image_path, dest_email)
    return '', 200

def generate_image_controlnet(image_name: str, image_style: str):
    from gradio_client import Client

    control_net_endpoint = os.getenv("CONTROL_NET_HF_ENDPOINT")
    
    temp_output_dir = "./backend/generated_images"
    if not os.path.exists(temp_output_dir):
        os.makedirs(temp_output_dir)

    client = Client(control_net_endpoint, output_dir=temp_output_dir)
    result = client.predict(
                    image_name,	# str (filepath or URL to image) in 'parameter_8' Image component
                    f"In the style of {image_style}",	# str in 'Prompt' Textbox component
                    "best quality, extremely detailed",	# str in 'Additional prompt' Textbox component
                    "longbody, lowres, bad anatomy, bad hands, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality",	# str in 'Negative prompt' Textbox component
                    1,	# int | float (numeric value between 1 and 1) in 'Number of images' Slider component
                    768,	# int | float (numeric value between 256 and 768) in 'Image resolution' Slider component
                    30,	# int | float (numeric value between 1 and 100) in 'Number of steps' Slider component
                    9,	# int | float (numeric value between 0.1 and 30.0) in 'Guidance scale' Slider component
                    1076737789,	# int | float (numeric value between 0 and 2147483647) in 'Seed' Slider component
                    100,	# int | float (numeric value between 1 and 255) in 'Canny low threshold' Slider component
                    200,	# int | float (numeric value between 1 and 255) in 'Canny high threshold' Slider component
                    api_name="/canny"
    )

    if not os.path.exists(result):
        return None
    
    return f'{os.path.join(result, get_hf_output_image_dir(result))}/image.png'

def get_creation_time(path):
  """Gets the creation time of the directory at the specified path."""
  stat = os.stat(path)
  return stat.st_ctime

def get_hf_output_image_dir(path):
  """Gets the second directory that was created in the specified path."""
  directories = os.listdir(path)
  creation_times = []
  for directory in directories:
    full_path = os.path.join(path, directory)
    if not os.path.isdir(full_path):
        continue

    creation_time = get_creation_time(full_path)
    creation_times.append((directory, creation_time))

  first_created_directory = min(creation_times, key=lambda x: x[1])[0]
  return first_created_directory

def send_email(image_path: str, dest_email: str):
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.base import MIMEBase
    from email import encoders

    # Your Gmail account
    from_address = os.getenv("SENDER_EMAIL")
    password = os.getenv("GMAIL_APP_TOKEN") # follow this guide to create such a token for your Gmail account https://stackoverflow.com/questions/72480454/sending-email-with-python-google-disables-less-secure-apps

    # Create the email header
    msg = MIMEMultipart()
    msg["From"] = from_address
    msg["To"] = dest_email
    msg["Subject"] = "Scenery reimagined with Monocle + AI ✨"

    # Open the file in bynary mode
    binary_file = open(image_path, "rb")

    # Then we create the MIMEBase object to store the image
    mime_image = MIMEBase("image", "jpeg")
    # And read it into the MIMEBase object
    mime_image.set_payload(binary_file.read())

    # We encode the image in base64 and add the headers so that the email client knows it's an attachment
    encoders.encode_base64(mime_image)
    mime_image.add_header("Content-Disposition", f"attachment; filename= {image_path}")
    msg.attach(mime_image)

    # We then connect to the Gmail server
    server = smtplib.SMTP("smtp.gmail.com", 587)

    # We start the server
    server.starttls()

    # Login to the server
    server.login(from_address, password)

    # Convert the MIMEMultipart object to a string
    text = msg.as_string()

    # And finally send the email
    server.sendmail(from_address, dest_email, text)
    server.quit()

if __name__ == '__main__':
    app.run(port=8000)


