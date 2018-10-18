import time
from datetime import datetime
from model import save_other_values, run


if __name__ == '__main__':
    t0 = time.time()
    #run()
    save_other_values()
    t1 = time.time()
    print('On {0} {1}, took: {2}'.format(datetime.today(), __file__, t1 - t0))
