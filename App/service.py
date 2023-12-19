# from time import sleep

# from jnius import autoclass

# PythonService = autoclass('org.kivy.android.PythonService')
# PythonService.mService.setAutoRestartService(True)


# while True:
#     print("service running.....")
#     sleep(5)


from jnius import autoclass
SERVICE_NAME = u'{packagename}.Service{servicename}'.format(
    packagename=u'org.kivy.test',
    servicename=u'Myservice'
)
service = autoclass(SERVICE_NAME)
mActivity = autoclass(u'org.kivy.android.PythonActivity').mActivity
argument = ''
service.start(mActivity, argument)