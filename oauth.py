from rauth import OAuth1Service, OAuth2Service
from flask import current_app, url_for, request, redirect, session
import os

class FacebookSignIn(object):
    def __init__(self):
        self.service = OAuth2Service(
            name='facebook',
            client_id=os.environ['FACEBOOK_ID'],
            client_secret=os.environ['FACEBOOK_API_SECRET'],
            authorize_url='https://graph.facebook.com/oauth/authorize',
            access_token_url='https://graph.facebook.com/oauth/access_token',
            base_url='https://graph.facebook.com/'
        )

    def authorize(self):
        return redirect(self.service.get_authorize_url(
            scope='email',
            response_type='code',
            redirect_uri=self.get_callback_url())
        )
    
    def get_callback_url(self):
        return url_for('oauth_callback', _external=True)

    def callback(self):
        if 'code' not in request.args:
            return None, None
        oauth_session = self.service.get_auth_session(
            data={'code': request.args['code'],
                  'grant_type': 'authorization_code',
                  'redirect_uri': self.get_callback_url()}
        )
        me = oauth_session.get('me?fields=id,email').json()
        print me['id'], me.get('email')
        return [
            'facebook$' + me['id'],
            me.get('email')
        ]

