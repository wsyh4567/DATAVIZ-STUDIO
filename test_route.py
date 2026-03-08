import sys
sys.path.append('.')
from app import route_page
import traceback

try:
    print('Testing route_page')
    res = route_page('/data')
    print('route_page returned successfully.')
except Exception as e:
    print('Caught exception!')
    traceback.print_exc()
