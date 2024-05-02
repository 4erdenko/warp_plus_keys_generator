# Warp Plus Key Generator

This is a Python script that generates Warp Plus keys for your applications using Cloudflare. 

The script automates the following procedures:
1. Registers a new user account
2. Adds a referral to the account
3. Deletes the referral account
4. Updates the initial license (swap with another license from a predefined list and then swap back to the initial)
5. Retrieves final quota and checks if Warp Plus is enabled
6. If Warp Plus is enabled, final license and quota are stored in a JSON file.

## Prerequisites

- Python 3.11.4
- httpx package for sending HTTP requests
- python-dotenv package for managing environment variables

These packages can be installed using:

```
pip install -r requirements.txt
```

## Usage

1. Clone the repository
2. Navigate to project directory
3. Create the .env file in the project directory and populate it with your keys. The format should be:
```
KEYS=key1,key2,key3,...
```
❗All keys must be already Warp+ for generation new keys. You need at least a one warp+ key!
4. To start the key generation process, simply run the Python script:

```bash
python main.py
```
Please note you need to specify the number of keys the program must generate in the `main` function.

## Disclaimer

This script is provided as is without any guarantees or warranty. The author is not responsible for any misuse or damage caused by this program.

## Contributions

Contributions, issues, and feature requests are welcome!

Feel free to check [issues page](http://github.com/4erdenko/warp_plus_keys_generator/issues).

## License

[MIT](LICENSE) 
