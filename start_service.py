import argparse

parser = argparse.ArgumentParser(description="")
parser.add_argument("-master", help="-master : start service_master", dest="master", action="store_true")
parser.set_defaults(master=False)
parser.add_argument("-detect", help="-run : start detect_service", dest="detect", action="store_true")
parser.set_defaults(detect=False)
parser.add_argument("-iden", help="-run : start identify_service", dest="iden", action="store_true")
parser.set_defaults(iden=False)
parser.add_argument("-client", help="-run : start client_service", dest="client", action="store_true")
parser.set_defaults(client=False)

def main(args):
    if args.master:
        import service_master
        service_master.FaceDetectionService()
    if args.detect:
        import service_detect_worker
        worker = service_detect_worker.FaceDetectionWorker()
        worker.register_work_service()
        worker.run_service()
    if args.iden:
        import service_identify
        service_identify.FaceIdentifyService().run()
    if args.client:
        import client
        client.start()
if __name__ == '__main__':
    main(parser.parse_args())