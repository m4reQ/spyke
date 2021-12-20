class Capabilities:
    __slots__ = (
        '__weakref__',
        'nv_command_list_enabled',
        'arb_bindless_texture_enabled',
        'arb_texture_compression_enabled',
        'intel_framebuffer_cmaa_enabled'
    )

    def __init__(self):
        self.nv_command_list_enabled = False
        self.arb_bindless_texture_enabled = False
        self.arb_texture_compression_enabled = False
        self.intel_framebuffer_cmaa_enabled = False