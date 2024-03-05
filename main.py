import json
import logging
import random
import sys
from typing import Tuple

import httpx
import time
import os

from dotenv import load_dotenv
from httpx import Client

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s ' '- %(message)s',
    stream=sys.stdout,
)

load_dotenv()

keys = [os.getenv('KEYS').split(',')]


def save_key_to_file(key_info: dict) -> None:
    """
    Saves the given key information to a JSON file.

    Parameters:
    - key_info (dict): The dictionary containing the key
    information to be saved.

    Returns:
    - None

    Raises:
    - Exception: If there is an error while saving the key
    information to the file.

    Example usage:
    key_info = {'license': 'ABC123', 'expiry_date': '2022-12-31'}
    save_key_to_file(key_info)
    """
    file_name = 'GeneratedKeys.json'
    try:
        if not os.path.exists(file_name):
            with open(file_name, 'w') as file:
                json.dump([], file)

        with open(file_name, 'r+') as file:
            data = json.load(file)
            data.append(key_info)
            file.seek(0)
            json.dump(data, file, indent=4)
        logging.info(f"Key successfully saved: {key_info['license']}")
    except Exception as e:
        logging.error(f'Error saving to file: {e}')


def register_user(client: Client) -> Tuple[int, str, str]:
    """
    Registers a new user.

    This method sends a POST request to the '/reg' endpoint to register a
    new user via the provided client.

    Parameters:
        client (Client): The client object used to send the request.

    Returns:
        A tuple containing the user information:
        - id (int): The id of the registered user.
        - license (str): The license associated with the user's account.
        - token (str): The token generated for the user.

    Raises:
        None.

    Usage:
        client = Client()
        id, license, token = register_user(client)
    """
    response = client.post('/reg')
    user_info = response.json()
    logging.info('New user registered successfully.')
    return user_info['id'], user_info['account']['license'], user_info['token']


def register_referral_user(client: Client) -> Tuple[int, str]:
    """
    Register a referral user.

    Args:
        client (Client): The client object for making the post request.

    Returns:
        Tuple[int, str]: A tuple containing the referral user's ID and token.

    Raises:
        None.

    Example:
        response = register_referral_user(client)
    """
    response = client.post('/reg')
    referral_info = response.json()
    logging.info('Referral user registered successfully.')
    return referral_info['id'], referral_info['token']


def add_referral_and_delete(
        client: Client,
        user_id: int,
        user_token: str,
        referral_id: int,
        referral_token: str,
) -> None:
    client.patch(
        f'/reg/{user_id}',
        headers={
            'Authorization': f'Bearer {user_token}',
            'Content-Type': 'application/json; charset=UTF-8',
        },
        json={'referrer': f'{referral_id}'},
    )
    logging.info('Referral added to the user.')
    client.delete(
        f'/reg/{referral_id}',
        headers={'Authorization': f'Bearer {referral_token}'},
    )
    logging.info('Referral user deleted.')


def swap_license_keys(
        client: Client, user_id: int, initial_license: str, user_token: str
) -> None:
    """
    Swap the license keys for a user account.

    Args:
        client (Client): The client object used to make API requests.
        user_id (int): The ID of the user account.
        initial_license (str): The initial license key.
        user_token (str): The user token used for authorization.

    Returns:
        None
    """
    selected_key = random.choice(keys)
    client.put(
        f'/reg/{user_id}/account',
        headers={
            'Authorization': f'Bearer {user_token}',
            'Content-Type': 'application/json; charset=UTF-8',
        },
        json={'license': f'{selected_key}'},
    )
    client.put(
        f'/reg/{user_id}/account',
        headers={
            'Authorization': f'Bearer {user_token}',
            'Content-Type': 'application/json; charset=UTF-8',
        },
        json={'license': f'{initial_license}'},
    )
    logging.info('License key applied and reverted.')


def get_updated_user_info(
        client: Client, user_id: int, user_token: str
) -> Tuple[int, str, bool, int]:
    """
    Retrieve the updated user information

    :param client: The client object used for making the API request
    :type client: Client

    :param user_id: The ID of the user
    :type user_id: int

    :param user_token: The token of the user
    :type user_token: str

    :return: A tuple containing the updated user information
    :rtype: tuple[int, str, bool, int]
    """
    response = client.get(
        f'/reg/{user_id}/account',
        headers={'Authorization': f'Bearer {user_token}'},
    )
    user_info = response.json()
    logging.info(f'Updated user information retrieved.')
    return (
        user_info['referral_count'],
        user_info['license'],
        user_info['warp_plus'],
        user_info['quota'],
    )


def delete_user(client: Client, user_id: int, user_token: str) -> None:
    """
    Deletes a user from the server.

    Parameters:
        client (Client): The client object used to make API requests.
        user_id (int): The ID of the user to be deleted.
        user_token (str): The token of the user making the delete request.

    Returns:
        None

    Raises:
        None

    Examples:
        client = Client(...)
        delete_user(client, '1234', 'abcde')
    """
    client.delete(
        f'/reg/{user_id}', headers={'Authorization': f'Bearer {user_token}'}
    )
    logging.info('User deleted after data retrieval.')


def generate_and_save_key(client: Client) -> None:
    """

    Generate and Save Key

    Generates a key and saves it to a file if the user has
    Warp Plus enabled.

    Parameters:
    - client (Client): An instance of the Client class used
    for making HTTP requests.

    Returns:
    None

    Raises:
    - Exception: If there is an error during the HTTP request processing.

    """
    try:
        user_id, initial_license, user_token = register_user(client)
        referral_id, referral_token = register_referral_user(client)
        add_referral_and_delete(
            client, user_id, user_token, referral_id, referral_token
        )
        swap_license_keys(client, user_id, initial_license, user_token)
        (
            referral_count,
            final_license,
            warp_plus,
            quota,
        ) = get_updated_user_info(client, user_id, user_token)
        delete_user(client, user_id, user_token)

        if warp_plus and quota != 0:
            save_key_to_file({'Quota': quota, 'license': final_license})

    except Exception as error:
        logging.error(f'Error during HTTP request processing: {error}')


def create_http_client() -> Client:
    """
    Create an HTTP client.

    This method returns a new instance of the `Client`
    class from the `httpx` library.

    Returns:
        Client: An HTTP client object.

    Example:
        client = create_http_client()
    """
    return httpx.Client(
        base_url='https://api.cloudflareclient.com/v0a2223',
        headers={
            'CF-Client-Version': 'a-6.11-2223',
            'Host': 'api.cloudflareclient.com',
            'Connection': 'Keep-Alive',
            'Accept-Encoding': 'gzip',
            'User-Agent': 'okhttp/3.12.1',
            'Content-Type': 'application/json; charset=UTF-8',
        },
        timeout=35,
    )


def apply_delay_if_needed(current_index: int, total_count: int) -> None:
    """
    Apply delay if needed.

    Parameters:
    current_index (int): The current index.
    total_count (int): The total count.

    Returns:
    None: This method does not return anything.

    """
    if current_index != total_count - 1:
        time.sleep(45)


def main(number_of_keys_to_generate: int) -> None:
    """

    Generates a specified number of Warp+ keys and saves them.

    Parameters:
    - number_of_keys_to_generate (int): The number of Warp+ keys to generate.

    Returns:
    - None

    Example:
        main(5)

    """
    logging.info('Welcome to the Warp+ key generator')
    with create_http_client() as client:
        for i in range(number_of_keys_to_generate):
            logging.info(f'Starting key generation process for key #{i + 1}')
            generate_and_save_key(client)
            apply_delay_if_needed(i, number_of_keys_to_generate)


if __name__ == '__main__':
    main(1)  # Numbers of keys
