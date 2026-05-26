from flask_jwt_extended import verify_jwt_in_request

def verify_token():

    try:
        verify_jwt_in_request()
        return True

    except:
        return False