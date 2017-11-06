import vcr

# Set to True to enable 'once' mock recording
MOCK_RECORDING_ENABLED = False


vcr = vcr.VCR(
    cassette_library_dir='tests/mock/',
    record_mode='once' if MOCK_RECORDING_ENABLED else 'none',
    match_on=['uri'],
)
