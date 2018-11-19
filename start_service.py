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
parser.add_argument("-camid", help="-camid : set camera for client service", dest="camid", action="store")
parser.set_defaults(camid=None)
parser.add_argument("-port", help="-port : set port streaming client service", dest="port", action="store")
parser.set_defaults(port=8888)
parser.add_argument("-graphic", help="-graphic : set graphic client service", dest="graphic", action="store_true")
parser.set_defaults(graphic=False)

def main(args):
    if args.master and args.detect:
        raise TypeError()
    if args.master and args.iden:
        raise TypeError()
    if args.detect and args.iden:
        raise TypeError()
    if args.master and args.client:
        raise TypeError()
    if args.detect and args.client:
        raise TypeError()
    if args.iden and args.client:
        raise TypeError()
    if args.master:
        if args.detect or args.client:
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
        if args.graphic:
            client.start(args.camid, port=args.port, show_graphhics=True)
        else:
            client.start(args.camid, port=args.port, show_graphhics=False)
if __name__ == '__main__':
    main(parser.parse_args())
