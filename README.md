# Samplify 

Samplify is a tool aimed to help content creators organize their media libraries in an easily structured and customizable way through use of templated models. Users can choose to process different types of media to various output locations by tagging folders with keywords, reg-ex patterns, or media metadata attributes. Samplify monitors specified folders for changes and will process them according to your configurations. FFmpeg is used for most audio/video processing but the PIL library is used for image processing. 

Samplify is written in Python and has a fair amount of package dependencies. More information on setup and installation of these will be coming soon.

Samplify supports multi-threaded processing and uses various frameworks for media conversion such as FFmpeg and Pill. Because of this, it has a wide veriety of file support and encoding/decoding options.

**Some features include:**

-Real-time input file detection.

-Independant customization for input and output directory models.

-Multi-processing support.

-GPU-Acceleration (If codec available for filetype).

-Regular Expression pattern matching for filenames and/or types.

-Wide file support through FFMpeg and other frameworks.

-End-User graphical interface (eventually).

**THIS IS A WORK IN PROGRESS**

Development is currently being performed in a windows enviroment. Although project dependencies are supported on other operating systems, I have not yet tested any code on them but the frameworks chosen do support both UNIX and macOS platforms as well. Eventually I will test on those platforms if and when I get down to it
