import redis
import numpy as np
import time
import vision_config
import logging
from threading import Thread

class FaceDetectionService():
    def __init__(self):
        self.RUNNING = True

        self.r = redis.StrictRedis(host=vision_config.REDIS_HOST, port=vision_config.REDIS_PORT)

        self.worker_IN = np.empty([vision_config.MAX_WORKER], dtype=object)
        self.worker_OUT = np.empty([vision_config.MAX_WORKER], dtype=object)
        self.worker_CHANNEL = np.empty([vision_config.MAX_WORKER], dtype=object)
        self.worker_KEY = np.empty([vision_config.MAX_WORKER], dtype=object)
        self.worker_STATUS = np.zeros([vision_config.MAX_WORKER], dtype=int)

        self.client_CHANNEL = np.empty([vision_config.MAX_CLIENT], dtype=object)
        self.client_KEY = np.empty([vision_config.MAX_CLIENT], dtype=object)

        self.sid = vision_config.SERVICE_TOKEN
        self.register_client = vision_config.SERVICE_REGISTER_CLIENT
        self.register_worker = vision_config.SERVICE_REGISTER_WORKER

        logging.info('Server TOKEN: {}'.format(self.sid))
        logging.info('Max client: {}'.format(vision_config.MAX_CLIENT))
        logging.info('Max worker: {}'.format(vision_config.MAX_WORKER))
        for i in range(vision_config.MAX_WORKER):
            self.worker_IN[i] = self.sid + '-IN-' + str(i)
            self.worker_OUT[i] = self.sid + '-OUT-' + str(i)
            self.worker_CHANNEL[i] = self.sid + '-CHANNEL-WORKER-' + str(i)
            self.worker_KEY[i] = None
            self.worker_STATUS[i] = vision_config.WORKER_OFFLINE
            self.r.delete(self.worker_IN[i])
            self.r.delete(self.worker_OUT[i])
            logging.info('WORKER:: {} :: {} :: {}'.format(self.worker_IN[i], self.worker_OUT[i], self.worker_CHANNEL[i]))

        for i in range(vision_config.MAX_CLIENT):
            self.client_CHANNEL[i] = self.sid + '-CHANNEL-CLIENT-' + str(i)
            self.client_KEY[i] = None

            logging.info('CLIENT:: {}'.format(self.client_CHANNEL[i]))
        self.r.delete(self.register_client)
        self.r.delete(self.register_worker)


        logging.info('Start register service worker...')
        Thread(target=self.register_service_worker).start()
        # _thread.start_new_thread(self.register_service_worker, ())

        logging.info('Start register service client...')
        Thread(target=self.register_service_client).start()
        # _thread.start_new_thread(self.register_service_client, ())

        logging.info('Start guard timeout service...')
        Thread(target=self.guard_timeout_channel).start()
        # _thread.start_new_thread(self.guard_timeout_channel, ())

    def register_service_client(self):
        try:
            while self.RUNNING:
                cid = self.r.rpop(self.register_client)
                if cid is not None:
                    worker = np.where(self.worker_STATUS == vision_config.WORKER_ONLINE)[0]
                    if len(worker) == 0:
                        self.r.set(cid, 'NONE')
                        logging.info('CLIENT:: {} register failed!'.format(cid))
                    else:
                        idx = worker[0]
                        self.r.set(cid, "{} {} {}".format(self.worker_IN[idx], self.worker_OUT[idx], self.client_CHANNEL[idx]))
                        SUBS = True
                        time_tmp = time.time()
                        while True:
                            num = self.r.execute_command('PUBSUB', 'NUMSUB', self.client_CHANNEL[idx])[1]
                            if num != 0:
                                break
                            if time.time() - time_tmp > 10.:
                                logging.info(
                                    'WORKER:: {} register failed! (Out of time: MAX_TIME_CLIENT_REGISTER)'.format(cid))
                                SUBS = False
                                break
                            time.sleep(0.01)
                        if SUBS:
                            self.worker_STATUS[idx] = vision_config.WORKER_RUNNING
                            self.client_KEY[idx] = cid
                            logging.info('CLIENT:: {} register to worker {}!'.format(cid, idx))
                        else:
                            self.r.delete(cid)
                time.sleep(0.01)
        except Exception as e:
            logging.error(str(e))
            self.RUNNING = False

    def register_service_worker(self):
        try:
            while self.RUNNING:
                wid = self.r.rpop(self.register_worker)
                if wid is not None:
                    worker = np.where(self.worker_KEY == None)[0]
                    if len(worker) == 0:
                        self.r.set(wid, 'NONE')
                        logging.info('WORKER:: {} register failed!'.format(wid))
                    else:
                        idx = worker[0]
                        self.r.set(wid, "{} {} {}".format(self.worker_IN[idx], self.worker_OUT[idx], self.worker_CHANNEL[idx]))
                        SUBS = True
                        time_tmp = time.time()
                        while True:
                            num = self.r.execute_command('PUBSUB', 'NUMSUB', self.worker_CHANNEL[idx])[1]
                            if num != 0:
                                break
                            if time.time()-time_tmp > 10.:
                                logging.info('WORKER:: {} register failed! (Out of time: MAX_TIME_WORKER_REGISTER)'.format(wid))
                                SUBS = False
                                break
                            time.sleep(0.01)
                        if SUBS:
                            self.worker_STATUS[idx] = vision_config.WORKER_ONLINE
                            self.worker_KEY[idx] = wid
                            logging.info('WORKER:: {} registered to worker {}!'.format(wid, idx))
                        else:
                            self.r.delete(wid)
                time.sleep(0.01)
        except Exception as e:
            logging.error(str(e))
            self.RUNNING = False

    def guard_timeout_channel(self, timecheck=0.1):
        while self.RUNNING:
            for idx in range(vision_config.MAX_WORKER):
                if self.worker_KEY[idx] is not None:
                    num = self.r.execute_command('PUBSUB', 'NUMSUB', self.worker_CHANNEL[idx])[1]
                    if num == 0:
                        logging.info('WORKER:: {} - worker {} diconnected!'.format(self.worker_KEY[idx], idx))
                        self.disconnet_channel_worker(idx)
                        if self.client_KEY[idx] is not None:
                            logging.info('CLIENT:: {} diconnected with worker {}'.format(self.client_KEY[idx], idx))
                            self.disconnet_channel_client(idx)

            for idx in range(vision_config.MAX_CLIENT):
                if self.client_KEY[idx] is not None:
                    num = self.r.execute_command('PUBSUB', 'NUMSUB', self.client_CHANNEL[idx])[1]
                    if num == 0:
                        logging.info('CLIENT:: {} - diconnected with worker {}'.format(self.client_KEY[idx], idx))
                        self.disconnet_channel_client(idx)
            time.sleep(timecheck)

    def disconnet_channel_client(self, idx):
        self.client_KEY[idx] = None
        if self.worker_STATUS[idx] == vision_config.WORKER_RUNNING:
            self.worker_STATUS[idx] = vision_config.WORKER_ONLINE

    def disconnet_channel_worker(self, idx):
        self.worker_KEY[idx] = None
        self.worker_STATUS[idx] = vision_config.WORKER_OFFLINE