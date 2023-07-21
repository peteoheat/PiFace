class PiFaceConfig:
    """
    Class that does a lot of the data structure setup
    """
    def AccessCards(self):
        # Dictionary to differentiate one, two and three factor cards. Factor 99 is for a spare card
        card_factor = {'0D004B5BBAA7': 1, '3900E1BC3753': 1, '3900E24C33A4': 1, '3900DC2807CA': 2, '3900E5EB4770': 2,
                       '3900DC751888': 2, '3900E5E7172C': 3, '3900DC75FB6B': 3, '3900E1BF3453': 3, '3900DC7760F2': 3,
                       '3900DC783AA7': 2, '3900E6685EE9': 1, '3900E4C66C77': 3, '3900E4BAFA9D': 2, '3900E6757FD5': 1,
                       '3900E4BDD2B2': 3, '3900E67049E6': 2, '3900E666873E': 1, '3900E6765FF6': 3, '3900E67817B0': 2,
                       '3900E665A51F': 1}

        # Dictionary to set the access PIN for each card. # is used for spare cards
        card_pin = {'0D004B5BBAA7': '1966', '3900E1BC3753': '1966', '3900E24C33A4': '1966', '3900DC2807CA': '1966',
                    '3900E5EB4770': '1966', '3900DC751888': '1966', '3900E5E7172C': '1966', '3900DC75FB6B': '1966',
                    '3900E1BF3453': '1966', '3900DC7760F2': '1966', '3900DC783AA7': '1966', '3900E6685EE9': '1966',
                    '3900E4C66C77': '1966', '3900E4BAFA9D': '1966', '3900E6757FD5': '1966', '3900E4BDD2B2': '1966',
                    '3900E67049E6': '1966', '3900E666873E': '1966', '3900E6765FF6': '1966', '3900E67817B0': '1966',
                    '3900E665A51F': '1966'}
    def GPIOSetup(self):
        # GPIO PINS
        Beacon = 26
        Buzzer = 17

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(Buzzer, GPIO.OUT)
        GPIO.setup(Beacon, GPIO.OUT)
        GPIO.output(Beacon, GPIO.HIGH)
        
    def LoadKnownFaceEncodings(self):
        # load the known faces and embeddings
        encodings_file = "encodings.pickle"
        # Load face encodings
        knownfacedata = pickle.loads(open(encodings_file, "rb").read())