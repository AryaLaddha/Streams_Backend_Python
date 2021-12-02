from PIL import Image
from src.channels import find_auth_id
import urllib.request
from src.error import InputError
from src import config
from src.data_store import data_store

'''
Crops a saved image given the coordinates of the point

Arguments:
    image_to_crop - string - url of the saved image
    x_start -  int    - x coordinate of the start of the image to crop
    y_start -  int    - y coordinate of the start of the image to crop
    x_end   -  int    - x coordinate of the end of the image to crop
    y_end   -  int    - y coordinate of the end of the image to crop
    ...

Exceptions:
    InputError  - Given size is invalid
    InputError  - Given height to crop is invalid
    InputError  - Given width to crop is invalid
    InputError  - Cooridinates of end points are less than start points
    

Return Value:
    Saves the crop image at the same url that was passed in.
'''
def crop_image_to_size(image_to_crop, x_start, y_start, x_end, y_end):
    image_open = Image.open(image_to_crop)
    image_width, image_height = image_open.size
    if x_start == x_end or y_start == y_end:
        raise InputError("Invalid Size")
    if y_start >= image_height or y_start < 0 or y_end >= image_height or y_end < 0:
        raise InputError("Invalid Height")
    if x_start >= image_width or x_start < 0 or x_end >= image_width or x_end < 0:
        raise InputError("Invalid Width")
    if x_end < x_start or y_end < y_start:
        raise InputError("Invalid Crop Dimmensions")
    cropped_image = image_open.crop((x_start, y_start, x_end, y_end))
    cropped_image.save(image_to_crop)

'''
Saves a image given by the image url if the url is valid

Arguments:
    image_to_save - string - url of the image to save
    u_id -  int    - u_id of the user that uploads the photo
    ...

Exceptions:
    InputError  - Given url returns an HTTP status other than 200
    
Return Value:
    Saves the image given by the url if the url is valid.
'''    
def save_image(image_to_save, u_id):
    #urllib.request.urlretrieve(image_to_save, f'src/static/{u_id}.jpg')
    try:
        urllib.request.urlretrieve(image_to_save, f'src/static/{u_id}.jpg')
        #print("Saved")
    except Exception as error:
        raise InputError(description = "HTTP status other than 200 returned") from error

'''
Sets the url generated after saving an image to the particular u_id in all channels

Arguments:
    image_url - string - url of the image created after saving
    auth_id -  int    - u_id of the user that uploads the photo
    ...
    
Return Value:
    Sets the image to the user given by the auth_id.
'''      
def set_image(img_url, auth_id):
    user_details = data_store.get()['users']
    channel_details = data_store.get()['channels']
    for user in user_details:
        if auth_id == user['auth_user_id']:
            user['profile_img_url'] = img_url
    for channel in channel_details:
        for member in channel['all_members']:
            if member['u_id'] == auth_id:
                member['profile_img_url'] = img_url

'''
Checks if the image type of the image saved is a JPEG

Arguments:
    saved_image - string - url of the image saved
    ...

Exceptions:
    InputError  - Type of the uploaded image is not a JPG
'''    
def check_file_type(saved_image):
    img = Image.open(saved_image)
    if img.format != 'JPEG':
        raise InputError("Image uploaded is not a JPG")

'''
Sets a server wide default image in case the user has not uploaded an image
    
Return Value:
    img_url_default - int - url of the default image after saving it.
'''           
def default_image():
    urllib.request.urlretrieve('http://cgi.cse.unsw.edu.au/~jas/home/pics/jas.jpg', f'src/static/default.jpg')
    img_url_default = config.url + f'static/default.jpg'
    return img_url_default

'''
Returns a url for the default image saved
    
Return Value:
    config.url + f'static/default.jpg' - string - url of the saved default image
'''         
def get_default_img_url(u_id):
    return config.url + f'static/default.jpg'
    
    
