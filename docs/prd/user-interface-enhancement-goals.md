# User Interface Enhancement Goals

### Integration with Existing UI

**Current State**: Samplify has NO existing UI - it's a CLI-only application with XML-based configuration.

**New UI Integration Approach**:
- Django-based web interface served on `localhost` (default port 8000)
- Browser-accessible UI replacing all XML template editing
- Self-contained local web server (no remote access, no cloud integration)
- Progressive enhancement: functional HTML with JavaScript enhancements
- Minimal design aesthetic (proof-of-concept focus)

### Single-Page Schema Designer (Final Design)

**Layout: Option 1 - Horizontal Split with Dual Queue Visualization**

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────┐
│  [🔄 File Monitor: ●ON ] [⚙️ Queue Processor: ●ON ]                                                 │
├─────────────────────────────────────────────────────────────────────────────────────────────────────┤
│  Schema: "Audio Processing Template" [Save] [Load] [Delete]                                         │
├─────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                       │
│  INPUT DIRECTORIES                              OUTPUT DIRECTORIES                                   │
│  ┌───────────────────────────┐                 ┌───────────────────────────┐                       │
│  │ [+ Add Folder]            │                 │ [+ Add Folder]            │                       │
│  ├───────────────────────────┤                 ├───────────────────────────┤                       │
│  │ ☑ C:\Input\Samples        │                 │ ☑ C:\Output\Drums         │                       │
│  │ ☐ C:\Input\Loops          │                 │ ☐ C:\Output\Bass          │                       │
│  │ ☐ C:\Input\FX             │                 │ ☐ C:\Output\Vocals        │                       │
│  └───────────────────────────┘                 └───────────────────────────┘                       │
│                                                                                                       │
│  SELECTED FOLDER PROPERTIES                                                                          │
│  ┌──────────────────────────────────────────────────────────────────────────────────────────────┐   │
│  │ Input: C:\Input\Samples                                                                       │   │
│  │ ┌──────────────────────────┐  ┌─────────────────────────────────────────────────────────────┐│   │
│  │ │ FILTERS                  │  │ PROCESSING RULES                                            ││   │
│  │ │ [+ Add Filter]           │  │ [+ Add Rule]                                                ││   │
│  │ │ • Keywords: kick         │  │ • Format: WAV                                               ││   │
│  │ │ • Extension: .wav        │  │ • Sample Rate: 44100                                        ││   │
│  │ │ • Contains: Audio        │  │ • Bit Depth: 24                                             ││   │
│  │ │                          │  │ • Normalize: -6dB                                           ││   │
│  │ └──────────────────────────┘  └─────────────────────────────────────────────────────────────┘│   │
│  │ Logic: [AND ▼] [OR]                                                                           │   │
│  └──────────────────────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                                       │
│  [Scan Input] [Preview Transformations] [Start Batch Process]                                       │
│                                                                                                       │
│  PROCESSING QUEUE (245 files)                                                                        │
│  ┌──────────────────────────────────────────────────────────────────────────────────────────────┐   │
│  │ INPUT FILES                                                                                   │   │
│  ├───┬────────┬─────────────────────────┬──────────────────┬────────┬────────┬───────┬─────────┤   │
│  │ ☑ │ UID    │ Filename                │ Path             │ Format │ SR     │ BD    │ Size    │   │
│  ├───┼────────┼─────────────────────────┼──────────────────┼────────┼────────┼───────┼─────────┤   │
│  │ ☑ │ #a1f2  │ kick_01.wav             │ C:\Input\Samples │ WAV    │ 44100  │ 16    │ 1.2 MB  │   │
│  │ ☑ │ #b3e4  │ kick_02.wav             │ C:\Input\Samples │ WAV    │ 44100  │ 24    │ 2.1 MB  │   │
│  │ ☑ │ #c5d6  │ snare_01.wav            │ C:\Input\Samples │ WAV    │ 48000  │ 16    │ 890 KB  │   │
│  └───┴────────┴─────────────────────────┴──────────────────┴────────┴────────┴───────┴─────────┘   │
│                                                                                                       │
│  ┌──────────────────────────────────────────────────────────────────────────────────────────────┐   │
│  │ OUTPUT DESTINATIONS        Filter by UID: [#a1f2, #b3e4, #c5d6                           ✕]  │   │
│  ├───┬────────┬─────────────────────────┬──────────────────┬────────┬────────┬───────┬─────────┤   │
│  │ ☑ │ UID    │ Filename                │ Destination      │ Format │ SR     │ BD    │ Process │   │
│  ├───┼────────┼─────────────────────────┼──────────────────┼────────┼────────┼───────┼─────────┤   │
│  │ ☑ │ #a1f2  │ kick_01.wav             │ C:\Output\Drums  │ WAV    │ 44100  │ 24    │ Norm-6dB│   │
│  │ ☑ │ #b3e4  │ kick_02.wav             │ C:\Output\Drums  │ WAV    │ 44100  │ 24    │ Norm-6dB│   │
│  │ ☑ │ #c5d6  │ snare_01.wav            │ C:\Output\Drums  │ WAV    │ 44100  │ 24    │ Resample│   │
│  └───┴────────┴─────────────────────────┴──────────────────┴────────┴────────┴───────┴─────────┘   │
│                                                                                                       │
│  ☑ Select All  [▲ Deselect Skipped]              [Clear Queue] [Export Preview]                     │
└─────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

**Key UI Features:**

1. **Dual Watchdog Controls** (top bar):
   - File Monitor toggle (filesystem watchdog)
   - Queue Processor toggle (processing watchdog)
   - Status indicators: ●ON (green) / ●OFF (red)

2. **Input/Output Directory Tables**:
   - Folder selection with checkboxes
   - Add/remove directories via file browser dialog

3. **Properties Panel**:
   - Filters (keywords, extensions, media type)
   - Processing rules (format, sample rate, bit depth, normalize)
   - AND/OR logic selector

4. **Dual Queue Visualization**:
   - **Input Queue**: Shows files with UID, metadata columns
   - **Output Queue**: Shows destinations with processing details
   - **UID Filtering**: Comma-delimited search (#a1f2, #b3e4)
   - Click input file → auto-filters output queue
   - Clear button (✕) shows all files

5. **Interaction Flow**:
   - Scan Input → Populates queue
   - Click input file → Filters output by UID
   - Multi-select (Ctrl+Click) → Multiple UIDs in filter
   - Preview Transformations → Shows queue
   - Start Batch Process → Executes checked items

---
