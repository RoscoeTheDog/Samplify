import mimetypes
import os


def decode_directory(path):
    # check if path is a valid directory
    try:
        os.chdir(path)

        if os.path.isdir(path):
            # log current working directory

            if os.path.isdir(path):

                # iterate through and decode files
                for root, directory, files in os.walk(path):

                    for f in files:
                        # merge our strings
                        path = os.path.join(root, f)

                        m_types = mimetypes.guess_type(path)

                        t, e = m_types

                        if t is not None:
                            print("file: ", path, "\n",
                                  "type: ", t.split('/')[0], "\n",
                                  "encoding: ", e)

    except Exception as e:
        print(e)


decode_directory("D:\\MOVIES & SHOWS")
