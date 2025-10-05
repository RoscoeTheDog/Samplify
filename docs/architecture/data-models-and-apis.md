# Data Models and APIs

### Data Models

**Primary Models** (see `database/database_setup.py`):

- **Files** (line 93): Universal file registry with video/audio/image metadata
  - Stores: path, name, extension, creation date
  - Video fields: width, height, duration, frame_rate, pix_format
  - Audio fields: sample_rate, bit_depth, sample_fmt, bit_rate, channels, channel_layout
  - Image fields: format, frames, width, height, alpha, mode

- **FilesVideo/FilesAudio/FilesImage** (lines 124, 153, 172): Type-specific file tables (redundant with Files)

- **OutputDirectories** (line 44): Processing rules per output folder
  - Conversion settings: extensions, sample rates, bit depths, channels
  - Processing flags: normalize, strip_silence, video_only, audio_only, image_only

- **InputDirectories** (line 195): Watched directories with monitoring flag

- **SearchTerms** (line 85): Keyword filters linked to folders

**⚠️ Technical Debt**: Denormalized schema with redundant tables (Files vs. FilesVideo/Audio/Image)

### API Specifications

**No API exists** - this is a CLI script. XML templates act as configuration:

**XML Template Structure**:
```xml
<samplify>
    <name>templateName</name>
    <libraries>
        <directory path="C:\input\path"/>
    </libraries>
    <outputDirectories>
        <directory path="C:\output\kick">
            <rules>
                <expression>Kick</expression>
                <extensions>.wav</extensions>
                <containsAudio>true</containsAudio>
                <audioFormat>default</audioFormat>
                <audioSampleRate>44100</audioSampleRate>
                <audioNormalize>True</audioNormalize>
            </rules>
            <governor>
                <comparison>AND</comparison>  <!-- or OR -->
            </governor>
        </directory>
    </outputDirectories>
</samplify>
```
