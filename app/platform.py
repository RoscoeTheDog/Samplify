import platform
import getpass
import app.environment

# This script checks the platform the program is running on

if platform.system() == 'Windows':
    app.environment.platform = 'Windows'

elif platform.system() == 'Linux':
    app.environment.platform = 'Linux'

elif platform.system() == 'Java':
    app.environment.platform = 'Java'

else:
    app.environment.platform = 'unknown'

app.environment.user_name = getpass.getuser()
