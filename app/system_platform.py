import platform
import getpass
import app.settings as settings

if platform.system() == 'Windows':
    settings.platform = 'Windows'

elif platform.system() == 'Linux':
    settings.platform = 'Linux'

elif platform.system() == 'Java':
    settings.platform = 'Java'

else:
    settings.platform = 'unknown'

settings.user_name = getpass.getuser()