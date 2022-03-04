from flask import Flask, request, send_file, render_template, abort
import os
from PIL import Image
import time

app = Flask(__name__)
APP_ROOT = os.path.dirname(os.path.abspath(__file__))

@app.route('/')
@app.route('/app')
def home():
    return render_template('app.html')

# Image upload API. 
@app.route('/upload', methods=["POST"])
def image_upload():
    target = os.path.join(APP_ROOT, 'user_images')

    # Check if directory is available. if not it will create new directory with name user_images.
    if not os.path.isdir(target):
        os.mkdir(target)

    # Get the image from the form.
    upload = request.files['file'] 
    global filename 
    filename = upload.filename

    # Checks file format. 
    ext = os.path.splitext(filename)[1]
    if (ext == ".jpg") or (ext == ".png") or (ext == ".jpeg"):
        print("File accepted.")
    else:
        print("Invalid file Format.")
        abort(400)

    # Upload file in user_image directory
    destination = "/".join([target, filename])
    upload.save(destination)

    # return editor.html with image.
    return render_template('editor.html', title="Editor Page", image_name=filename)

# Different image operation API
@app.route('/image_operations', methods=["POST"])
def image_operations():
    operation_list = []
    global destination

    # Get the img operation value from the HTML form
    operation_list.append(request.form.get('flip_horizontal'))
    operation_list.append(request.form.get('flip_vertical'))
    operation_list.append(request.form.get('grayscale'))
    operation_list.append(request.form.get('thumbnail'))
    operation_list.append(request.form.get('rotate_left'))
    operation_list.append(request.form.get('rotate_right'))
    operation_list.append(request.form.get('resize_height'))
    operation_list.append(request.form.get('resize_width'))
    operation_list.append(request.form.get('rotate_degree'))
    
    # Get the image from directory 
    target = os.path.join(APP_ROOT, 'user_images/')
    destination = "".join([target, filename])
    img = Image.open(destination)

    # Removes the None entry from list of operation.
    res = [i for i in operation_list if i]

    # Image operations.
    def flip_horizontal(img):
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
        return img

    def flip_vertical(img):
        img = img.transpose(Image.FLIP_TOP_BOTTOM)
        return img

    def grayscale(img):
        img = img.convert(mode="L")
        return img

    def resize_height_and_width(height, width, img):
        if int(width) and int(height) > 0:
            img = img.resize((int(width), int(height)))
        else:
            abort(400)
        return img

    def thumbnail(img):
        img = img.resize((100, 100))  
        return img

    def rotate_left(img):
        img = img.rotate(90,resample=0, expand=True)
        return img

    def rotate_right(img):
        img = img.rotate(-1*90,resample=0, expand=True)
        return img

    def rotate_degree(angle, img):
        img = img.rotate(int(angle))
        return img

    #Applies all user specified operations on image
    for operation in res: 
        if operation == 'flip_horizontal':
            img = flip_horizontal(img)
        elif operation == 'flip_vertical':
            img = flip_vertical(img)
        elif operation == 'grayscale':
            img = grayscale(img) 
        elif operation == 'thumbnail':
            img = thumbnail(img)
        elif operation == 'rotate_left':
            img = rotate_left(img)
        elif operation == 'rotate_right':
            img = rotate_right(img)
        elif operation_list[6] != "":
            img = resize_height_and_width(operation_list[6],operation_list[7], img)
        elif operation_list[8] != "":
            img = rotate_degree(operation_list[8],img)

    # save processed image in directory. 
    filename2 = str(time.time()) + filename
    destination = "/".join([target, filename2])
    img.save(destination)

    # Return image download page.
    return render_template('download.html', title="Download Page", image_name=destination)

# Image Download API. 
@app.route('/download',  methods=["GET"])
def download_file():
	return send_file(destination, as_attachment=True)

# Main function to start execution of program.
if __name__ == '__main__':
    app.run('0.0.0.0', port = 5001)
