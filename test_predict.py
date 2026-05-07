import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.model import predict_text

try:
    print(predict_text('https://www.bing.com'))
except Exception as e:
    import traceback
    traceback.print_exc()
