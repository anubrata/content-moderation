import http.client, urllib.request, urllib.parse, urllib.error, base64
import glob, json

from azure_cfg import api_key

# azure setup
uri_base = 'westcentralus.api.cognitive.microsoft.com'
uri_endpoint = '/contentmoderator/moderate/v1.0/ProcessImage/Evaluate?%s'

params = {
}

headers = {
    'Content-Type': 'image/jpeg',
    'Ocp-Apim-Subscription-Key': api_key,
}

# setup
images = glob.glob('../images/**/*.jpg')
predictions = {}
failed = []

# loop through images
for idx, image in enumerate(images):
    print('[INFO] Predicting adult content for \''+ image + '\' (' + \
          str((idx + 1)) + '/' + str(len(images)) + ')')

    name = image.split('/')[-1]
    body = open(image, 'rb')

    # ping Azure REST API
    try:
        conn = http.client.HTTPSConnection(uri_base)
        conn.request('POST', uri_endpoint % params, body, headers)
        response = conn.getresponse()
        data = response.read()
        conn.close()

        data = json.loads(data.decode('utf-8'))
        predictions[name] = {
            'AdultClassificationScore': data['AdultClassificationScore'],
            'IsImageAdultClassified'  : data['IsImageAdultClassified'],
            'RacyClassificationScore' : data['RacyClassificationScore'],
            'IsImageRacyClassified'   : data['IsImageRacyClassified']
        }
    except Exception:
        print('[ERROR] ' + str(data))

        failed.append(image)
        predictions[name] = None

# print images for which predictions failed
if len(failed) > 0:
    print('[INFO] Failed to predict adult content in the following images:')
    print('\t' + ('\n\t').join(failed))

# save predictions to json
print('[INFO] Saving predictions to disk...')
with open('azure_predictions.json', 'w') as handle:
    json.dump(predictions, handle, sort_keys=True, indent=4)

