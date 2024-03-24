# Image-Croping
This is an image cropping application that allows users to crop images to predefined sizes like passport photos and ID cards, as well as custom sizes specified by the user. The application uses computer vision techniques to identify the main subject in an image and intelligently crop around it. Even if the image is not perfectly aligned or contains extras like scarves or hats, the app can crop tightly around the subject's face.

The core cropping functionality is powered by a deep learning model built using PyTorch and trained on a dataset of portrait images. The model takes in an input image, detects the face and body of the main subject using object detection techniques, and suggests an optimal crop around the subject. This enables tight, professional-looking crops even with imperfect input images.

Live link:- https://image-croping.onrender.com
Additional features include:

1. An interface for users to upload one or more images via a web form. Images can be in common formats like JPG, PNG, etc.  
2. Options to crop images to predefined sizes for profiles, passport photos, or custom dimensions specified by the user.
3. Face detection algorithms to identify faces in the images. Even if a face is obscured by hats, masks, etc, it attempts to detect and crop.
4. Smart cropping to ensure the face is centered and framed consistently across all images. Automatically handles rotated or off-center faces.
5. Resizing of the cropped images to the target dimensions set by the user. Popular presets as well as custom sizes are supported.
6. Downloading of ZIP archives containing all processed images for easy distribution.
7. Logging of any errors or failures in processing to help diagnose issues.

The main technologies used are Python, Flask for the web framework, and OpenCV for efficient image processing and face detection. 

Built With:
1. Python, Flask - Backend framework
2. OpenCV - Image processing
3. SQLite - Database


Platform Screenshots:

![Screenshot 2023-10-12 203205](https://github.com/vaibhav13002/Image-Croping/assets/134428799/d5f11013-fe0d-4bb2-b82e-14b812e107b9)
code snip

![Screenshot 2023-10-12 203009](https://github.com/vaibhav13002/Image-Croping/assets/134428799/a72124e2-0f7f-41fb-ac88-581343eb111a)
Login portal

![Screenshot 2023-10-12 202953](https://github.com/vaibhav13002/Image-Croping/assets/134428799/711c3a8e-c6b7-4d95-9993-7e442ea5e94c)
Custom Selection

![Screenshot 2023-10-12 202921](https://github.com/vaibhav13002/Image-Croping/assets/134428799/d5abc4ed-acc8-4ae7-8e37-5685fe497ee7)
Processed Images

[ Accuracy= 96% ]
