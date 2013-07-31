from flask import Flask
import settings

app = Flask('wallet')
app.config.from_object('wallet.settings')
 
import views
import workers
#import data