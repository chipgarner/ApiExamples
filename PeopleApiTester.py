import base64
import io
import json
import time

import numpy as np
import requests
from PIL import Image


class PeopleApiTester:
    def __init__(self, sentry_id):

        self.headers = {
            'content-type': "application/json",
            'x-api-key': "get me from Sentry",
            'cache-control': "no-cache"
        }
        self.url = 'get url from sentry'

        self.payload_no_image = {'body': {'Site_Id': sentry_id, 'Camera_Name': 'test', 'Image_Bytes': ''}}

        self.np_image = None
        self.img_results = None

    def do_next_image(self, np_image):

        post_payload = self.payload_no_image
        encoded_string = self.np_image_to_base64(np_image)
        post_payload['body']['Image_Bytes'] = encoded_string.decode('utf-8')

        post_payload = json.dumps(post_payload)

        self.img_results = self.process_image_wait_for_result(self.url, post_payload, self.headers)

        return self.img_results

    @staticmethod
    def np_image_to_base64(np_image):
        pil_image = Image.fromarray(np_image)
        bytes_image = io.BytesIO()
        pil_image.save(bytes_image, "JPEG")
        bytes_image.seek(0)
        encoded_string = base64.b64encode(bytes_image.read())

        return encoded_string

    @staticmethod
    def process_image_wait_for_result(url, post_payload, headers):
        try:
            start_post = time.time()

            image_post_response = requests.request("POST", url, data=post_payload, headers=headers, timeout=25)
            print('Post time: ' + str(time.time() - start_post))
        except requests.exceptions.ReadTimeout as ex:
            return str(ex)
        except requests.exceptions.ConnectionError as ex:
            return str(ex)

        if image_post_response.status_code == 200:

            post_data = json.loads(image_post_response.text)
            return post_data

        else:
            return image_post_response


def get_image():
    image_bytes = open('Tests/Images/Bridge.jpg', "rb").read()  # Relative path to a .jpg imaage
    img = Image.open(io.BytesIO(image_bytes))
    np_image = np.asarray(img)
    return np_image


if __name__ == '__main__':
    sentryid = 'S-J3FKD5'
    api_tester = PeopleApiTester(sentryid)

    image = get_image()

    response = api_tester.do_next_image(image)

    print(response)

## Examle response:
## {'marketing_message': ' ', 'bounding_box': [[240, 798, 1320, 1394], [259, 517, 1179, 835]], 'occupied_state': 'Alert', 'Image_Id': 'S-J3FKD5_test@1572897954'}
## Two bounding boxes returned from an image with two people in it.
