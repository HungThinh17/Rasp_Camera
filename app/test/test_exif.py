from exif import Image

folder_path = '/home/dgmsli/Desktop/test_image/20230319'
img_filename = '1.png'
img_path = f'{folder_path}/{img_filename}'

with open(img_path, 'rb') as img_file:
    img = Image(img_file)
    
print(img)

#print(img.has_exif)
# List all EXIF tags contained in the image
print(sorted(img.list_all()))


for att in img.list_all():
    print(f'{att}: {img.get(att)}')
# Check updated metadata
#print(f'Date time: {img.get("datetime")}')