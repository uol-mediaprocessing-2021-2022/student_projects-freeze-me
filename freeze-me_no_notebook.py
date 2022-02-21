import cv2 as cv
import numpy as np
import urllib.request
import time
start_time = time.time()


def get_videostream_from_file(filename):
    return cv.VideoCapture(filename)


def get_videostream_from_url(url, filename='video.mp4'):
    urllib.request.urlretrieve(url, filename)
    return cv.VideoCapture(filename)


def background_substraction(stream, noise_reduction=False):
    ret, frame = stream.read()
    images = []
    fgbg = cv.createBackgroundSubtractorKNN()
    kernel = cv.getStructuringElement(cv.MORPH_RECT, (3, 3))
    while ret:
        fgmask = fgbg.apply(frame)
        if noise_reduction:
            fgmask = cv.morphologyEx(fgmask, cv.MORPH_OPEN, kernel)
        testcolor = cv.bitwise_and(frame, cv.cvtColor(fgmask, cv.COLOR_GRAY2RGB))
        masked = np.ma.masked_equal(testcolor, 0)
        images.append(masked)
        ret, frame = stream.read()
    return images


def optical_flow(stream, int_threshold=150, noise_reduction=False):
    ret, frame1 = stream.read()
    prvs = cv.cvtColor(frame1, cv.COLOR_BGR2GRAY)
    hsv = np.zeros_like(frame1)
    hsv[..., 1] = 255
    images = []
    kernel = cv.getStructuringElement(cv.MORPH_RECT, (3, 3))
    while (1):
        ret, frame2 = stream.read()
        if not ret:
            break
        next = cv.cvtColor(frame2, cv.COLOR_BGR2GRAY)
        flow = cv.calcOpticalFlowFarneback(prvs, next, None, 0.5, 3, 15, 3, 5, 1.2, 0)
        mag, ang = cv.cartToPolar(flow[..., 0], flow[..., 1])
        hsv[..., 0] = ang * 180 / np.pi / 2
        hsv[..., 2] = cv.normalize(mag, None, 0, 255, cv.NORM_MINMAX)
        intensity = hsv[:, :, 2]
        intensity_mask = (np.logical_not(intensity < int_threshold) * 255).astype(np.uint8)
        mask = np.dstack((intensity_mask, intensity_mask, intensity_mask))
        if noise_reduction:
            mask = cv.morphologyEx(mask, cv.MORPH_OPEN, kernel)
        masked_img = cv.bitwise_and(frame2, mask)
        masked = np.ma.masked_equal(masked_img, 0)
        images.append(masked)
        prvs = next
    return images


# def bgs_and_optical(stream, noise_reduction=False):
#     images_bgs = background_substraction(stream,noise_reduction=noise_reduction)
#     stream.set(cv.CAP_PROP_POS_FRAMES,0)
#     images_of = optical_flow(stream, noise_reduction=noise_reduction)
#     new_images = []
#     for i in range(len(images_bgs)):
#         bgs_mask = cv.threshold(cv.cvtColor(images_bgs[1],cv.COLOR_BGR2GRAY), 254, 255 )
#         new_img = cv.bitwise_and(images_bgs[i])

def average_images(images, opacity):
    avg_img = np.ma.average(images, axis=0)
    avg_img = avg_img.astype(np.uint8)
    avg_img_bgra = cv.cvtColor(avg_img, cv.COLOR_BGR2BGRA)
    alpha_channel = avg_img_bgra[:, :, 3]
    alpha_channel[np.all(avg_img_bgra[:, :, 0:3] == (0, 0, 0), 2)] = 0
    avg_img_bgra = avg_img_bgra.astype(np.float64)
    avg_img_bgra[:, :, 3] *= opacity
    avg_img_bgra = avg_img_bgra.astype(np.uint8)

    # final_img = cv.add(avg_img_bgra, cv.cvtColor(firstframe, cv.COLOR_RGB2BGRA))
    return avg_img_bgra


def video_to_freeze_picture(mode, blur_motion=False, opacity=0.5, noise_reduction=False, file=None, url=None):
    if file:
        stream = get_videostream_from_file(file)
    elif url:
        stream = get_videostream_from_url(url)
    else:
        print("No input file provided")
        quit()
    if mode.lower() == 'bgs':
        images = background_substraction(stream)
    elif mode.lower() == 'of':
        images = optical_flow(stream, noise_reduction=noise_reduction)
    elif mode.lower() == 'both':
        print("Not implemented yet")
        quit()
    else:
        print("No valid mode provided")
        quit()
    avg_image = average_images(images, opacity=opacity)
    if blur_motion:
        avg_image = cv.blur(avg_image,(3,3))
    stream.set(cv.CAP_PROP_POS_FRAMES,0)
    ret, img = stream.read()
    avg_img_to_gray = cv.cvtColor(avg_image, cv.COLOR_BGR2GRAY)
    motion_mask_inv = (np.logical_not(avg_img_to_gray > 1) * 255).astype(np.uint8)
    firstframe_masked = cv.bitwise_and(img, img, mask=motion_mask_inv)
    final_img = cv.add(avg_image, cv.cvtColor(firstframe_masked, cv.COLOR_BGR2BGRA))
    return final_img


image = video_to_freeze_picture('bgs', url='https://media.istockphoto.com/videos/female-gymnast-doing-a-flip-on-balance-beam-video-id512016636', blur_motion=True)
cv.imwrite('gymnast_of.png', image)
print("--- %s seconds ---" % (time.time() - start_time))

