from testing_webpage.beta_invite.util.email_sender import send
from beta_invite.models import User


send(User(name='    Juan Pablo Isaza', email='biosolardecolombia@gmail.com'))
