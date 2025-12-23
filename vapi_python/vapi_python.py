from daily import *
import requests
from .daily_call import DailyCall

SAMPLE_RATE = 16000
CHANNELS = 1


def create_web_call(api_url, api_key, payload):
    url = f"{api_url}/call/web"
    headers = {
        'Authorization': 'Bearer ' + api_key,
        'Content-Type': 'application/json'
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        call_id = data.get('id')
        web_call_url = data.get('webCallUrl')
        return call_id, web_call_url
    except requests.exceptions.HTTPError as e:
        try:
            error_data = response.json()
            message = error_data.get('message', 'Unknown API error')
        except:
            message = f"HTTP Error {response.status_code}: {response.reason}"
        raise Exception(f"API Call Failed: {message}") from e
    except requests.exceptions.RequestException as e:
        raise Exception(f"Connection Error: {e}") from e


class Vapi:
    def __init__(self, *, api_key, api_url="https://api.vapi.ai"):
        self.api_key = api_key
        self.api_url = api_url

    def start(
        self,
        *,
        assistant_id=None,
        assistant=None,
        assistant_overrides=None,
        squad_id=None,
        squad=None,
    ):
        # Start a new call
        if assistant_id:
            payload = {'assistantId': assistant_id, 'assistantOverrides': assistant_overrides}
        elif assistant:
            payload = {'assistant': assistant, 'assistantOverrides': assistant_overrides}
        elif squad_id:
            payload = {'squadId': squad_id}
        elif squad:
            payload = {'squad': squad}
        else:
            raise Exception("Error: No assistant specified.")

        call_id, web_call_url = create_web_call(
            self.api_url, self.api_key, payload)

        if not web_call_url:
            raise Exception("Error: Unable to create call.")

        print('Joining call... ' + call_id)

        self.__client = DailyCall()
        self.__client.join(web_call_url)

    def stop(self):
        self.__client.leave()
        self.__client = None

    def send(self, message):
        """
        Send a generic message to the assistant.

        :param message: A dictionary containing the message type and content.
        """
        if not self.__client:
            raise Exception("Call not started. Please start the call first.")

        # Check message format here instead of serialization
        if not isinstance(message, dict) or 'type' not in message:
            raise ValueError("Invalid message format.")

        try:
            self.__client.send_app_message(message)  # Send dictionary directly
        except Exception as e:
            print(f"Failed to send message: {e}")

    def add_message(self, role, content):
        """
        method to send text messages with specific parameters.
        """
        message = {
            'type': 'add-message',
            'message': {
                'role': role,
                'content': content
            }
        }
        self.send(message)
