from dotenv import load_dotenv

load_dotenv("config.env")

HEROKU = True  # NOTE Make it false if you're not deploying on heroku or docker.

if HEROKU:
    from os import environ

    BOT_TOKEN = environ.get("BOT_TOKEN", None)
    API_ID = int(environ.get("API_ID", 6))
    API_HASH = environ.get(
        "API_HASH", "eb06d4abfb49dc3eeb1aeb98ae0f581e"
    )
    SESSION_STRING = environ.get("SESSION_STRING", None)
    USERBOT_PREFIX = environ.get("USERBOT_PREFIX", ".")
    SUDO_USERS_ID = list(
        int(x) for x in environ.get("SUDO_USERS_ID", "").split()
    )
    LOG_GROUP_ID = int(environ.get("LOG_GROUP_ID", None))
    GBAN_LOG_GROUP_ID = int(environ.get("GBAN_LOG_GROUP_ID", None))
    MESSAGE_DUMP_CHAT = int(environ.get("MESSAGE_DUMP_CHAT", None))
    FERNET_ENCRYPTION_KEY = environ.get("FERNET_ENCRYPTION_KEY", None)
    WELCOME_DELAY_KICK_SEC = int(
        environ.get("WELCOME_DELAY_KICK_SEC", None)
    )
    MONGO_DB_URI = environ.get("MONGO_DB_URI", None)
    ARQ_API_URL = environ.get("ARQ_API_URL", None)
    ARQ_API_KEY = environ.get("ARQ_API_KEY", None)
    LOG_MENTIONS = (
        True if int(environ.get("LOG_MENTIONS", None)) == 1 else False
    )
    SPAM_CHECK_EXCEPTION_GROUPS = list(
        int(y)
        for y in environ.get(
            "SPAM_CHECK_EXCEPTION_GROUPS", ""
        ).split()
    )
else:
    BOT_TOKEN = "467677575:YZfaakjwd545dfg-N6JStihhuw5gQeZHntc"
    API_ID = 123456
    API_HASH = "dfxcgs5s12hdcxfgdfz"
    USERBOT_PREFIX = "."
    PHONE_NUMBER = "+916969696969"  # Need for Helper Userbot
    SUDO_USERS_ID = [
        4543744343,
        543214651351,
    ]  # Sudo users have full access to everythin, don't trust anyone
    LOG_GROUP_ID = -100125431255
    GBAN_LOG_GROUP_ID = -100125431255
    MESSAGE_DUMP_CHAT = -1001181696437
    FERNET_ENCRYPTION_KEY = "iKMq0WZMnJKjMQxZWKtv-cplMuF_LoyshXj0XbTGGWM="  # Leave this as it is
    WELCOME_DELAY_KICK_SEC = 300
    MONGO_DB_URI = "mongodb+srv://username:password@cluster0.ksiis.mongodb.net/YourDataBaseName?retryWrites=true&w=majority"
    ARQ_API_KEY = "Get this from @ARQRobot"
    ARQ_API_URL = "https://thearq.tech"
    LOG_MENTIONS = True
    SPAM_CHECK_EXCEPTION_GROUPS = (
        []
    )  # Leave it empty if you don't know about it
